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


import unittest
import uuid
import helpers
import json
import os
import tempfile
import shutil
from pymongo import MongoClient
from datetime import datetime


class HPFeedsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.mkdtemp()
        cls._dbname = str(uuid.uuid4())
        hpfeeddata = []

        #alternate 1/2 on inserts
        for x in range(100):
            entry = {'channel': 'channel_{0}'.format(x % 2),
                     'ident': 'ident_{0}'.format(x % 2),
                     'payload': 'payload_{0}'.format(x % 2),
                     'timestamp': datetime.utcnow(),
                     'normalized': False}
            hpfeeddata.append(entry)

        c = MongoClient('localhost', 27017)

        for item in hpfeeddata:
            c[cls._dbname].hpfeed.insert(item)

        daily_stats = [
            {'date': '20130906',
             'channel': 'dionaea.capture',
             'hourly': {
                 '12': 1,
                 '13': 2
             }
            },
            {

                'date': '20130907',
                'channel': 'dionaea.capture',
                'hourly': {
                    '12': 1978,
                    '13': 115
                }
            },
            {
                'date': '20130907',
                'channel': 'mwbinary.dionaea.sensorunique',
                'hourly': {
                    '12': 28,
                    '13': 2
                }
            },
            {
                'date': '20130907',
                'channel': 'glastopf.events',
                'hourly': {
                    '12': 109,
                    '13': 2
                }
            },
            {'date': '20130907',
             'channel': 'beeswarm.hive',
             'hourly': {'12': 13, '13': 1}},
            {
            '_id': 'total',
            'dionaea_capture' : 22,
            'mwbinary_dionaea_sensorunique' : 1
}
        ]

        for item in daily_stats:
            c[cls._dbname].daily_stats.insert(item)

        cls.sut = helpers.prepare_app(cls._dbname, cls.tmpdir, 'a_all')

    @classmethod
    def tearDownClass(cls):
        connection = MongoClient('localhost', 27017)
        connection.drop_database(cls._dbname)
        if os.path.isdir(cls.tmpdir):
            shutil.rmtree(cls.tmpdir)

    def test_count_no_query(self):
        '''
        Test if default amount of entries are returned if no limiting parameter is used.
        '''
        sut = HPFeedsTest.sut

        res = sut.get('/hpfeeds')
        result = json.loads(res.body)['hpfeeds']
        #API sets a default limit of 50
        self.assertEqual(50, len(result))

    def test_count_limit_query(self):
        '''
        Test if correct amout of entries are returned when using the limit parameter.
        '''
        sut = HPFeedsTest.sut

        for limit, expected in ((5, 5), (80, 80), (250, 100)):
            res = sut.get('/hpfeeds?limit={0}'.format(limit))
            result = json.loads(res.body)['hpfeeds']
            self.assertEqual(expected, len(result))

    def test_count_query_by_channel(self):
        '''
        Test if correct number of entries are returned when filtering by channel name.
        '''
        sut = HPFeedsTest.sut

        for limit, expected in (('trubadur', 0), ('channel_0', 50), ('channel_1', 50)):
            res = sut.get('/hpfeeds?channel={0}'.format(limit))
            result = json.loads(res.body)['hpfeeds']
            self.assertEqual(expected, len(result))

    def test_count_query_mixed_channel_limit(self):
        '''
        Test if correct number of entries are returned when mixing filtering options.
        '''
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
            res = sut.get('/hpfeeds?channel={0}&limit={1}'.format(channel, limit))
            result = json.loads(res.body)['hpfeeds']
            self.assertEqual(expected, len(result))

    def test_content_query_channel(self):
        '''
        Test if content is as expected.
        '''
        sut = HPFeedsTest.sut

        #fetch all
        res = sut.get('/hpfeeds?limit=100')
        result = json.loads(res.body)['hpfeeds']

        for item in result:
            self.assertFalse(item['normalized'])
            #Check if we can parse without exception
            datetime.strptime(item['timestamp'], '%Y-%m-%dT%H:%M:%S.%f')

            if item['channel'] == 'channel_0':
                self.assertEqual('ident_0', item['ident'])
                self.assertEqual('payload_0', item['payload'])
            elif item['channel'] == 'channel_1':
                self.assertEqual('ident_1', item['ident'])
                self.assertEqual('payload_1', item['payload'])
            else:
                raise Exception('Unexpected channel name: {0}'.format(item['channel']))

    def test_get_stats_query_date_query_channel(self):
        '''
        Tests if the correct data is returned when querying a specific combination of date and channel name
        '''

        sut = HPFeedsTest.sut

        res = sut.get('/hpfeeds/stats?date=20130907&channel=dionaea.capture')
        result = json.loads(res.body)
        expected = {'stats': [{'date': '20130907', 'channel': 'dionaea.capture',
                               'hourly': {'12': 1978, '13': 115}}]}

        self.assertDictEqual(result, expected)

    def test_get_stats_specific_date(self):
        '''
        Tests if the correct data is returned when querying a specific date
        '''

        sut = HPFeedsTest.sut
        res = sut.get('/hpfeeds/stats?date=20130907')
        result = json.loads(res.body)

        expected = {'stats': [{'hourly': {'13': 115, '12': 1978}, 'date': '20130907', 'channel': 'dionaea.capture'},
                              {'hourly': {'13': 2, '12': 28}, 'date': '20130907',
                               'channel': 'mwbinary.dionaea.sensorunique'},
                              {'hourly': {'13': 2, '12': 109}, 'date': '20130907', 'channel': 'glastopf.events'},
                              {'hourly': {'13': 1, '12': 13}, 'date': '20130907', 'channel': 'beeswarm.hive'}]}

        self.assertDictEqual(result, expected)

    def test_get_stats_specific_channel(self):
        '''
        Tests if the correct data is returned when querying a specific channel
        '''
        self.maxDiff = 9999
        sut = HPFeedsTest.sut

        res = sut.get('/hpfeeds/stats?channel=dionaea.capture')
        result = json.loads(res.body)
        expected = {'stats': [{'hourly': {'12': 1, '13': 2}, 'date': '20130906', 'channel': 'dionaea.capture'},
                              {'hourly': {'13': 115, '12': 1978}, 'date': '20130907', 'channel': 'dionaea.capture'}]}

        self.assertDictEqual(result, expected)

    def test_get_stats_total(self):
        '''
        Tests if counts and channel names are summarized correctly.
        '''

        expected = {'stats':
                        [{'channel': 'dionaea_capture', 'count': 22},
                         {'channel': 'mwbinary_dionaea_sensorunique', 'count': 1}
                        ]}

        sut = HPFeedsTest.sut

        res = sut.get('/hpfeeds/stats/total')
        result = json.loads(res.body)

        self.assertDictEqual(result, expected)
