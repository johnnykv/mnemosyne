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


class FilesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.mkdtemp()
        cls._dbname = str(uuid.uuid4())

        test_data = [{
                         "content_guess": "PE32 executable (DLL) (GUI) Intel 80386, for MS Windows, UPX compressed",
                         "data": "deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
                         "encoding": "hex",
                         "hashes": {
                             "md5": "10000000000000000000000000000md5",
                             "sha1": "100000000000000000000000000000000000sha1",
                             "sha512": "1000000000000000000000000000000000000000"
                                       "00000000000000000000000000000000000000000"
                                       "00000000000000000000000000000000000000000sha512"
                         },
                         "hpfeed_ids": [
                             "10f3e41b09ce4533629cea00"
                         ]
                     },
                     {
                         "content_guess": "PE32 executable (DLL) (GUI) Intel 80386, for MS Windows, UPX compressed",
                         "data": "deadb33fdeadb33fdeadb33fdeadb33fdeadb33fdeadb33fdeadb33f",
                         "encoding": "hex",
                         "hashes": {
                             "md5": "20000000000000000000000000000md5",
                             "sha1": "200000000000000000000000000000000000sha1",
                             "sha512": "200000000000000000000000000000000000000"
                                       "000000000000000000000000000000000000000"
                                       "00000000000000000000000000000000000000000000sha512"
                         },
                         "hpfeed_ids": [
                             "20f3e41b09ce4533629cea00"
                         ]
                     }]

        c = MongoClient('localhost', 27017)

        for item in test_data:
            c[cls._dbname].file.insert(item)

        cls.sut = helpers.prepare_app(cls._dbname, cls.tmpdir, 'a_all')

    @classmethod
    def tearDownClass(cls):
        connection = MongoClient('localhost', 27017)
        connection.drop_database(cls._dbname)
        if os.path.isdir(cls.tmpdir):
            shutil.rmtree(cls.tmpdir)

    def test_md5_query(self):
        """
        Test if the correct data is returned when querying files bu md5 hash.
        """
        sut = FilesTests.sut

        res = sut.get('/files?hash=10000000000000000000000000000md5')
        result = json.loads(res.body)['files'][0]
        self.assertEquals('deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef', result['data'])

    def test_sha1_query(self):
        """
        Test if the correct data is returned when querying files bu md5 hash.
        """
        sut = FilesTests.sut

        res = sut.get('/files?hash=1000000000000000000000000000000000000000'
                      '00000000000000000000000000000000000000000'
                      '00000000000000000000000000000000000000000sha512')
        result = json.loads(res.body)['files'][0]
        self.assertEquals('deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef', result['data'])

    def test_sha512_query(self):
        """
        Test if the correct data is returned when querying files bu md5 hash.
        """
        sut = FilesTests.sut

        res = sut.get('/files?hash=10000000000000000000000000000md5')
        result = json.loads(res.body)['files'][0]
        self.assertEquals('deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef', result['data'])

    def test_no_data_query(self):
        """
        Test to verify that the 'data' field is not returned when queried with no_data.
        """
        sut = FilesTests.sut

        res = sut.get('/files?hash=10000000000000000000000000000md5&no_data')
        result = json.loads(res.body)['files'][0]
        self.assertTrue('data' not in result)
        self.assertEquals('PE32 executable (DLL) (GUI) Intel 80386, for MS Windows, UPX compressed',
                          result['content_guess'])

