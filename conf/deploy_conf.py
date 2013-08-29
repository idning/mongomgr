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


# hide it
cluster_jomo = {
    'type' : 'sharding',
    'user' : 'bae',
    'configserver': [
        # host,  port, install path
        ['10.46.190.58', 7222, '/home/bae/configsvr'],
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
        #{ # shard 2 @ jomo-0
            #'type' : 'mongod', 
            #'server': ['10.42.42.58',  7111, '/home/bae/mongod'],
        #},
        { # shard 2
            'type' : 'mongod',
            'server': ['10.26.140.32',  7111, '/home/bae/mongod'],
        },
        { # shard 2
            'type' : 'mongod',
            'server': ['10.26.138.25',  7111, '/home/bae/mongod'],
        },
    ]
}

cluster_test = {
    'type' : 'sharding',
    'user' : 'rd',
    'configserver': [
        # host,  port, install path
        ['10.65.16.245', 17222, '/home/rd/mongodb-deploy/cluster_test/configsvr'],
    ],
    'mongos': [
        # host,  port, install path
        ['10.65.19.52', 17333, '/home/rd/mongodb-deploy/cluster_test/mongos'],
        ['10.65.16.245', 17333, '/home/rd/mongodb-deploy/cluster_test/mongos'],
    ], 
    'shard': [
        { # shard 1
            'type' : 'replset',
            'replset_name' : 'set_test_1',
            'mongod': [
                # host,  port, install path
                ['10.65.16.245', 17111, '/home/rd/mongodb-deploy/cluster_test/mongodb-17111'],
                ['10.65.19.52', 17111, '/home/rd/mongodb-deploy/cluster_test/mongodb-17111'],
                ['10.65.19.26', 17111, '/home/rd/mongodb-deploy/cluster_test/mongodb-17111'],
            ]
        },
        { # shard 2
            'type' : 'replset',
            'replset_name' : 'set_test_2',
            'mongod': [
                # host,  port, install path
                ['10.65.16.245', 27111, '/home/rd/mongodb-deploy/cluster_test/mongodb-27111'],
                ['10.65.19.52', 27111, '/home/rd/mongodb-deploy/cluster_test/mongodb-27111'],
                ['10.65.19.26', 27111, '/home/rd/mongodb-deploy/cluster_test/mongodb-27111'],
            ]
        },
    ]
}

cluster_mig = {
    'type' : 'sharding',
    'user' : 'rd',
    'auth' : {                  # only for sharding
        'user': 'structure', 
        'password': 'PcSmongoPcS', 
    },
    'configserver': [
        # host,  port, install path
        ['10.65.16.245', 37222, '/home/rd/mongodb-deploy/cluster_t2/configsvr'],
    ],
    'mongos': [
        # host,  port, install path
        ['10.65.19.52', 37333, '/home/rd/mongodb-deploy/cluster_t2/mongos'],
    ], 
    'shard': [
        { # shard 1
            'type' : 'replset',
            'replset_name' : 'set_test_1',
            'mongod': [
                # host,  port, install path
                ['10.65.16.245', 37111, '/home/rd/mongodb-deploy/cluster_t2/mongodb-37111'], #jx-bae-bcs0.jx.baidu.com
                ['10.65.19.52', 37111, '/home/rd/mongodb-deploy/cluster_t2/mongodb-37111'],
                ['10.65.19.26', 37111, '/home/rd/mongodb-deploy/cluster_t2/mongodb-37111'],
            ]
        },
        { # shard 2
            'type' : 'replset',
            'replset_name' : 'set_test_2',
            'mongod': [
                # host,  port, install path
                ['10.65.16.245', 47111, '/home/rd/mongodb-deploy/cluster_t2/mongodb-47111'],
                ['10.65.19.52', 47111, '/home/rd/mongodb-deploy/cluster_t2/mongodb-47111'],
                ['10.65.19.26', 47111, '/home/rd/mongodb-deploy/cluster_t2/mongodb-47111'],
            ]
        },
    ]
}

