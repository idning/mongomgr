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
        ['10.65.16.245', 7500, '/home/rd/mongodb-deploy/cluster0/mongodb-7500'],
        ['10.65.19.52' , 7500, '/home/rd/mongodb-deploy/cluster0/mongodb-7500'],
        ['10.65.16.151', 7500, '/home/rd/mongodb-deploy/cluster0/mongodb-7500'],
        ['10.65.19.26' , 7500, '/home/rd/mongodb-deploy/cluster0/mongodb-7500'],
        ['10.65.19.27' , 7500, '/home/rd/mongodb-deploy/cluster0/mongodb-7500'],
    ]
}


shard0 = cluster0
shard1 = {
    'type' : 'replset',
    'mongod': [
        # host,  port, install path
        ['10.65.16.245', 7501, '/home/rd/mongodb-deploy/cluster0/mongodb-7501'],
        ['10.65.19.52' , 7501, '/home/rd/mongodb-deploy/cluster0/mongodb-7501'],
        ['10.65.16.151', 7501, '/home/rd/mongodb-deploy/cluster0/mongodb-7501'],
    ]
}


cluster_10 = {
    'type' : 'sharding',
    'configserver': [
        # host,  port, install path
        ['10.65.16.245', 30001, '/home/rd/mongodb-deploy/cluster0/mongodb-30001'],
        ['10.65.19.52' , 30001, '/home/rd/mongodb-deploy/cluster0/mongodb-30001'],
        ['10.65.16.151', 30001, '/home/rd/mongodb-deploy/cluster0/mongodb-30001'],
    ],
    'mongos': [
        # host,  port, install path
        ['10.65.16.245', 30002, '/home/rd/mongodb-deploy/cluster0/mongodb-30002'],
        ['10.65.19.52' , 30002, '/home/rd/mongodb-deploy/cluster0/mongodb-30002'],
        ['10.65.16.151', 30002, '/home/rd/mongodb-deploy/cluster0/mongodb-30002'],
    ], 
    'shard': [
        shard0,
        shard1,
    ]
}

