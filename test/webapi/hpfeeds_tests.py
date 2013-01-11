# Copyright (C) 2013 Johnny Vestergaard <jkv@unixcluster.dk>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

#make sure we can find bottle.py
import sys
sys.path.append('webapi/')

import bottle
import unittest
import uuid
from pymongo import MongoClient
from bottle import install, uninstall
from bottle.ext import mongo
from webapi.api import app
from datetime import datetime

from webtest import TestApp

from datetime import datetime

import json


class HPFeedsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls._dbname = str(uuid.uuid4())
        insert_data = []

        #alternate 1/2 on inserts
        for x in range(100):
            entry = {'channel': 'channel_{0}'.format(x % 2),
                     'ident': 'ident_{0}'.format(x % 2),
                     'payload': 'payload_{0}'.format(x % 2),
                     'timestamp': datetime.utcnow(),
                     'normalized': False}
            insert_data.append(entry)

        c = MongoClient('localhost', 27017)

        for item in insert_data:
            c[cls._dbname].hpfeed.insert(item)

        cls.sut = TestApp(app.app)

        for plug in bottle.app().plugins:
            if isinstance(plug, bottle.ext.mongo.MongoPlugin):
                uninstall(plug)

        plugin = bottle.ext.mongo.MongoPlugin(uri="localhost", db=cls._dbname, json_mongo=True)
        install(plugin)

    @classmethod
    def tearDownClass(cls):
        connection = MongoClient('localhost', 27017)
        connection.drop_database(cls._dbname)

    def test_count_no_query(self):
        """
        Test if default amount of entries are returned if no limiting parameter is used.
        """
        sut = HPFeedsTest.sut

        res = sut.get('/api/hpfeeds')
        result = json.loads(res.body)['hpfeeds']
        #API sets a default limit of 50
        self.assertEqual(50, len(result))

    def test_count_limit_query(self):
        """
        Test if correct amout of entries are returned when using the limit parameter.
        """
        sut = HPFeedsTest.sut

        for limit, expected in ((5, 5), (80, 80), (250, 100)):
            res = sut.get('/api/hpfeeds?limit={0}'.format(limit))
            result = json.loads(res.body)['hpfeeds']
            self.assertEqual(expected, len(result))

    def test_count_query_by_channel(self):
        """
        Test if correct number of entries are returned when filtering by channel name.
        """
        sut = HPFeedsTest.sut

        for limit, expected in (('trubadur', 0), ('channel_0', 50), ('channel_1', 50)):
            res = sut.get('/api/hpfeeds?channel={0}'.format(limit))
            result = json.loads(res.body)['hpfeeds']
            self.assertEqual(expected, len(result))

    def test_count_query_mixed_channel_limit(self):
        """
        Test if correct number of entries are returned when mixing filtering options.
        """
        sut = HPFeedsTest.sut

        #channel, limit, expected
        test_triplets = (
            ('nonexisting', 10, 0),
            ('channel_0', 100, 50),
            ('channel_1', 10, 10),
            ('channel_0', 100, 50),
            ('channel_1', 10, 10)
        )

        for channel, limit, expected in test_triplets:
            res = sut.get('/api/hpfeeds?channel={0}&limit={1}'.format(channel, limit))
            result = json.loads(res.body)['hpfeeds']
            self.assertEqual(expected, len(result))

    def test_content_query_channel(self):
        """
        Test if content is as expected.
        """
        sut = HPFeedsTest.sut

        #fetch all
        res = sut.get('/api/hpfeeds?limit=100')
        result = json.loads(res.body)['hpfeeds']

        for item in result:
            self.assertFalse(item['normalized'])
            #Check if we can parse without exception
            datetime.strptime(item['timestamp'], "%Y-%m-%dT%H:%M:%S.%f")

            if item['channel'] == 'channel_0':
                self.assertEqual('ident_0', item['ident'])
                self.assertEqual('payload_0', item['payload'])
            elif item['channel'] == 'channel_1':
                self.assertEqual('ident_1', item['ident'])
                self.assertEqual('payload_1', item['payload'])
            else:
                raise Exception('Unexpected channel name: {0}'.format(item['channel']))
