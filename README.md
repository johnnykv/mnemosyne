Mnemosyne
=========
## About
Mnemosyne has three main objectives:

1. Provide immutable persistence for [hpfeeds](https://redmine.honeynet.org/projects/hpfeeds/wiki).
2. Normalization of data to enable sensor agnostic analysis.
3. Expose the normalized data through a RESTful API.

## Channels
Mnemosyne currently supports normalization of data from the following channels:

* dionaea.capture
* mwbinary.dionaea.sensorunique
* kippo.sessions
* glastopf.events
* glastopf.files
* thug.events (limited - still under development)

## Preliminary REST API
### Unormalized data
*GET /hpfeeds*
```json
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
    }]
}
```

*GET /hpfeeds/\<hpfeed_id\>*
```json
{
    "ident": "2l3if@hp8",
    "timestamp": "2012-12-26T19:49:22.212000",
    "normalized": true,
    "_id": "50dbdeadbeeff7b874e806ba",
    "payload": "<payload>",
    "channel": "glastopf.events"
}
```
### Normalized data
*GET /sessions/\<session_id\>*
```json
{
    "_id": "50db96f9dfe0f7aacb57c7af",
    "protocol": "http",
    "hpfeed_id": "50da20b2dfe0f7b0b5fb37d1",
    "timestamp": "2012-12-25T15:52:45",
    "source_ip": "123.123.222.21",
    "source_port": 57462,
    "destination_port": 80,
    "honeypot": "Glastopf",
    "session_http": {
        "request": {
            "body": "",
            "header": "{\"Accept-Language\": \"en-gb,en;q=0.5\", \"Proxy-Connection\": \"Keep-Alive\", \"Accept\": \"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\", \"User-Agent\": \"Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.28) Gecko/20120306 Firefox/3.6.28 (.NET CLR 3.5.30729)\", \"Accept-Charset\": \"ISO-8859-1,utf-8;q=0.7,*;q=0.7\", \"Host\": \"kratlusker.zz\", \"Pragma\": \"no-cache\", \"Cache-Control\": \"no-cache\", \"Accept-Encoding\": \"deflate, gzip\"}",
            "host": "kratluster.zz",
            "verb": "GET",
            "url": "http://kratlusker.zz/page.php?id='"
        }
    }
}
```
*GET /sessions/protocol/ssh
```json
{
  "sessions": [
    {
      "protocol": "ssh",
      "hpfeed_id": "50dc4537dfe0f7bf93d06080",
      "timestamp": "2012-12-27T12:55:19.317000",
      "source_ip": "111.222.111.18",
      "session_ssh": {
        "version": "SSH-2.0-libssh-0.1"
      },
      "source_port": 48418,
      "destination_port": 2222,
      "_id": "50e3f666dfe0f7e295f37815",
      "honeypot": "Kippo",
      "auth_attempts": [
        {
          "login": "root",
          "password": "massymo002"
        }
      ]
    },
    {
      "protocol": "ssh",
      "hpfeed_id": "50dc453bdfe0f7bf93d06081",
      "timestamp": "2012-12-27T12:55:23.073000",
      "source_ip": "111.222.111.18",
      "session_ssh": {
        "version": "SSH-2.0-libssh-0.1"
      },
      "source_port": 49478,
      "destination_port": 2222,
      "_id": "50e3f666dfe0f7e295f37816",
      "honeypot": "Kippo",
      "auth_attempts": [
        {
          "login": "cgi",
          "password": "florici123"
        }
      ]
    }
  ]
}
<
```
*GET /sessions/protocols*
```json
{"protocols": [{"count": 680, "protocol": "http"},
               {"count": 125, "protocol": "ssh"},
               {"count": 74,  "protocol": "imap"},
               {"count": 51922, "protocol": "microsoft-ds"]}
```

*GET /urls*
```json
{
  "urls": [
    {
      "_id": "50e233b700b0c57966791074",
      "url": "http://111.222.111.222:5397/jihrao",
      "extractions": [
        [
          {
            "timestamp": "2012-12-29T00:07:39.197000",
            "hashes": {
              "sha512": "<cut...>",
              "md5": "gg5673fac780251q8083e688c7c381cd"
            }
          }
        ],
        [
          {
            "timestamp": "2012-12-29T00:07:51.789000",
            "hashes": {
              "sha512": "<cut...>",
              "md5": "595113fac780251f8083e688c7c381cd"
            }
          }
        ]
      ]
    },
    {
      "_id": "50e233b700b0c57966791085",
      "url": "http://trobadur.xx:80/goodstuff",
      "extractions": [
        [
          {
            "timestamp": "2012-12-29T00:07:52.703000",
            "hashes": {
              "sha512": "<cut...>",
              "md5": "11530fdeba56bc1230d7a87813dbae53"
            }
          }
        ]
      ]
    }
  ]
}
```
*GET /file/755c4f9270db48f51f601638d2c4b4b0* (accepts md5, sha1 and sha512)
```json
{
  "files": [
    {
      "_id": "49e0a833df590d436f91da4d",
      "hpfeed_id": "50e0882cdf590d436f91b389",
      "encoding": "base64",
      "hashes": {
        "sha1": "9ed97ccdd683aa8842a5473315e8b45bda168556",
        "sha512": "bb1d9c92a7cdc8dbd61365c5d757729a2c8d131fb5f49da3e4a6818635f5e8eb40a2bf06e9a25a069b618d934c53b367f3327a37b65c50e66d60580ee178a135",
        "md5": "755c4f9270db48f51f601638d2c4b4b0"
      },
      "data": "<cut....>",
      "hpfeed_ids": [
        "50e08833df590d436f91dc4d",
        "50e08848df590d436f91fe35",
        "50e0884bdf590d436f91fe3d",
        "50e08864df590d436f91feaf",
        "50e08866df590d436f91febe",
        "50e0886fdf590d436f91feea",
        "50e08870df590d436f91fef0",
        "50e08890df590d436f91ffa1",

      ]
    }
  ]
}

