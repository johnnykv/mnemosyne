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
from normalizer.modules import beeswarm_hive
from datetime import datetime


class BeeswarnHiveTest(unittest.TestCase):
    def test_session(self):
        """
        Test if a valid beeswarm json message get parsed as expected.
        """

        input_submission_time = datetime(2012, 12, 14, 12, 22, 51)
        input_string = "{\"honey_ip\": \"111.222.222.111\", \"attacker_ip\": \"123.123.123.123\", \"login_attempts\": [{\"username\": \"james\", \"timestamp\": \"2013-02-20T15:02:25.228523\", \"password\": \"bond\"}, {\"username\": \"a\", \"timestamp\": \"2013-02-20T15:02:27.467429\", \"password\": \"s\"}, {\"username\": \"wokka\", \"timestamp\": \"2013-02-20T15:02:27.804439\", \"password\": \"wokka\"}], \"honey_port\": 23, \"timestamp\": \"2013-02-20T15:02:23.432581\", \"attacker_source_port\": 56982, \"id\": \"f2deccc8-0395-488c-87a1-b40850f8aa78\", \"protocol\": \"telnet\"}"


        auth_attempts = [{'login': 'james',
                          'password': 'bond'},
                         {'login': 'a',
                          'password': 's'},
                         {'login': 'wokka',
                          'password': 'wokka'}]

        session = {
            'timestamp': datetime(2012, 12, 14, 12, 22, 51),
            'source_ip': '123.123.123.123',
            'source_port': 56982,
            'destination_port': 23,
            'destination_ip': '111.222.222.111',
            'honeypot': 'beeswarm.hive',
            'protocol': 'telnet',
            'auth_attempts': auth_attempts,
        }

        expected_output = [{'session': session}, ]

        sut = beeswarm_hive.BeeswarmHive()
        result = sut.normalize(input_string, 'beeswarm.hive', input_submission_time)

        #test if we got the correct amount of root (document) items
        self.assertEqual(len(expected_output), len(result))
        self.assertItemsEqual(expected_output[0]['session'], result[0]['session'])
        self.assertItemsEqual(expected_output[0]['session']['auth_attempts'], result[0]['session']['auth_attempts'])
