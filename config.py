#!/usr/bin/python
#coding: utf-8
#file   : config.py
#author : ning
#date   : 2012-08-24 07:37:52


#the downloaded mongodb-static-legacy path
MONGO_DB_PATH = '/home/yanglin/soft_packages/mongodb-linux-x86_64-static-legacy-2.0.6/'

# user account in target machine
USER = 'rd'

#replset config 1 (should startswith "cluster")
cluster0 = {
    'type' : 'replset',
    'mongod': [
        # host,  port, install path
        ['10.65.16.245', 30001, '/home/rd/mongodb-deploy/cluster0/mongodb-30001'],
        ['10.65.19.52' , 30002, '/home/rd/mongodb-deploy/cluster0/mongodb-30002'],
        ['10.65.16.151', 30003, '/home/rd/mongodb-deploy/cluster0/mongodb-30003'],
        ['10.65.19.26' , 30004, '/home/rd/mongodb-deploy/cluster0/mongodb-30004'],
        ['10.65.19.27' , 30005, '/home/rd/mongodb-deploy/cluster0/mongodb-30005'],
    ]
}


shard0 = cluster0
shard1 = {
    'type' : 'replset',
    'mongod': [
        # host,  port, install path
        ['10.65.16.245', 30011, '/home/rd/mongodb-deploy/cluster0/mongodb-30011'],
        ['10.65.19.52' , 30012, '/home/rd/mongodb-deploy/cluster0/mongodb-30012'],
        ['10.65.16.151', 30013, '/home/rd/mongodb-deploy/cluster0/mongodb-30013'],
    ]
}


cluster_10 = {
    'type' : 'sharding',
    'configserver': [
        # host,  port, install path
        ['10.65.16.245', 30101, '/home/rd/mongodb-deploy/cluster0/mongodb-30101'],
        ['10.65.19.52' , 30102, '/home/rd/mongodb-deploy/cluster0/mongodb-30102'],
        ['10.65.16.151', 30103, '/home/rd/mongodb-deploy/cluster0/mongodb-30103'],
    ],
    'mongos': [
        # host,  port, install path
        ['10.65.16.245', 30201, '/home/rd/mongodb-deploy/cluster0/mongodb-30201'],
        ['10.65.19.52' , 30202, '/home/rd/mongodb-deploy/cluster0/mongodb-30202'],
        ['10.65.16.151', 30203, '/home/rd/mongodb-deploy/cluster0/mongodb-30203'],
    ], 
    'shard': [
        shard0,
        shard1,
    ]
}

