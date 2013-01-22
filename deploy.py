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
    info(cmd)
    return system(cmd)

def _init():
    _system('rm -rf ./mongodb-base')
    _system('cp -rf %s ./mongodb-base' % config.MONGO_DB_PATH)
    _system('mkdir -p ./mongodb-base/conf')
    _system('mkdir -p ./mongodb-base/log')
    _system('mkdir -p ./mongodb-base/db')
    _system('cp mongod.conf ./mongodb-base/conf')

def _alive(host, port):
    cmd = 'mongostat --host %s --port %s -n1' % (host, port)
    r = _system(cmd)
    if r.find('insert') >= 0:
        return True
    return False
    
def mongod_start(host, port, path, replset_name):

    if _alive(host, port):
        print 'already alive:  we do nothing!'
        return 

    cmd = 'ssh -n -f %s@%s "mkdir -p %s "' % (config.USER, host, path)
    _system(cmd)

    cmd = 'rsync -avP ./mongodb-base/ %s@%s:%s 1>/dev/null 2>/dev/null' % (config.USER, host, path)
    _system(cmd)

    cmd = 'ssh -n -f %s@%s "cd %s ; ./bin/mongod -f ./conf/mongod.conf --port %d --replSet %s --fork "' % (config.USER, host, path, port, replset_name)
    print _system(cmd)

def mongod_clean(host, path):
    cmd = 'ssh %s@%s "rm -rf %s "' % (config.USER, host, path)
    print _system(cmd)


################################### op
def replset_ps(replset):
    for host, port, path in  replset['mongod']:
        cmd = 'ssh -n -f %s@%s "pgrep -l -f \'./bin/mongod -f ./conf/mongod.conf --port %d \'"' % (config.USER, host, port)
        print _system(cmd)

def replset_log(replset):
    for host, port, path in  replset['mongod']:
        cmd = 'ssh -n -f %s@%s "cd %s ; tail -20 log/mongod.log"' % (config.USER, host, path)
        print _system(cmd)

def replset_kill(replset):
    for host, port, path in  replset['mongod']:
        cmd = 'ssh -n -f %s@%s "pkill -9 -f \'./bin/mongod -f ./conf/mongod.conf --port %d \'"' % (config.USER, host, port)
        print _system(cmd)

def replset_stop(replset):
    for host, port, path in  replset['mongod']:
        cmd = 'ssh -n -f %s@%s "cd %s ; ./bin/mongod -f ./conf/mongod.conf --port %d --shutdown"' % (config.USER, host, path, port)
        print _system(cmd)

def replset_clean(replset):
    for host, port, path in  replset['mongod']:
        mongod_clean(host, path)

tmpfile= TmpFile()

def run_js(host, port, js):
    print 'run_js: \n', js
    filename = tmpfile.content_to_tmpfile(js)

    cmd = './mongodb-base/bin/mongo %s:%d/admin %s' % (host, port, filename)
    rst = _system(cmd)
    if rst.find('command failed') >=0:
        raise Exception('run js error: \n' + rst)
    print rst


def replset_start(replset):
    for host, port, path in  replset['mongod']:
        mongod_start(host, port, path, replset['replset_name'])
    time.sleep(5)
    members = [{'_id': id, 'host': '%s:%d'%(host,port) } for (id, (host, port, path)) in enumerate(replset['mongod'])]
    replset_config = {
        '_id': replset['replset_name'],
        'members': members
    }
    js = '''
config = %s;
rs.initiate(config);
''' % json.dumps(replset_config)

    
    primary = replset['mongod'][0]
    ip = socket.gethostbyname(primary[0])
    port = primary[1]
    run_js(ip, port, js)

    print_green( 'see http://%s:%d/_replSet' % (primary[0], 1000+primary[1]) )

def mongos_start(mongos, configdb):
    [host, port, path] = mongos

    if _alive(host, port):
        print 'already alive:  we do nothing!'
        return 

    cmd = 'ssh -n -f %s@%s "mkdir -p %s "' % (config.USER, host, path)
    _system(cmd)

    cmd = 'rsync -avP ./mongodb-base/ %s@%s:%s 1>/dev/null 2>/dev/null' % (config.USER, host, path)
    _system(cmd)

    cmd = 'ssh -n -f %s@%s "cd %s ; ./bin/mongos --configdb %s --logpath ./log/mongod.log --port %d --fork "' % (config.USER, host, path, configdb, port)
    print _system(cmd)


def mongos_kill(mongos, configdb):
    [host, port, path] = mongos

    cmd = '''ssh -n -f %s@%s "pkill -f  './bin/mongos --configdb %s --logpath ./log/mongod.log --port %d --fork' "''' % (config.USER, host, configdb, port)
    print _system(cmd)

def mongos_ps(mongos, configdb):
    [host, port, path] = mongos

    cmd = '''ssh -n -f %s@%s "pgrep -l -f  './bin/mongos --configdb %s --logpath ./log/mongod.log --port %d --fork' "''' % (config.USER, host, configdb, port)
    print _system(cmd)

def configserver_start(configserver):
    [host, port, path] = configserver

    if _alive(host, port):
        print 'already alive:  we do nothing!'
        return 

    cmd = 'ssh -n -f %s@%s "mkdir -p %s "' % (config.USER, host, path)
    _system(cmd)

    cmd = 'rsync -avP ./mongodb-base/ %s@%s:%s 1>/dev/null 2>/dev/null' % (config.USER, host, path)
    _system(cmd)

    cmd = 'ssh -n -f %s@%s "cd %s ; ./bin/mongod --configsvr --dbpath ./db --logpath ./log/mongod.log --port %d --fork "' % (config.USER, host, path, port)
    print _system(cmd)


def configserver_kill(configserver):
    [host, port, path] = configserver

    cmd = '''ssh -n -f %s@%s "pkill -f './bin/mongod --configsvr --dbpath ./db --logpath ./log/mongod.log --port %d --fork' "''' % (config.USER, host, port)
    print _system(cmd)

def configserver_ps(configserver):
    [host, port, path] = configserver

    cmd = '''ssh -n -f %s@%s "pgrep -l -f './bin/mongod --configsvr --dbpath ./db --logpath ./log/mongod.log --port %d --fork' "''' % (config.USER, host, port)
    print _system(cmd)

def sharding_status(sharding):
    [ip, port, path] = sharding['mongos'][0]
    run_js(ip, port, 'sh.status()')

def sharding_start(sharding):
    configdb = ['%s:%d' % (i[0], i[1]) for i in sharding['configserver']]
    configdb = ','.join(configdb)

    for shard in sharding['shard']:
        replset_start(shard)

    for configserver in sharding['configserver']:
        configserver_start(configserver)

    for mongos in sharding['mongos']:
        mongos_start(mongos, configdb)

    @retry(Exception, tries=2)
    def add_shard(shard):
        members = ['%s:%d'%(host,port) for (id, (host, port, path)) in enumerate(shard['mongod'])]
        members = ','.join(members)
        js =''' 
        //use admin;
        sh.addShard( "%s/%s" );
        ''' % (shard['replset_name'], members)

        [ip, port, path] = sharding['mongos'][0]
        try: 
            run_js(ip, port, js)
        except Exception as e: 
            if str(e).find('E11000 duplicate key error index: config.shards.$_id_') >= 0:
                print 'shard already added !!!'
                return 
            raise e

    for shard in sharding['shard']:
        add_shard(shard)
    sharding_status(sharding)


def sharding_ps(sharding):
    configdb = ['%s:%d' % (i[0], i[1]) for i in sharding['configserver']]
    configdb = ','.join(configdb)

    for shard in sharding['shard']:
        replset_ps(shard)

    for mongos in sharding['mongos']:
        mongos_ps(mongos, configdb)

    for configserver in sharding['configserver']:
        configserver_ps(configserver)
    sharding_status(sharding)

def sharding_kill(sharding):
    for shard in sharding['shard']:
        replset_kill(shard)

    configdb = ['%s:%d' % (i[0], i[1]) for i in sharding['configserver']]
    configdb = ','.join(configdb)

    for mongos in sharding['mongos']:
        mongos_kill(mongos, configdb)

    for configserver in sharding['configserver']:
        configserver_kill(configserver)

mongos_clean = mongod_clean
configserver_clean = mongod_clean

def sharding_clean(sharding):
    for shard in sharding['shard']:
        replset_clean(shard)

    for host, port, path in sharding['mongos']:
        mongos_clean(host, path)
    for host, port, path in sharding['configserver']:
        configserver_clean(host, path)

def discover_op():
    sets =  globals().keys()
    sets = [s.replace('replset_', '') for s in sets if s.startswith('replset_')]
    return sets

def discover_cluster():
    sets = [s for s in dir(config) if s.startswith('cluster')]
    return sets

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('op', choices=discover_op(), 
        help='start/stop/clean mongodb replset cluster')

    parser.add_argument('target', choices=discover_cluster(), help='replset target ')
    args = parser.parse_args()

    _init()
    cluster = eval('config.%s' % args.target)
    
    #print args
    eval('%s_%s(config.%s)' % (cluster['type'], args.op, args.target))

if __name__ == "__main__":
    parse_args()

