#!/usr/bin/env python
#coding: utf-8
#file   : deploy2.py
#author : ning
#date   : 2013-08-30 16:44:12

import urllib, urllib2, httplib, os, re, sys, time, logging, hmac, base64, commands, glob
  

import urllib, urllib2, httplib, os, re, sys, time, logging, hmac, base64, commands, glob
import json
import argparse
import socket

from pcl import common

PWD = os.path.dirname(os.path.realpath(__file__))
WORKDIR = os.path.join(PWD,  '../')
LOGPATH = os.path.join(WORKDIR, 'log/deploy.log')

sys.path.append(os.path.join(WORKDIR, 'lib/'))
sys.path.append(os.path.join(WORKDIR, 'conf/'))

import deploy_conf as conf

class TmpFile:
    def __init__(self, tmp_dir = './tmp/'):
        self.tmp_dir = tmp_dir

        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir, mode=0777) 
            os.chmod(tmp_dir, 0777)

    def random_tmp_file(self, key):
        from datetime import datetime
        name = str(datetime.now())
        name = name.replace(' ', '_')
        name = name.replace(':', '_')
        name = name.replace('.', '_')
        return self.tmp_dir + key + name

    def content_to_tmpfile(self, content):
        tmp_file = self.random_tmp_file('_')
        f = file(tmp_file, 'wb')
        f.write(content)
        f.close()
        return tmp_file

def _remote_run(user, host, raw_cmd):
    if raw_cmd.find('"') >= 0:
        error('bad cmd: ' + raw_cmd)
        return
    cmd = 'ssh -n -f %s@%s "%s"' % (user, host, raw_cmd)
    return common.system(cmd, logging.info)

def _init():
    #common.system('rm -rf ./mongodb-base', logging.debug)

    common.system('mkdir -p ./mongodb-base/bin', logging.debug)
    common.system('mkdir -p ./mongodb-base/conf', logging.debug)
    common.system('mkdir -p ./mongodb-base/log', logging.debug)
    common.system('mkdir -p ./mongodb-base/db', logging.debug)

    common.system('cp -u %s/bin/mongo ./mongodb-base/bin' % conf.MONGO_DB_PATH, logging.debug)
    common.system('cp -u %s/bin/mongostat ./mongodb-base/bin' % conf.MONGO_DB_PATH, logging.debug)
    common.system('cp -u %s/bin/mongod ./mongodb-base/bin' % conf.MONGO_DB_PATH, logging.debug)
    common.system('cp -u %s/bin/mongos ./mongodb-base/bin' % conf.MONGO_DB_PATH, logging.debug)

    common.system('cp conf/mongod.conf ./mongodb-base/conf', logging.debug)

class Base:
    def start(self):
        logging.error("start: not implement")

    def stop(self):
        logging.error("stop : not implement")

    def kill(self):
        logging.error("kill: not implement")

    def ps(self):
        logging.error("ps: not implement")

    def log(self):
        logging.error("log: not implement")

    def clean(self):
        logging.error("clean: not implement")

class Mongod(Base):
    '''
    for mongod, mongos, configserver
    '''
    def __init__(self, host, port, ssh_user, path, auth):
        self.host = host
        self.port = port
        self.ssh_user = ssh_user
        self.path = path
        self.auth = auth

    def _vars(self):
        return {
            'role': type(self),
            'host': self.host,
            'port': self.port,
            'ssh_user': self.ssh_user,
            'path': self.path,
            'user': self.auth['user'],
            'password': self.auth['password'],
            'key': self.auth['key'],
        }
    def __str__(self):
        return '[%(role)s] %(host)s:%(port)s' % self._vars()

    def _alive(self):
        cmd = 'mongostat --host %(host)s --port %(port)s -u __system -p %(key)s -n1 ' % self._vars()
        r = common.system(cmd, logging.debug)
        if r.find('insert') >= 0:
            alive = True
        else:
            alive = False
        logging.info("%s alive = %s" % (self, alive))
        return alive

    def _copy_files(self):
        cmd = 'mkdir -p %s ' % self.path
        _remote_run(self.ssh_user, self.host, cmd)

        cmd = 'rsync -avP ./mongodb-base/ %s@%s:%s 1>/dev/null 2>/dev/null' % (self.ssh_user, self.host, self.path)
        common.system(cmd, logging.debug)

    def _run_js(self, js):
        logging.info('run_js: \n' + js.replace(' ', '').replace('\n', '  '))
        filename = TmpFile().content_to_tmpfile(js)

        cmd = './mongodb-base/bin/mongo %(host)s:%(port)s/admin -u __system -p %(key)s' % self._vars()
        r = common.system(cmd, logging.info)
        if r.find('command failed') >=0 or r.find('uncaught exception') >=0:
            raise Exception('run js error: \n' + r)
        logging.info(r)

    def start(self):
        pass

    def stop(self):
        pass

    def kill(self):
        pass

    def ps(self):
        pass

    def log(self):
        pass

    def clean(self):
        pass

class Mongos(Mongod):
    pass

class Configserver(Mongod):
    pass

class Replset(Base):
    pass

class Sharding(Base):
    pass



def discover_op():
    import inspect
    methods = inspect.getmembers(Base, predicate=inspect.ismethod)
    sets = [m[0] for m in methods]
    return sets

def discover_cluster():
    sets = [s for s in dir(conf) if s.startswith('cluster')]
    return sets

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('op', choices=discover_op(), 
        help='start/stop/clean mongodb/replset/sharding-cluster')

    parser.add_argument('target', choices=discover_cluster(), help='replset target ')
    args = common.parse_args2(LOGPATH, parser)

    _init()

    cluster = eval('conf.%s' % args.target)
    func = eval('%s_%s' % (cluster['type'], args.op) )
    conf.USER = cluster['user']
    func(cluster)
    #eval('%s_%s(conf.%s)' % (, args.target))

if __name__ == "__main__":
    parse_args()

