******
WebAPI
******

Versioning
==========
To maintain backwards compatibility the REST path will be prefixed with version numbers, a prefix of /api/d/ will serve the current unstable development api, whereas /api/v* will serve the specified stable version.

Examples:

**/api/v1/sessions**
   Sessions resource as it was defined in release 1.
**/api/v2/sessions**
   Sessions resource as it was defined in release 2.
**/api/d/sessions**
   Sessions resource under development.

Path conventions
================
To ensure a clean API, Mnemosyne has the following conventions for URL construction:

1. If the consumer has filtering options use query strings.
2. If the consumer has no options in regards to filtering use a clean path.

Access levels
=========================

=====   ===========
Level   Description
=====   ===========
100     Administrator
70      Access to all data, including raw hpfeeds store
60      Access to normalized data where IP of honeypots has been removed.
10      Public access to basic sanitized data. (Example: Dorks service for glastopf)
=====   ===========

Resources as of version 1
=========================

HPFeeds
*******
The HPFeeds resource located at /api/v1/hpfeeds serves unparsed data from various HPFeed channels.

.. http:get:: /api/v1/hpfeeds

   Returns filtered HPFeeds data.

   **Example request**:

   .. sourcecode:: http

      GET /api/v1/hpfeeds?channel=glastopf.events HTTP/1.1
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


   :query id: hpfeed's unique id (optional).
   :query channel: channel name (optional).
   :query limit: limit number of returned items (optional, default is 50).
   :statuscode 200: no error.
   :statuscode 400: Bad request.

HPFeeds statistics
******************
The HPFeeds statistics resources is a subresource and is located at /api/v1/hpfeeds/stats.
.. http:get:: /api/v1/hpfeeds/stats

   Returns a collection of hourly counts for one or more HPFeeds channels.

   **Example request**:

   .. sourcecode:: http

      GET /api/v1/hpfeeds/stats?channel=dionaea.capture HTTP/1.1
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {'stats':
       [
        {'hourly': {'12': 1, '13': 2}, 'date': '20130906', 'channel': 'dionaea.capture'},
        {'hourly': {'13': 115, '12': 1978}, 'date': '20130907', 'channel': 'dionaea.capture'}
       ]
      }


   :query channel: channel name.
   :query date: limit query to an specific date, format: YYYYMMDD, example: 20131230.
   :statuscode 200: no error.
   :statuscode 400: Bad request.

.. http:get:: /api/v1/hpfeeds/stats/total

   Returns the total count for every received channel name.

   **Example request**:

   .. sourcecode:: http

      GET /api/v1/hpfeeds/stats/total HTTP/1.1
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {'stats':
       [
        {'channel': 'dionaea_capture', 'count': 22},
        {'channel': 'mwbinary_dionaea_sensorunique', 'count': 1}
       ]
      }


   :statuscode 200: no error.
   :statuscode 400: Bad request.



Sessions
********
The Sessions resource located at /api/v1/sessions contains normalized data from traditional serverside honeypots.

.. http:get:: /api/v1/sessions

   Returns sessions filtered by query parameters.

   **Example request**:

   .. sourcecode:: http

       GET /api/v1/sessions?honeypot=kippo&source_port=36888 HTTP/1.1
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

   :query id: unique identifer (optional).
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
****
The URLS resource located at /urls, contains urls which potentially are serving malicious content.

.. http:get:: /api/v1/urls

   Returns urls serving potential malicious content. If any files has been extracted, an reference to the checksum will be provided.

   **Example request**:

   .. sourcecode:: http

         GET /api/v1/urls?url_regex=\.ru(\/|\:|$) HTTP/1.1
         Host: example.com
         Accept: application/json

   **Example response**:

   .. sourcecode:: http

         HTTP/1.1 200 OK
         Content-Type: application/json

         {
          "urls": [
            {
              "url": "http://ikbyznod.ru/count26.php",
              "_id": "50ec7f6fc1512da84f113386",
              "extractions": [
                {
                  "timestamp": "2012-12-26T13:51:13.507000",
                  "hashes": {
                    "md5": "549eccb6939274ac9664f0201e4771c4",
                    "sha1": "d337b47020b1e214d35b044483bf04ae1f0a7b4d",
                    "sha512": "53ece48162e635bd93ea3240c12b4a844974de0a75f3b30da1f18f8e2892c10a9930a2380673afd4521083b9f952a10b3c54de3be477ab1f11c61a8902c0d435"
                  }
                }
              ],
              "hpfeeds_ids": [
                "50da8260dfe0f7b2c68c2fde"
              ]
            },
            {
              "url": "http://www.ajy-aa.xx/images/M_images/t?%0D?",
              "_id": "50ec7f70c1512da84f113387",
              "hpfeeds_ids": [
                "50dad02bdfe0f7b4f48cd434",
                "50dad0a6dfe0f7b4f48cd435"
              ]
            },
            {
              "url": "http://www.xxyycatab.com.qq",
              "_id": "50ec7f70c1512da84f113388",
              "hpfeeds_ids": [
                "50dada38dfe0f7b53ceb8383"
              ]
            }
          ]
         }

   :query url_regex: PCRE regex which will be tried against the stored url (optional).
   :query hash: returns URL's where the files with the specified HASH has been downloaded (optional).
   :query limit: limit number of returned items (optional, default is 50).
   :statuscode 200: no error.
   :statuscode 400: Bad request.

Files
*****
The Files resource located at /api/v1/files contains various forms of binaries and code samples collected from HPFeeds channels.

.. http:get:: /api/v1/files

   Returns matches for the given hash. The following hashes are supported: MD5, SHA1, SHA512

   **Example request**:

   .. sourcecode:: http

       GET /api/v1/files?hash=549eccb6939274ac9664f0201e4771c4 HTTP/1.1
       Host: example.com
       Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

       HTTP/1.1 200 OK
       Content-Type: application/json

         {
           "files": [
             {
               "_id": "50e5e440cfd26d1f23bfe7b7",
               "content_guess": "Javascript",
               "data": "0a0909090909706172656e742e6c6f636174696f6e2e68726566203d2022687474703a2f2f736f6e617464616e69736d616e6c696b2e636f6d2f6d61696e6c792e68746d6c223b0a09090909",
               "encoding": "hex",
               "hashes": {
                 "md5": "549eccb6939274ac9664f0201e4771c4",
                 "sha1": "d337b47020b1e214d35b044483bf04ae1f0a7b4d",
                 "sha512": "53ece48162e635bd93ea3240c12b4a844974de0a75f3b30da1f18f8e2892c10a9930a2380673afd4521083b9f952a10b3c54de3be477ab1f11c61a8902c0d435"
               },
               "hpfeed_ids": [
                 "50da8260dfe0f7b2c68c2fde"
               ]
             }
           ]
         }

   :query hash: SHA1, SHA51 or MD5 digest (required).
   :query no_data: If present the 'data' field will not be returned (optional).
   :statuscode 200: no error.
   :statuscode 400: Bad request.

.. http:get:: /api/v1/aux/dorks

   Serves Dorks collected by Glastopf.

   **Example request**:

   .. sourcecode:: http

       GET /api/v1/aux/dorks HTTP/1.1
       Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
       "dorks": [
        {
         "content": "/pivotx/includes/index.php",
         "count": 716,
         "firsttime": "2013-02-01T20:38:42+00:00",
         "lasttime": "2013-01-14T16:20:51.504000",
         "type": "inurl"
        },
        {
         "content": "/axis-cgi/mjpg/wp-content/themes/diner/timthumb.php",
         "count": 545,
         "firsttime": "2013-02-01T20:38:32+00:00",
         "lasttime": "2013-01-14T16:26:03.036000",
         "type": "inurl"
        },
        {
         "content": "/board/board/include/pivotx/includes/wp-content/pivotx/includes/timthumb.php",
         "count": 493,
         "firsttime": "2013-02-01T20:39:03+00:00",
         "lasttime": "2013-01-14T10:55:50.197000",
         "type": "inurl"
        },

        <--- SNIP --- >

         ]
       }