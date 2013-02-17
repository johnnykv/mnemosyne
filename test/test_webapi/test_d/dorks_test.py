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

class DorkTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmpdir =  tempfile.mkdtemp()
        cls._dbname = str(uuid.uuid4())
        insert_data = []

        #type, content, count, timestamp
        test_data = (
            ('inurl', '/jamesBond.php', 1, datetime(2011, 1, 1)),
            ('inurl', '/some/path', 2, datetime(2012, 2, 2)),
            ('inurl', '/no/fjords/here', 3, datetime(2013, 3, 3)),
            )

        for type_, content, count, timestamp in test_data:
            entry = {'type': type_,
                     'content': content,
                     'count': count,
                     'lasttime': timestamp}
            insert_data.append(entry)

        c = MongoClient('localhost', 27017)

        for item in insert_data:
            c[cls._dbname].dork.insert(item)

        cls.sut = helpers.prepare_app(cls._dbname, cls.tmpdir, 'a_all')

    @classmethod
    def tearDownClass(cls):
        connection = MongoClient('localhost', 27017)
        connection.drop_database(cls._dbname)
        if os.path.isdir(cls.tmpdir):
            shutil.rmtree(cls.tmpdir)

    def test_get_dorks(self):
        sut = DorkTest.sut

        res = sut.get('/aux/dorks')
        result = json.loads(res.body)['dorks']

        expected = [{'content': '/jamesBond.php', 'count': 1, 'type': 'inurl',
                     'timestamp': '2011-01-01T00:00:00'},
                    {'content': '/some/path', 'count': 2, 'type': 'inurl',
                     'timestamp': '2012-02-02T00:00:00'},
                    {'content': '/no/fjords/here', 'count': 3,
                     'type': 'inurl', 'timestamp': '2013-03-03T00:00:00'}]
        #TODO: Compare the actual output with expected
        self.assertEqual(len(expected), len(result))

    def test_get_dorks_with_regex(self):
        sut = DorkTest.sut

        res = sut.get('/aux/dorks?regex=/fjords/')
        result = json.loads(res.body)['dorks']

        #TODO: Compare the actual output with expected
        self.assertEqual(1, len(result))

    def test_get_dorks_with_limit(self):
        sut = DorkTest.sut

        res = sut.get('/aux/dorks?limit=2')
        result = json.loads(res.body)['dorks']

        #TODO: Compare the actual output with expected
        self.assertEqual(2, len(result))

    def test_get_dorks_with_known_type(self):
        sut = DorkTest.sut

        res = sut.get('/aux/dorks?type=inurl')
        result = json.loads(res.body)['dorks']

        #TODO: Compare the actual output with expected
        self.assertEqual(3, len(result))

    def test_get_dorks_with_unknown_type(self):
        sut = DorkTest.sut

        res = sut.get('/aux/dorks?type=stuff')
        result = json.loads(res.body)['dorks']

        #TODO: Compare the actual output with expected
        self.assertEqual(0, len(result))

    def test_get_dorks_sorted_default(self):
        """
        Test if dorks are sorted descending by count by default
        """
        sut = DorkTest.sut

        res = sut.get('/aux/dorks')
        result = json.loads(res.body)['dorks']

        self.assertEqual('/no/fjords/here', result[0]['content'])
        self.assertEqual('/some/path', result[1]['content'])
        self.assertEqual('/jamesBond.php', result[2]['content'])

    def test_get_dorks_sorted_ascending(self):
        """
        Tests ascending sorting when providing sort_order as parameter.
        """
        sut = DorkTest.sut

        res = sut.get('/aux/dorks?sort_order=1')
        result = json.loads(res.body)['dorks']

        self.assertEqual('/jamesBond.php', result[0]['content'])
        self.assertEqual('/some/path', result[1]['content'])
        self.assertEqual('/no/fjords/here', result[2]['content'])