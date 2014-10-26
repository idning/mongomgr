#!/usr/bin/python
#coding: utf-8
#file   : config.py
#author : ning
#date   : 2012-08-24 07:37:52


#the downloaded mongodb-static-legacy path
MONGO_DB_PATH = '/home/yanglin/soft_packages/mongodb-build-zf00/'

# hide it
cluster_jomo = {
    'type' : 'sharding',
    'user' : 'ning',
    'configserver': [
        # host,  port, install path
        ['10.46.190.58', 7222, '/home/ning/configsvr'],
    ],
    'mongos': [
        # host,  port, install path
        ['10.46.190.58', 7333, '/home/ning/mongos'],
    ],
    'shard': [
        { # shard 1
            'type' : 'mongod',
            'server': ['10.46.190.58', 7111, '/home/ning/mongod'],
        },
        #{ # shard 2 @ jomo-0
            #'type' : 'mongod',
            #'server': ['10.42.42.58',  7111, '/home/ning/mongod'],
        #},
        { # shard 2
            'type' : 'mongod',
            'server': ['10.26.140.32',  7111, '/home/ning/mongod'],
        },
        { # shard 2
            'type' : 'mongod',
            'server': ['10.26.138.25',  7111, '/home/ning/mongod'],
        },
    ]
}

cluster_single_mongod = {
    'type' : 'Mongod',
    'ssh_user' : 'ning',
    'host': '10.65.16.245',
    'port': 7200,
    'path': '/home/ning/mongodb-deploy/cluster0/mongodb-7200',
    'auth' : {
        'user': 'ning',            # we will add this user at last
        'password': 'pass',      #
        'key':      'pass',      # keyfile auth (the __system password)
    },
    'replset_name': 'test-replset'
    #'extra' : '--replSet xxx',  #optional arg
}

#replset config 1 (should startswith "cluster")
cluster0 = {
    'type' : 'Replset',
    'ssh_user' : 'ning',
    'auth' : {
        'user': 'ning',            # we will add this user at last
        'password': 'pass',      #
        'key':      'pass',      # keyfile auth (the __system password)
    },
    'replset_name' : 'cluster0',
    'mongod': [
        # host,  port, install path
        ['10.65.16.245', 7500, '/home/ning/mongodb-deploy/cluster0/mongodb-7500'],
        ['10.65.19.52' , 7500, '/home/ning/mongodb-deploy/cluster0/mongodb-7500'],
        ['10.65.16.151', 7500, '/home/ning/mongodb-deploy/cluster0/mongodb-7500'],
        ['10.65.19.26' , 7500, '/home/ning/mongodb-deploy/cluster0/mongodb-7500'],
        ['10.65.19.27' , 7500, '/home/ning/mongodb-deploy/cluster0/mongodb-7500'],
    ]
}

cluster_mig = {
    'type' : 'Sharding',
    'ssh_user' : 'ning',
    'auth' : {
        'user': 'ning',            # we will add this user at last
        'password': 'pass',      #
        'key':      'pass',      # keyfile auth (the __system password)
    },
    'configserver': [
        # host,  port, install path
        ['10.65.16.245', 37222, '/home/ning/mongodb-deploy/cluster_t2/configsvr'],
    ],
    'mongos': [
        # host,  port, install path
        ['10.65.19.52', 37333, '/home/ning/mongodb-deploy/cluster_t2/mongos'],
    ],
    'shard': [
        { # shard 1
            'type' : 'Replset',
            'replset_name' : 'set_test_1',
            'mongod': [
                # host,  port, install path
                ['10.65.16.245', 37111, '/home/ning/mongodb-deploy/cluster_t2/mongodb-37111'],
                ['10.65.19.52', 37111, '/home/ning/mongodb-deploy/cluster_t2/mongodb-37111'],
                ['10.65.19.26', 37111, '/home/ning/mongodb-deploy/cluster_t2/mongodb-37111'],
            ]
        },
        { # shard 2
            'type' : 'Replset',
            'replset_name' : 'set_test_2',
            'mongod': [
                # host,  port, install path
                ['10.65.16.245', 47111, '/home/ning/mongodb-deploy/cluster_t2/mongodb-47111'],
                ['10.65.19.52', 47111, '/home/ning/mongodb-deploy/cluster_t2/mongodb-47111'],
                ['10.65.19.26', 47111, '/home/ning/mongodb-deploy/cluster_t2/mongodb-47111'],
            ]
        },
    ]
}

