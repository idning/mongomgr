
mongodb manager scripts

you need : 

1. rsync
2. ssh(ssh-copy-id for ssh to target machines without password)

config
===============

define a sharding in config.py::

    #the downloaded mongodb-static-legacy path
    MONGO_DB_PATH = '/home/ning/soft/mongodb-linux-x86_64-2.0.6/'

    # user account in target machine
    USER = 'ning'

    #replset config 1 (should startswith "cluster")
    cluster0 = {
        'type' : 'replset',
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

usage
===============

start mongodb replset ::

    $ ./deploy.py start cluster_10

    [INFO] mongostat --host 10.65.16.245 --port 7500 -n1
    [INFO] ssh -n -f rd@10.65.16.245 "mkdir -p /home/rd/mongodb-deploy/cluster0/mongodb-7500 "
    [INFO] rsync -avP ./mongodb-base/ rd@10.65.16.245:/home/rd/mongodb-deploy/cluster0/mongodb-7500 1>/dev/null 2>/dev/null
    [INFO] ssh -n -f rd@10.65.16.245 "cd /home/rd/mongodb-deploy/cluster0/mongodb-7500 ; ./bin/mongod -f ./conf/mongod.conf --port 7500 --replSet cluster0 --fork "
    forked process: 5974
    all output going to: /home/rd/mongodb-deploy/cluster0/mongodb-7500/./log/mongod.log

    ...

    [INFO] ./mongodb-base/bin/mongo 10.65.16.245:30002/admin ./tmp/_2013-01-22_17_54_43_063068
    MongoDB shell version: 2.0.6
    connecting to: 10.65.16.245:30002/admin
    --- Sharding Status ---
      sharding version: { "_id" : 1, "version" : 3 }
      shards:
            {  "_id" : "cluster0",  "host" : "cluster0/10.65.16.151:7500,10.65.16.245:7500,10.65.19.26:7500,10.65.19.27:7500,10.65.19.52:7500" }
            {  "_id" : "set1",  "host" : "set1/10.65.16.151:7501,10.65.16.245:7501,10.65.19.52:7501" }
      databases:
            {  "_id" : "admin",  "partitioned" : false,  "primary" : "config" }


see status::

    $ ./deploy.py ps cluster_10
    [INFO] rm -rf ./mongodb-base
    [INFO] cp -rf /home/yanglin/soft_packages/mongodb-linux-x86_64-static-legacy-2.0.6/ ./mongodb-base
    [INFO] mkdir -p ./mongodb-base/conf
    [INFO] mkdir -p ./mongodb-base/log
    [INFO] mkdir -p ./mongodb-base/db
    [INFO] cp mongod.conf ./mongodb-base/conf
    [INFO] ssh -n -f rd@10.65.16.245 "pgrep -l -f './bin/mongod -f ./conf/mongod.conf --port 7500 '"
    5974 ./bin/mongod -f ./conf/mongod.conf --port 7500 --replSet cluster0 --fork
    [INFO] ssh -n -f rd@10.65.19.52 "pgrep -l -f './bin/mongod -f ./conf/mongod.conf --port 7500 '"
    26455 ./bin/mongod -f ./conf/mongod.conf --port 7500 --replSet cluster0 --fork
    [INFO] ssh -n -f rd@10.65.16.151 "pgrep -l -f './bin/mongod -f ./conf/mongod.conf --port 7500 '"
    19047 ./bin/mongod -f ./conf/mongod.conf --port 7500 --replSet cluster0 --fork
    [INFO] ssh -n -f rd@10.65.19.26 "pgrep -l -f './bin/mongod -f ./conf/mongod.conf --port 7500 '"
    6985 ./bin/mongod -f ./conf/mongod.conf --port 7500 --replSet cluster0 --fork
    [INFO] ssh -n -f rd@10.65.19.27 "pgrep -l -f './bin/mongod -f ./conf/mongod.conf --port 7500 '"
    1334 ./bin/mongod -f ./conf/mongod.conf --port 7500 --replSet cluster0 --fork
    [INFO] ssh -n -f rd@10.65.16.245 "pgrep -l -f './bin/mongod -f ./conf/mongod.conf --port 7501 '"
    6688 ./bin/mongod -f ./conf/mongod.conf --port 7501 --replSet set1 --fork
    [INFO] ssh -n -f rd@10.65.19.52 "pgrep -l -f './bin/mongod -f ./conf/mongod.conf --port 7501 '"

stop/kill mongodb replset ::

    ./deploy.py stop cluster0

undeploy mongodb replset ::

    ./deploy.py clean cluster0



