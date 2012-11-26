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
cluster0 = {
    'type' : 'replset',
    'host': [
        # host,  port, install path
        ['127.0.0.1', 30001, '/tmp/mongodb-deploy/cluster0/mongodb-30001'],
        ['127.0.0.1', 30002, '/tmp/mongodb-deploy/cluster0/mongodb-30002'],
        ['127.0.0.1', 30003, '/tmp/mongodb-deploy/cluster0/mongodb-30003'],
        ['127.0.0.1', 30004, '/tmp/mongodb-deploy/cluster0/mongodb-30004'],
        ['127.0.0.1', 30005, '/tmp/mongodb-deploy/cluster0/mongodb-30005'],
    ]
}


shard0 = cluster0
shard1 = {
    'type' : 'replset',
    'host': [
        # host,  port, install path
        ['127.0.0.1', 30011, '/tmp/mongodb-deploy/cluster0/mongodb-30011'],
        ['127.0.0.1', 30012, '/tmp/mongodb-deploy/cluster0/mongodb-30012'],
        ['127.0.0.1', 30013, '/tmp/mongodb-deploy/cluster0/mongodb-30013'],
    ]
}


cluster_10 = {
    'type' : 'sharding',
    'config-server': [
        # host,  port, install path
        ['127.0.0.1', 30101, '/tmp/mongodb-deploy/cluster0/mongodb-30101'],
        ['127.0.0.1', 30102, '/tmp/mongodb-deploy/cluster0/mongodb-30102'],
        ['127.0.0.1', 30103, '/tmp/mongodb-deploy/cluster0/mongodb-30103'],
    ],
    'mongos': [
        # host,  port, install path
        ['127.0.0.1', 30201, '/tmp/mongodb-deploy/cluster0/mongodb-30201'],
        ['127.0.0.1', 30202, '/tmp/mongodb-deploy/cluster0/mongodb-30202'],
        ['127.0.0.1', 30203, '/tmp/mongodb-deploy/cluster0/mongodb-30203'],
    ], 
    'shard': [
        shard0,
        shard1,
    ]
}

