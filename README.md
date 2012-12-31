Mnemosyne
=========
Mnemosyne has three main objectives:

1. Provide immutable persistence for [hpfeeds](https://redmine.honeynet.org/projects/hpfeeds/wiki).
2. Normalization of data to enable sensor agnostic analysis.
3. Expose the normalized data through a RESTful API.

## Preliminary REST API
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

*GET /session/\<session_id\>*
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
            "host": "gameframe.net",
            "verb": "GET",
            "url": "http://kratlusker.zz/page.php?id='"
        }
    }
}
```

*GET /sessions/protocols*
```json
{"protocols": [{"count": 680, "protocol": "http"},
               {"count": 125, "protocol": "ssh"},
               {"count": 74,  "protocol": "imap"}]}
```

*GET /urls*
```json
{
"urls": [
    {
        "url": "http://inutterod.ru/count22.php",
        "_id": "50db96fa2c533872c1ba0d26",
        "hpfeed_ids": [
            "50da8260dfe0f7b2c68c2fde"
        ]
    },
    {
        "url": "http://www.jotto-to.xx/images/M_images/t?%0D?",
        "_id": "50db96fa2c533872c1ba0d27",
        "hpfeed_ids": [
            "50dad02bdfe0f7b4f48cd434",
            "50dad0a6dfe0f7b4f48cd435"
        ]
    }
}
```
*GET /file/755c4f9270db48f51f601638d2c4b4b0* (accepts md5, sha1 and sha512)
```json
{
  "files": [
    {
      "hpfeed_id": "50e0882cdf590d436f91b389",
      "encoding": "base64",
      "hashes": {
        "sha1": "9ed97ccdd683aa8842a5473315e8b45bda168556",
        "sha512": "bb1d9c92a7cdc8dbd61365c5d757729a2c8d131fb5f49da3e4a6818635f5e8eb40a2bf06e9a25a069b618d934c53b367f3327a37b65c50e66d60580ee178a135",
        "md5": "755c4f9270db48f51f601638d2c4b4b0"
      },
      "_id": "bb1d9c92a7cdc8dbd61365c5d757729a2c8d131fb5f49da3e4a6818635f5e8eb40a2bf06e9a25a069b618d934c53b367f3327a37b65c50e66d60580ee178a135",
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
        "50e08892df590d436f91ffa7",
        "50e0889adf590d436f91ffda",
        "50e0889cdf590d436f91ffea",
        "50e088b9df590d436f92006e",
        "50e088badf590d436f920074",
        "50e088cadf590d436f9200b5",
        "50e088cddf590d436f9200cc",
        "50e088cfdf590d436f9200e4",
        "50e088d1df590d436f9200ec",
        "50e088ecdf590d436f920177",
        "50e088eedf590d436f92017b",
        "50e08908df590d436f9201e4",
        "50e0890adf590d436f9201f4"
      ]
    }
  ]
}



### Sample console output
```
2012-12-21 23:14:54,804 (connect) connecting to hpfeeds.honeycloud.net:10000
2012-12-21 23:14:54,811 (insert_normalized) Inserting normalized item origination from hpfeeds with id: 1
2012-12-21 23:14:54,876 (connect) info message name: @hp2, rand: '7\x004\xe3'
2012-12-21 23:15:08,187 (on_message) Persisted message from glastopf.events (payload size: 10566)
2012-12-21 23:15:09,816 (insert_normalized) Inserting normalized item origination from hpfeeds with id: 2
2012-12-21 23:15:51,402 (on_message) Persisted message from glastopf.events (payload size: 9885)
2012-12-21 23:15:51,486 (on_message) Persisted message from glastopf.events (payload size: 9863)
2012-12-21 23:15:52,427 (on_message) Persisted message from glastopf.events (payload size: 10343)
2012-12-21 23:15:52,541 (on_message) Persisted message from glastopf.events (payload size: 9102)
2012-12-21 23:15:54,847 (insert_normalized) Inserting normalized item originating from hpfeeds with id: 3
2012-12-21 23:15:54,855 (insert_normalized) Inserting normalized item originating from hpfeeds with id: 4
2012-12-21 23:15:54,861 (insert_normalized) Inserting normalized item originating from hpfeeds with id: 5
2012-12-21 23:15:54,866 (insert_normalized) Inserting normalized item originating from hpfeeds with id: 6
```
