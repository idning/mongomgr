#!/usr/bin/python
#coding: utf-8
#file   : config.py
#author : ning
#date   : 2012-08-24 07:37:52


#the downloaded mongodb-static-legacy path
MONGO_DB_PATH = '/home/yanglin/soft_packages/mongodb-linux-x86_64-static-legacy-2.0.6/'

# user account in target machine

#replset config 1 (should startswith "cluster")
cluster0 = {
    'type' : 'replset',
    'user' : 'rd',
    'replset_name' : 'cluster0',
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
    'user' : 'rd',
    'replset_name' : 'set1',
    'mongod': [
        # host,  port, install path
        ['10.65.16.245', 7501, '/home/rd/mongodb-deploy/cluster0/mongodb-7501'],
        ['10.65.19.52' , 7501, '/home/rd/mongodb-deploy/cluster0/mongodb-7501'],
        ['10.65.16.151', 7501, '/home/rd/mongodb-deploy/cluster0/mongodb-7501'],
    ]
}


cluster_10 = {
    'type' : 'sharding',
    'user' : 'rd',
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


cluster_j = {
    'type' : 'sharding',
    'user' : 'bae',
    'configserver': [
        # host,  port, install path
        ['10.42.42.58', 7222, '/home/bae/configsvr'],
    ],
    'mongos': [
        # host,  port, install path
        ['10.46.190.58', 7333, '/home/bae/mongos'],
    ], 
    'shard': [
        { # shard 1
            'type' : 'mongod',
            'server': ['10.46.190.58', 7111, '/home/bae/mongod'],
        },
        { # shard 2
            'type' : 'mongod',
            'server': ['10.42.42.58',  7111, '/home/bae/mongod'],
        },
    ]
}
