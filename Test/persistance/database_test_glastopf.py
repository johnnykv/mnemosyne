# Copyright (C) 2012 Johnny Vestergaard <jkv@unixcluster.dk>
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
import tempfile
import os
from persistance import database
from datetime import datetime
from copy import deepcopy


class DatabaseTests(unittest.TestCase):
    def test_glastopf_insert(self):
        """
        Test inseration of a valid and normalized Glastopf entry.
        This test only checks if the specified data can be inserted without exceptions
        """

        tmp_db = tempfile.mktemp()
        try:
            sut = database.Database('sqlite:///' + tmp_db)
            sut.insert_normalized(deepcopy(DatabaseTests.glastopf_valid_input_1), 1)
        finally:
            if os.path.isfile(tmp_db):
                os.remove(tmp_db)

    def test_glastopf_two_inserts_same_url(self):
        """
        Test inseration of a valid and normalized Glastopf entry.
        This test only checks if the specified data can be inserted without exceptions
        """

        tmp_db = tempfile.mktemp()
        try:
            sut = database.Database('sqlite:///' + tmp_db)
            sut.insert_normalized(deepcopy(DatabaseTests.glastopf_valid_input_1), 1)
            sut.insert_normalized(deepcopy(DatabaseTests.glastopf_valid_input_1), 1)
        finally:
            if os.path.isfile(tmp_db):
                os.remove(tmp_db)

    glastopf_valid_input_1 = {'session':
                             {
                              'timestamp': datetime(2012, 12, 14, 12, 22, 51),
                              'source_ip': '1.2.3.4',
                              'source_port': 49111,
                              'destination_port': 80,
                              'session_type': 'http',
                              'session_http':
                             {
                                 'host': 'www.something.com',
                                 'header': '{"Accept-Language": "en-US", "Accept-Encoding": "gzip", "Connection": "close", "Accept": "*/*", "User-Agent": "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)", "Host": "www.something.com"}',
                                 'body': '',
                                 'verb': 'GET',
                                 'url':
                             {
                                 'url': 'http://www.something.com/someURL?a=b',
                                 'scheme': 'http',
                                 'netloc': 'www.something.com',
                                 'path': '/someURL',
                                 'query': 'a=b',
                                 'params': '',
                                 'fragment': ''
                             }
                             },
                             },
    }
