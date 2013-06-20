#!/usr/bin/env python
#coding: utf-8
#file   : deploy.py
#author : ning
#date   : 2012-08-24 06:26:25


import urllib, urllib2, httplib, os, re, sys, time, logging, hmac, base64, commands, glob
import json
import argparse
import config
import socket
import pymongo, bson
import threading
import calendar
from common import *

def _system(cmd):
    info(cmd)
    return system(cmd)
    
class StatusChecker():
    '''
    
    '''
    pass

class OplogReplayer(threading.Thread):
    def __init__(self, src, args):
        threading.Thread.__init__(self)
        self.name = src
        self.src = src
        self.args = args

    def run(self):
        info("Starting " + self.name)
        _getoplog(self.src, args)

def _getoplog(src, args):
    src_conn = pymongo.Connection(src)
    dest_conn = pymongo.Connection(args.to)

    rename = {}     # maps old namespace (regex) to the new namespace (string)
    for rename_pair in args.rename:
        old_ns, new_ns = rename_pair.split("=")
        old_ns_re = re.compile(r"^{0}(\.|$)".format(re.escape(old_ns)))
        rename[old_ns_re] = new_ns + "."

    # Find out where to start from
    start = bson.timestamp.Timestamp(args.start, 0)
    start = read_ts(args.resume_file) or day_ago

    info("starting from %s" % start)
    q = {"ts": {"$gte": start}}

    count = src_conn.local['oplog.rs'].find(q, tailable=True, await_data=True, timeout=False).count()
    print count

    oplog = (src_conn.local['oplog.rs'].find(q, tailable=True, await_data=True, timeout=False)
                                  .sort("$natural", pymongo.ASCENDING))

    num = 0
    ts = start

    try:
        while oplog.alive:
            try:
                op = oplog.next()
            except StopIteration:
                info("%s: [num:%d] waiting for new data..." % (src, num))
                time.sleep(1)
                continue
            except bson.errors.InvalidDocument as e:
                info(src + repr(e))
                continue
            #print op

            # Update status
            ts = op['ts']
            #print time.time(), '  ', ts.time
            delay = time.time() - ts.time
            if not num % 1000:
                save_ts(ts, args.resume_file)
                info(src + " %s\t%s\t%s -> %s [delay:%d]" %
                             (num, ts.as_datetime(),
                             op.get('op'),
                             op.get('ns'), delay )
                    )

            num += 1

            # Skip excluded namespaces or namespaces that does not match --ns
            excluded = any(op['ns'].startswith(ns) for ns in args.exclude)
            included = any(op['ns'].startswith(ns) for ns in args.ns)

            if excluded or (args.ns and not included):
                debug("skipping ns %s", op['ns'])
                continue

            # Rename namespaces
            for old_ns, new_ns in rename.iteritems():
                if old_ns.match(op['ns']):
                    ns = old_ns.sub(new_ns, op['ns']).rstrip(".")
                    debug("renaming %s to %s", op['ns'], ns)
                    op['ns'] = ns

            # Apply operation
            try:
                apply_op(dest_conn, op)
            except pymongo.errors.OperationFailure as e:
                warning(repr(e))
                raise

    except KeyboardInterrupt:
        debug("Got Ctrl+C, exiting...")

    finally:
        save_ts(ts, args.resume_file)

#not work on mongos
def apply_op(dest_conn, op):
    dbname = op['ns'].split('.')[0] or "admin"
    dest_conn[dbname].command("applyOps", [op])

def apply_op(dest_conn, raw):
    def _dest_coll(ns):
        db, collection = ns.split('.', 1)
        return dest_conn[db][collection]

    ns = raw['ns']
    op = raw['op']

    if op == 'i':
        try:
            _dest_coll(ns).insert(raw['o'], safe=True)
        except pymongo.errors.DuplicateKeyError, e:
            warning(str(e))
    elif op == 'u':
        _dest_coll(ns).update(raw['o2'], raw['o'], safe=True)
    elif op == 'd':
        _dest_coll(ns).remove(raw['o'], safe=True)
    #elif op == 'c':
        #command(ns=ns, raw=raw)
    #elif op == 'db':
        #db_declare(ns=ns, raw=raw)
    elif op == 'n':
        print 'noop'
        pass
    else:
        error("Unknown op: %r" % raw)

    #TODO: add/drop index


def save_ts(ts, filename):
    """Save last processed timestamp to file. """
    try:
        if filename and filename.lower() != 'none':
            with open(filename, 'w') as f:
                obj = {"ts": {"time": ts.time, "inc":  ts.inc}}
                json.dump(obj, f)
    except IOError:
        return False
    else:
        return True

def read_ts(filename):
    """Read last processed timestamp from file. Return next timestamp that
    need to be processed, that is timestamp right after last processed one.
    """
    try:
        with open(filename, 'r') as f:
            data = json.load(f)['ts']
            ts = bson.Timestamp(data['time'], data['inc'] + 1)
            return ts

    except (IOError, KeyError):
        return None

def main(args):
    conn = pymongo.Connection(args.fromhost)
    db = conn['config']
    shards = list(db.shards.find())
    info( 'shards' + str(shards))
    for s in shards:
        (setname, hosts) = s['host'].split('/')
        set_conn = pymongo.ReplicaSetConnection(hosts, replicaSet=setname)
        primary = '%s:%d' % set_conn.primary
        info("primary: " + primary)
        OplogReplayer(primary, args).start()

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--from", metavar="host[:port]", dest="fromhost",
                        required = True,
                        help="host to pull from")

    parser.add_argument("--to", metavar="host[:port]",
                        required = True,
                        help="mongo host to push to (<set name>/s1,s2 for sets)")

    parser.add_argument("--start", type=int, default=0,
                        help="""seconds to start from. if resume-file exist, will use resume-file
                        default : 0""")

    parser.add_argument("--ns", nargs="*", default=[],
                        help="this namespace(s) only ('dbname' or 'dbname.coll')")

    parser.add_argument("-x", "--exclude", nargs="*", default=[],
                        help="exclude namespaces ('dbname' or 'dbname.coll')")

    parser.add_argument("--rename", nargs="*", default=[],
                        metavar="ns_old=ns_new",
                        help="rename namespaces before processing on dest")

    parser.add_argument("--resume-file", default="mongomigrate.ts",
                        metavar="FILENAME",
                        help="""resume from timestamp read from this file and
                             write last processed timestamp back to this file
                             (default is %(default)s).
                             Pass empty string or 'none' to disable this
                             feature.
                             """)

    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    print args
    main(args)

