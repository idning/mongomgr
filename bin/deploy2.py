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
    def __init__(self, args):
        args['role'] = self.__class__.__name__
        args['user'] = args['auth']['user']
        args['password'] = args['auth']['password']
        args['key'] = args['auth']['key']

        self.args = args

        self.args['startcmd'] = './bin/mongod -f ./conf/mongod.conf --port %(port)d --fork --replSet %(replset_name)s --keyFile=%(path)s/conf/mongokey' % self.args
        #self.args['startcmd'] = './bin/mongod -f ./conf/mongod.conf --port %(port)d --fork --keyFile=%(path)s/conf/mongokey' % self.args

    def __str__(self):
        return '[%(role)s] [%(host)s:%(port)s]' % self.args

    def _alive(self):
        cmd = 'mongostat --host %(host)s --port %(port)s -u __system -p %(key)s -n1 ' % self.args
        r = common.system(cmd, logging.debug)
        if r.find('insert') >= 0:
            alive = True
        else:
            alive = False
        logging.info("%s alive = %s" % (self, alive))
        return alive

    def _remote_run(self, raw_cmd):
        if raw_cmd.find('"') >= 0:
            raise Exception('bad cmd: ' + raw_cmd)
        cmd = 'ssh -n -f %s@%s "%s"' % (self.args['ssh_user'], self.args['host'], raw_cmd)
        return common.system(cmd, logging.info)

    def _copy_files(self):

        cmd = 'echo "%(key)s" > ./mongodb-base/conf/mongokey && chmod 700 ./mongodb-base/conf/mongokey' % self.args
        common.system(cmd, logging.debug)

        cmd = 'mkdir -p %(path)s ' % self.args
        self._remote_run(cmd)

        cmd = 'rsync -avP ./mongodb-base/ %(ssh_user)s@%(host)s:%(path)s 1>/dev/null 2>/dev/null' % self.args
        common.system(cmd, logging.debug)

    def _runjs(self, js):
        logging.info('_run_js: \n' + js.replace(' ', '').replace('\n', '  '))
        filename = TmpFile().content_to_tmpfile(js)

        cmd = './mongodb-base/bin/mongo %(host)s:%(port)s/admin -u __system -p %(key)s' % self.args 
        cmd += ' ' + filename
        r = common.system(cmd, logging.info)
        if r.find('command failed') >=0 or r.find('uncaught exception') >=0:
            raise Exception('run js error: \n' + r)

        logging.debug(r)
        return r

    def _adduser(self):
        js = 'db.addUser("%(user)s", "%(password)s");' % self.args
        self._runjs(js)

    def start(self):
        if self._alive():
            logging.info('%s already alive:  we do nothing!' % self)
            return 

        cmd = 'cd %(path)s && numactl --interleave=all %(startcmd)s ' % self.args

        self._copy_files()
        r = self._remote_run(cmd)
        logging.debug(r)
        if r.find('forked process') == -1:
            raise Exception("%s mongod start Fail" % self)
        if not self._alive():
            raise Exception("%s mongod start Fail" % self)
        logging.info("%s start Success" % self)
        #self._adduser() # we should not add user from mongod in replset mode

    def stop(self):
        cmd = 'cd %(path)s ; %(startcmd)s --shutdown' % self.args
        print self._remote_run(cmd)

    def kill(self):
        cmd = 'pkill -9 -f \'%(startcmd)s\'' % self.args
        print self._remote_run(cmd)

    def ps(self):
        cmd = 'pgrep -f \'%(startcmd)s\'' % self.args
        print self._remote_run(cmd)
        pass

    def log(self):
        cmd = 'cd %(path)s ; tail -20 log/mongod.log' % self.args
        print self._remote_run(cmd)

    def clean(self):
        if self._alive():
            raise Exception("%s is still running, we can't clean it" % self)
        cmd = 'rm -rf %(path)s' % self.args
        print self._remote_run(cmd)

class Replset(Base):
    '''
    replset: 
        we should add user from primary
    '''
    def __init__(self, args):
        args['role'] = self.__class__.__name__
        args['user'] = args['auth']['user']
        args['password'] = args['auth']['password']
        args['key'] = args['auth']['key']

        self.args = args
        self.mongods = []
        self.primary = None

        for host, port, path in self.args['mongod']:
            mongod = {
                'type' : 'Mongod',
                'ssh_user' : args['ssh_user'],
                'auth' : args['auth'],
                'replset_name': args['replset_name'],
                'host': host,
                'port': port,
                'path': path,
            }
            self.mongods.append(mongod)

    def __str__(self):
        hosts = ','.join(['%s:%d' % (h, p) for h, p, _p in  self.args['mongod']])
        return '[%(role)s] %(replset_name)s : ' + hosts

    def _runjs(self, js, need_primary):
        logging.info('_run_js: \n' + js.replace(' ', '').replace('\n', '  '))
        filename = TmpFile().content_to_tmpfile(js)

        if need_primary:
            primary = self._get_primary()
            host, port = primary.split(':')
        else:
            primary = self.args['mongod'][0]
            host = socket.gethostbyname(primary[0])
            port = primary[1]

        key = self.args['key']

        cmd = './mongodb-base/bin/mongo --quiet %(host)s:%(port)s/admin -u __system -p %(key)s' % locals()
        cmd += ' ' + filename
        r = common.system(cmd, logging.info)
        if r.find('command failed') >=0 or r.find('uncaught exception') >=0:
            raise Exception('run js error: \n' + r)

        logging.debug(r)
        return r

    def _get_primary(self):
        if self.primary:
            return self.primary
        js = 'printjson(rs.isMaster())'
        rst = self._runjs(js, need_primary=False)
        rst = re.sub('"localTime" : ISODate\(".*?"\),', '', rst)
        #print rst
        json = common.json_decode(rst)
        if 'primary' in json:
            self.primary = json['primary']
            return self.primary
        else:
            return None

    def _rs_init(self):
        members = [{'_id': id, 'host': '%s:%d'%(host,port) } for (id, (host, port, path)) in enumerate(self.args['mongod'])]
        replset_config = {
            '_id': self.args['replset_name'],
            'members': members
        }
        js = '''
        config = %s;
        rs.initiate(config);
        ''' % json.dumps(replset_config)
        
        self._runjs(js, need_primary=False)

        
        while True:
            primary = self._get_primary()
            if primary:
                break
            logging.debug("waiting for rs.init")
            time.sleep(3)
        
        logging.info('primary is %s ' % primary)
        host, port = primary.split(':')
        port = int(port) + 1000
        user = self.args['user']
        password = self.args['password']
        logging.info('see http://%(user)s:%(password)s@%(host)s:%(port)s/_replSet' % locals())

    def _adduser(self):
        js = 'db.addUser("%(user)s", "%(password)s");' % self.args
        self._runjs(js, need_primary=True)

    def start(self):
        for mongod in self.mongods:
            Mongod(mongod).start()
        self._rs_init()
        self._adduser()

    def stop(self):
        for mongod in self.mongods:
            Mongod(mongod).stop()

    def ps(self):
        for mongod in self.mongods:
            Mongod(mongod).ps()
        self._get_primary()

    def log(self):
        for mongod in self.mongods:
            Mongod(mongod).log()

    def kill(self):
        for mongod in self.mongods:
            Mongod(mongod).kill()

    def clean(self):
        for mongod in self.mongods:
            Mongod(mongod).clean()

class Mongos(Mongod):
    pass

class Configserver(Mongod):
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
    eval('%s(%s).%s()' % (cluster['type'], cluster, args.op) )

if __name__ == "__main__":
    parse_args()

