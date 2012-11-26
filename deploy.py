#!/usr/bin/env python
#coding: utf-8
#file   : deploy.py
#author : ning
#date   : 2012-08-24 06:26:25


import urllib, urllib2, httplib, os, re, sys, time, logging, hmac, base64, commands, glob
import json
from common import *
import argparse
import config
import socket

def _system(cmd):
    print_green('[info] ' + cmd)
    return system(cmd)

def _init():
    _system('rm -rf ./mongodb-base')
    _system('cp -rf %s ./mongodb-base' % config.MONGO_DB_PATH)
    _system('mkdir -p ./mongodb-base/conf')
    _system('mkdir -p ./mongodb-base/log')
    _system('mkdir -p ./mongodb-base/db')
    _system('cp mongod.conf ./mongodb-base/conf')

    
def _deploy_single(host, port, path):

    cmd = 'ssh -n -f %s@%s "mkdir -p %s "' % (config.USER, host, path)
    _system(cmd)

    cmd = 'rsync -avP ./mongodb-base/ %s@%s:%s 1>/dev/null 2>/dev/null' % (config.USER, host, path)
    _system(cmd)

    cmd = 'ssh -n -f %s@%s "cd %s ; ./bin/mongod -f ./conf/mongod.conf --port %d --fork "' % (config.USER, host, path, port)
    print _system(cmd)

################################### op
def replset_ps(replset):
    for host, port, path in  replset['host']:
        cmd = 'ssh -n -f %s@%s "ps aux | grep mongo"' % (config.USER, host)
        print _system(cmd)

def replset_log(replset):
    for host, port, path in  replset['host']:
        cmd = 'ssh -n -f %s@%s "cd %s ; tail -20 log/mongod.log"' % (config.USER, host, path)
        print _system(cmd)

def replset_stop(replset):
    for host, port, path in  replset['host']:
        cmd = 'ssh -n -f %s@%s "cd %s ; ./bin/mongod -f ./conf/mongod.conf --port %d --shutdown"' % (config.USER, host, path, port)
        print _system(cmd)

def replset_clean(replset):
    for host, port, path in  replset['host']:
        cmd = 'ssh %s@%s "rm -rf %s "' % (config.USER, host, path)
        print _system(cmd)

def replset_start(replset):
    for host, port, path in  replset['host']:
        _deploy_single(host, port, path)
    time.sleep(5)
    members = [{'_id': id, 'host': '%s:%d'%(host,port) } for (id, (host, port, path)) in enumerate(replset['host'])]
    replset_config = {
        '_id': 'cluster0',
        'members': members
    }
    js = '''
config = %s;
rs.initiate(config);
''' % json.dumps(replset_config)

    f = file('tmp.js', 'w')
    f.write(js)
    f.close()
    print 'tmp.js: ', js
    
    primary = replset['host'][0]
    ip = socket.gethostbyname(primary[0])
    port = primary[1]
    cmd = './mongodb-base/bin/mongo %s:%d %s' % (ip, port, 'tmp.js')
    print _system(cmd)
    print_green( 'see http://%s:%d/_replSet' % (primary[0], 1000+primary[1]) )


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('op', choices=['start', 'stop', 'clean', 'ps', 'log'], 
        help='start/stop/clean mongodb replset cluster')
    sets = [s for s in dir(config) if s.startswith('cluster')]
    parser.add_argument('target', choices=sets , help='replset target ')
    args = parser.parse_args()

    _init()
    cluster = eval('config.%s' % args.target)
    
    #print args
    eval('%s_%s(config.%s)' % (cluster['type'], args.op, args.target))

if __name__ == "__main__":
    parse_args()

