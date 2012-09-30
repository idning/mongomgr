#!/usr/bin/python
#coding: utf-8
#file   : config.py
#author : ning
#date   : 2012-08-24 07:37:52


#the downloaded mongodb-static-legacy path
MONGO_DB_PATH = '/home/ning/soft/mongodb-linux-x86_64-2.0.6/'

# user account in target machine
USER = 'ning'

#replset config 1 (should startswith "cluster")
cluster0 = [
    # host,  port, install path
    ['localhost', 30001, '/tmp/mongodb-deploy/cluster0/mongodb-30001'],
    ['localhost', 30002, '/tmp/mongodb-deploy/cluster0/mongodb-30002'],
    ['localhost', 30003, '/tmp/mongodb-deploy/cluster0/mongodb-30003'],
    ['localhost', 30004, '/tmp/mongodb-deploy/cluster0/mongodb-30004'],
    ['localhost', 30005, '/tmp/mongodb-deploy/cluster0/mongodb-30005'],
]

#replset config 2 (should startswith "cluster")
cluster1 = [
    # host,  port, install path
    ['localhost', 31001, '/home/ning/idning-github/mongomgr/deploy-zone/cluster1/mongodb-31001'],
    ['localhost', 31002, '/home/ning/idning-github/mongomgr/deploy-zone/cluster1/mongodb-31002'],
    ['localhost', 31003, '/home/ning/idning-github/mongomgr/deploy-zone/cluster1/mongodb-31003'],
    ['localhost', 31004, '/home/ning/idning-github/mongomgr/deploy-zone/cluster1/mongodb-31004'],
    ['localhost', 31005, '/home/ning/idning-github/mongomgr/deploy-zone/cluster1/mongodb-31005'],
]
