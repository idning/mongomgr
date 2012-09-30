
mongodb manager scripts

you need rsync, ssh(ssh to target machines without password)

1. deploy
===============

config in config.py::

    #the downloaded mongodb-static-legacy path
    MONGO_DB_PATH = '/home/ning/soft/mongodb-linux-x86_64-2.0.6/'

    # user account in target machine
    USER = 'ning'

    cluster0 = [
        # host,  port, install path
        ['localhost', 30001, '/tmp/mongodb-deploy/cluster0/mongodb-30001'],
        ['localhost', 30002, '/tmp/mongodb-deploy/cluster0/mongodb-30002'],
        ['localhost', 30003, '/tmp/mongodb-deploy/cluster0/mongodb-30003'],
        ['localhost', 30004, '/tmp/mongodb-deploy/cluster0/mongodb-30004'],
        ['localhost', 30005, '/tmp/mongodb-deploy/cluster0/mongodb-30005'],
    ]

start mongodb replset ::

    ./deploy.py start cluster0

stop mongodb replset ::

    ./deploy.py stop cluster0

undeploy mongodb replset ::

    ./deploy.py clean cluster0



