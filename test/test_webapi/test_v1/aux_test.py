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
import os
import tempfile
import shutil
from pymongo import MongoClient
from datetime import datetime

import json


class AuxTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmpdir =  tempfile.mkdtemp()
        cls._dbname = str(uuid.uuid4())
        insert_data = []

        #TODO: Generate larger dataset
        day_channel_pairs = (
            (1, 'channel_1'),
            (1, 'channel_1'),
            (1, 'channel_2'),
            (2, 'channel_3'),
            (2, 'channel_1'),
            (3, 'channel_1')
            )

        for day, channel in day_channel_pairs:
            entry = {'channel': '{0}'.format(channel),
                     'ident': 'dummy_ident',
                     'payload': 'dummy_payload',
                     'timestamp': datetime.strptime(str(day), '%j').replace(year=2013),
                     'normalized': False}
            insert_data.append(entry)

        c = MongoClient('localhost', 27017)

        for item in insert_data:
            c[cls._dbname].hpfeed.insert(item)

        cls.sut = helpers.prepare_app(cls._dbname, cls.tmpdir, 'access_all')

    @classmethod
    def tearDownClass(cls):
        connection = MongoClient('localhost', 27017)
        connection.drop_database(cls._dbname)
        if os.path.isdir(cls.tmpdir):
            shutil.rmtree(cls.tmpdir)

    def test_get_hpfeed_stats(self):
        sut = AuxTest.sut

        res = sut.get('/aux/get_hpfeeds_stats')
        result = json.loads(res.body)['result']

        expected = [{'date': u'2013-01-01T00:00:00', 'count': 3},
                    {'date': u'2013-01-02T00:00:00', 'count': 2},
                    {'date': u'2013-01-03T00:00:00', 'count': 1}]

        self.assertItemsEqual(expected, result)

    def test_get_hpfeed_channels(self):
        sut = AuxTest.sut

        res = sut.get('/aux/get_hpfeeds_channels')
        result = json.loads(res.body)['channels']

        expected = [{'channel': 'channel_1', 'count': 4},
                    {'channel': 'channel_2', 'count': 1},
                    {'channel': 'channel_3', 'count': 1}]

        self.assertItemsEqual(expected, result)
