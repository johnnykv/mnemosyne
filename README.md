Mnemosyne
=========
Mnemosyne has two main objectives:
1. Provide immutable persistence for [hpfeeds](hpfeeds https://redmine.honeynet.org/projects/hpfeeds/wiki).
2. Normalization of data to enable sensor agnostic analysis.
3. Expose the normalized data through a RESTful API.

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
