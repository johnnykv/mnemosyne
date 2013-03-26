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
import json
import os
import tempfile
import shutil

from pymongo import MongoClient

import helpers


class URLTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.mkdtemp()
        cls._dbname = str(uuid.uuid4())

        test_data = [{
                         "url": "http://herr-doctor.zz",

                         "extractions": [
                             {"hashes": {
                                 "md5": "10000000000000000000000000000md5",
                                 "sha1": "100000000000000000000000000000000000sha1",
                                 "sha512": "1000000000000000000000000000000000000000"
                                           "00000000000000000000000000000000000000000"
                                           "00000000000000000000000000000000000000000sha512"
                             },
                              "timestamp": "2013-03-16T19:12:51.279000"
                             },
                             {"hashes": {
                                 "md5": "20000000000000000000000000000md5",
                                 "sha1": "200000000000000000000000000000000000sha1",
                                 "sha512": "2000000000000000000000000000000000000000"
                                           "00000000000000000000000000000000000000000"
                                           "00000000000000000000000000000000000000000sha512"
                             },
                              "timestamp": "2013-02-16T19:12:51.279000"
                             }
                         ]
                     },
                     {
                         "url": "http://gerber.zz",

                         "extractions": [
                             {"hashes": {
                                 "md5": "30000000000000000000000000000md5",
                                 "sha1": "300000000000000000000000000000000000sha1",
                                 "sha512": "3000000000000000000000000000000000000000"
                                           "00000000000000000000000000000000000000000"
                                           "00000000000000000000000000000000000000000sha512"
                             },
                              "timestamp": "2013-03-16T19:12:51.279000"
                             },
                             {"hashes": {
                                 "md5": "10000000000000000000000000000md5",
                                 "sha1": "100000000000000000000000000000000000sha1",
                                 "sha512": "1000000000000000000000000000000000000000"
                                           "00000000000000000000000000000000000000000"
                                           "00000000000000000000000000000000000000000sha512"
                             },
                              "timestamp": "2013-02-16T19:12:51.279000"
                             }
                         ]
                     }
        ]

        c = MongoClient('localhost', 27017)

        for item in test_data:
            c[cls._dbname].url.insert(item)

        cls.sut = helpers.prepare_app(cls._dbname, cls.tmpdir, 'a_all')

    @classmethod
    def tearDownClass(cls):
        connection = MongoClient('localhost', 27017)
        connection.drop_database(cls._dbname)
        if os.path.isdir(cls.tmpdir):
            shutil.rmtree(cls.tmpdir)

    def test_md5_query(self):
        """
        Test if the correct URL's are returned when querying by md5 hash.
        """
        sut = URLTest.sut

        res = sut.get('/urls?hash=20000000000000000000000000000md5')
        result = json.loads(res.body)['urls']

        self.assertEquals('http://herr-doctor.zz', result[0]['url'])
        self.assertEquals(1, len(result))

    def test_sha1_query(self):
        """
        Test if the correct URL's are returned when querying by sha1 hash.
        """
        sut = URLTest.sut

        res = sut.get('/urls?hash=200000000000000000000000000000000000sha1')
        result = json.loads(res.body)['urls']
        self.assertEquals('http://herr-doctor.zz', result[0]['url'])
        self.assertEquals(1, len(result))

    def test_sha512_query(self):
        """
        Test if the correct URL's are returned when querying by sha512 hash.
        """
        sut = URLTest.sut

        res = sut.get("/urls?hash=2000000000000000000000000000000000000000"
                      "00000000000000000000000000000000000000000"
                      "00000000000000000000000000000000000000000sha512")
        result = json.loads(res.body)['urls']
        self.assertEquals('http://herr-doctor.zz', result[0]['url'])
        self.assertEquals(1, len(result))

    def test_query_with_multiple_results(self):
        """
        Tests if multiple URL's can be returned.
        """
        sut = URLTest.sut

        res = sut.get('/urls?hash=10000000000000000000000000000md5')
        result = json.loads(res.body)['urls']
        self.assertEquals(2, len(result))