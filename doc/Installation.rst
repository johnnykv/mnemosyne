************
Installation
************

Prerequisites
=============

Get Mnemosyne::

    $ git clone https://github.com/johnnykv/mnemosyne.git


Install python requirements::

    $ pip install -r requirements.txt


Configuration
=============

Copy default configuration::

    cp mnemosyne.cfg.dist mnemosyne.cfg

While testing it is recommended to simplify the configuration as much as possible, example::

    [webapi]
    # 0.0.0.0 = listen on all interfaces
    host = 0.0.0.0
    port = 8181

    [mongodb]
    database = mnemosyne

    [hpfriends]
    ident = <IDENT FROM HPFRIENDS>
    secret = <SECRET FROM HPFRIENDS>
    host = hpfriends.honeycloud.net
    port = 20000
    channels = dionaea.capture

    [file_log]
    enabled = True
    file = mnemosyne.log

    [loggly_log]
    enabled = False
    token =

Running
=======

First off, you need to start mongod, afterwards you can start mnemosyne::

    $ python runner.py
    2013-09-09 21:44:58,541 (root) Starting mnemosyne. (Git: af0388c4a9a251bdafa0d2a5d1de262b7c94b08c)
    2013-09-09 21:44:58,542 (persistance.mnemodb) Connecting to mongodb, using "mnemosyne" as database.
    2013-09-09 21:44:58,543 (persistance.preagg_reports) Connecting to mongodb, using "mnemosyne" as database.
    2013-09-09 21:44:58,653 (root) Spawning hpfriends feed puller.
    2013-09-09 21:44:58,653 (root) Spawning web api.
    2013-09-09 21:44:58,653 (webapi.mnemowebapi) Cork authentication files not found, creating new files.
    2013-09-09 21:44:58,653 (webapi.mnemowebapi) Creating new authentication files, check STDOUT for the generated admin password.
    A 'admin' account has been created with the password 'df02548f-fc01-40ca-808a-15ba07aed8d5'
    2013-09-09 21:44:58,670 (root) Spawning normalizer
    2013-09-09 21:44:58,670 (pyhpfeeds) connecting to hpfriends.honeycloud.net:20000
    2013-09-09 21:44:58,671 (webapi.mnemowebapi) Starting web api, listening on 0.0.0.0:8181
    2013-09-09 21:44:59,236 (pyhpfeeds) info message name: hpfriends, rand: '}\xbb\xbb\xe1'
    2013-09-09 21:44:59,236 (pyhpfeeds) Sending subscription for dionaea.capture.
Please notice that the the generated admin password was printed on line 9.

After running mnemosyne for a short while, you can fire up the mongo console at check the database, example::

    $ mongo
    MongoDB shell version: 2.4.4
    connecting to: test
    Server has startup warnings:
    > use mnemosyne
    switched to db mnemosyne
    > db.hpfeed.count()
    28747
    > db.session.count()
    27154
    > db.session.find().limit(1).pretty()
    {
        "_id" : ObjectId("522e253b79b45e7673aa4a6d"),
        "destination_ip" : [
            "18.17.141.211"
        ],
        "protocol" : "microsoft-ds",
        "attachments" : [
            {
                "hashes" : {
                    "sha512" : "e2de6f3a3927d92f213bf153f72f2a1407a1f9f350a54115f38453aa85a6087debdab2160f246ff3808d0f6b679b6dc421fa5d5f1aa6271684de31ec0952deb0",
                    "md5" : "94e689d7d6bc7c769d09a59066727497"
                },
                "description" : "Binary extraction"
            }
        ],
        "timestamp" : ISODate("2013-09-07T22:42:33.808Z"),
        "source_ip" : "177.100.148.19",
        "source_port" : 4483,
        "destination_port" : 445,
        "honeypot" : "dionaea",
        "hpfeed_id" : ObjectId("522babd979b45e68a094614a")
    }
    >
