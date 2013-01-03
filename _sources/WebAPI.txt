******
WebAPI
******

Introduction
============

Some thought here...

HPFeeds
=======
.. http:get:: /hpfeeds/channels

   Distinct channel names and count of items.

   **Example request**:

   .. sourcecode:: http

       GET /hpfeeds/channels HTTP/1.1
       Host: example.com
       Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "channels": [
          {
            "count": 3165,
            "channel": "glastopf.events"
          },
          {
            "count": 6,
            "channel": "thug.files"
          },
          {
            "count": 24,
            "channel": "thug.events"
          },
          {
            "count": 68,
            "channel": "glastopf.files"
          },
          {
            "count": 728,
            "channel": "kippo.sessions"
          },
          {
            "count": 70035,
            "channel": "dionaea.capture"
          },
          {
            "count": 61,
            "channel": "mwbinary.dionaea.sensorunique"
          }
        ]
      }

.. http:get:: /hpfeeds

   Retrieve the latest received items from a specific HPFeeds channel.

   **Example request**:

   .. sourcecode:: http

      GET /hpfeeds?channel=glastopf.events HTTP/1.1
      Host: example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "hpfeeds": [
          {
            "ident": "2l3if@hp8",
            "timestamp": "2012-12-26T20:01:46.908000",
            "normalized": true,
            "_id": "5deadbeef0e0f7b874e8088d",
            "payload": "<payload>",
            "channel": "glastopf.events"
          },
          {
            "ident": "2l3if@hp8",
            "timestamp": "2012-12-26T20:05:32.773000",
            "normalized": false,
            "_id": "50db57aadfe0f7b8deadbeef",
            "payload": "<payload>",
            "channel": "glastopf.events"
          }
        ]
      }

   :query channelname: channel name (required).
   :query limit: limit number of returned items (optional, default is 50).
   :statuscode 200: no error.
   :statuscode 403: Listing of all content forbidden.


.. http:get:: /hpfeeds/(hpfeed_id)

   The hpfeed entry with id (string:hpfeed_id).

   **Example request**:

   .. sourcecode:: http

       GET /hpfeeds/50dbdeadbeeff7b874e806ba HTTP/1.1
       Host: example.com
       Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

       HTTP/1.1 200 OK
       Content-Type: application/json

       {
           "ident": "2l3if@hp8",
           "timestamp": "2012-12-26T19:49:22.212000",
           "normalized": true,
           "_id": "50dbdeadbeeff7b874e806ba",
           "payload": "<payload>",
           "channel": "glastopf.events"
       }

   :param hpfeed_id: hpfeed's unique id.
   :type hpfeed_id: string
   :statuscode 200: no error.
   :statuscode 400: Bad request.

Sessions
========
.. http:get:: /sessions/protocols

   Distinct protocols and session count from normalized honeypot sessions.

   **Example request**:

   .. sourcecode:: http

          GET /sessions/protocols HTTP/1.1
          Host: example.com
          Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

         HTTP/1.1 200 OK
         Content-Type: application/json

         {
           "protocols": [
             {
               "count": 3212,
               "protocol": "http"
             },
             {
               "count": 728,
               "protocol": "ssh"
             },
             {
               "count": 75392,
               "protocol": "microsoft-ds"
             },
             {
               "count": 8,
               "protocol": "dcom-scm"
             }
           ]
         }

.. http:get:: /sessions/(string:session_id)

   The sesion entry with id (string:session_id).

   **Example request**:

   .. sourcecode:: http

       GET /sessions/11dbdeadbeeff7b874e806ff HTTP/1.1
       Host: example.com
       Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

         HTTP/1.1 200 OK
         Vary: Accept
         Content-Type: application/json

         {
           "sessions": {
             "_id": "40e551dedfe0f61a450f9c39",
             "honeypot": "Glastopf"
             "protocol": "http",
             "hpfeed_id": "50da20b2dfe0f7b0b5fc37d6",
             "timestamp": "2012-12-25T15:52:45",
             "destination_port": 80,
             "source_ip": "11.224.111.2",
             "source_port": 57462,
             "session_http": {
               "request": {
                 "body": "",
                 "header": "{\"Accept-Language\": \"en-gb,en;q=0.5\", \"Proxy-Connection\": \"Keep-Alive\", \"Accept\": \"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\", \"User-Agent\": \"Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.28) Gecko/20120306 Firefox/3.6.28 (.NET CLR 3.5.30729)\", \"Accept-Charset\": \"ISO-8859-1,utf-8;q=0.7,*;q=0.7\", \"Host\": \"xxmexxame.net\", \"Pragma\": \"no-cache\", \"Cache-Control\": \"no-cache\", \"Accept-Encoding\": \"deflate, gzip\"}",
                 "host": "xxmexxame.net",
                 "verb": "GET",
                 "url": "http://xxmexxame.net/headers"
               }
             }
           }
         }

   :statuscode 200: no error.
   :statuscode 400: Bad request.

.. http:get:: /sessions

   Returns sessions filtered by query parameters.

   **Example request**:

   .. sourcecode:: http

       GET /sessions?honeypot=kippo&source_port=36888 HTTP/1.1
       Host: example.com
       Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

         HTTP/1.1 200 OK
         Content-Type: application/json

         {
           "sessions": [
             {
               "protocol": "ssh",
               "hpfeed_id": "50dc4244dfe0f7bf93d06076",
               "timestamp": "2012-12-27T12:42:44.296000",
               "source_ip": "181.5.23.53",
               "session_ssh": {
                 "version": "SSH-2.0-libssh-0.1"
               },
               "source_port": 36868,
               "destination_port": 2222,
               "_id": "50dcc2ebdfe0f7c4d1ce350d",
               "honeypot": "Kippo",
               "auth_attempts": [
                 {
                   "login": "root",
                   "password": "321muie321"
                 }
               ]
             },
             {
               "protocol": "ssh",
               "hpfeed_id": "50dc4249dfe0f7bf93d06077",
               "timestamp": "2012-12-27T12:42:49.131000",
               "source_ip": "182.5.23.53",
               "session_ssh": {
                 "version": "SSH-2.0-libssh-0.1"
               },
               "source_port": 36868,
               "destination_port": 2222,
               "_id": "50dcc2ebdfe0f7c4d1ce350e",
               "honeypot": "Kippo",
               "auth_attempts": [
                 {
                   "login": "root",
                   "password": "123muie123"
                 }
               ]
             }
           ]
         }

   :query protocol: protocol name -  ssh, imap, etc (optional).
   :query honeypot: honeypot type - kippo, dionaea, glastopf, etc (optional).
   :query source_ip: ip address of attacker (optional).
   :query source_port: tcp port of attacker (optional).
   :query destination_ip: ip address of honeypot (optional).
   :query destination_port: tcp port of honeypot (optional).
   :query limit: limit number of returned items (optional, default is 50).
   :statuscode 200: no error.
   :statuscode 400: Bad request.


URLS
========

.. http:get:: /urls

   Returns urls serving potiential malicious content. If any files has been extracted, an reference to the checksum will be provided.

   **Example request**:

   .. sourcecode:: http

       GET /urls?url_regex=\.ru(\/|\:|$) HTTP/1.1
       Host: example.com
       Accept: application/json

   **Example response**:

   .. sourcecode:: http

         HTTP/1.1 200 OK
         Content-Type: application/json

         {
           "urls": [
             {
               "_id": "50e5e440cfd26d1f23bfe7b8",
               "url": "http://xxxyyyzzz.ru/count26.php"
               "extractions": [
                 [
                   {
                     "timestamp": "2012-12-26T13:51:13.507000",
                     "hashes": {
                       "md5": "549exxb6939274deadbeef01e4771c4",
                       "sha1": "deafbeef20b1e214d35b044483bf04ae1f0a7b4d",
                       "sha512": "53ece41162e635bd93ea3240c12b4a844974deadbeed30da1f18f8e2892c10a9930a2380673afd4521083b9f952a10b3c54de3be477ab1f11c61a8902c0d435"
                     }
                   }
                 ]
               ],
               "hpfeed_ids": [
                 "50da8260dfe0f7b2c68c2fde"
               ]
             },
             {
               "_id": "50e5e5a4cfd26d1f23bffce7",
               "url": "http://putskixxxyy.ru",
               "extractions": [
                 [
                   {
                     "timestamp": "2013-01-03T13:06:23.917000"
                     "hashes": {
                       "md5": "1871bd38d860deafbeefdaae831a9441",
                       "sha1": "1a57e92deafbeed691000c1c2a77de124bb6402e",
                       "sha512": "a22306bdf51bd8fe6efb52685287e7edeadbeef5a7880bcba5146ea24e6091c54e7f9579f9ce6a979d40f284b72ee8c316d902925c2fba58b206fb621778bd48"
                     }
                   },
                   {
                     "timestamp": "2013-01-03T13:06:23.917000"
                     "hashes": {
                       "md5": "f8aa58a9deafbeef6c710d2ca078fbd0",
                       "sha1": "a1455c9ad5ea26a1deafbeef168d2cf810ef421c",
                       "sha512": "ad887e8d6c31e995deafbeeffb703cce829b648f25dfa8b45725bf33cb924e92849bcb19c89d9b7c09187ac1b4f2872a9a3f8d1bb930fae941eee72a5eb9e13e"
                     }
                   },
                   {
                     "timestamp": "2013-01-03T13:06:23.917000"
                     "hashes": {
                       "md5": "72395deafbeef6fab1e89fd6290300b3",
                       "sha1": "9d1c5671deadbeeff5ae9335e5764bb9aaae464a",
                       "sha512": "11a9fa3c3928edeafbeef3be97ef6d2df7876daa8ef859e8060c062eda6465b843192206186e832b2b414dc7b714d1f6a17eaa5f10abeeeec7540f9c9c46bb4a"
                     }
                   }
                 ]
               ],
               "hpfeed_ids": [
                 "50e5745cdfe0f70a59cf8d99"
               ]
             }
           ]
         }

   :query url_regex: PCRE regex which will be tried against the stored url (optional).
   :query limit: limit number of returned items (optional, default is 50).
   :statuscode 200: no error.
   :statuscode 400: Bad request.

Files
========