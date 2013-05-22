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
from datetime import datetime

from normalizer.modules import conpot_events


class ConpotTest(unittest.TestCase):
    def test_session(self):
        """
        Test if a valid conpot json message get parsed as expected.
        """

        input_submission_time = datetime(2012, 12, 14, 12, 22, 51)
        input_string = "{\"data_type\":  \"modbus\", \"data\": [{\"request_pdu\": \"0300000002\", \"function_code\": 3, \"slave_id\": 1," \
                       "\"response_pdu\": \"030400000001\"}, {\"request_pdu\": \"0100000002\", \"function_code\": 1, " \
                       "\"slave_id\": 5, \"response_pdu\": \"010100\"}], \"remote\": [\"12.34.43.21\", 45358], " \
                       "\"session_id\": \"069db6a6-5faa-4f3a-8de0-ce90af0e7b2c\"}"

        expected_session = {
            'timestamp': datetime(2012, 12, 14, 12, 22, 51),
            'source_ip': '12.34.43.21',
            'source_port': 45358,
            'destination_port': 502,
            'honeypot': 'conpot',
            'protocol': 'modbus',
            'session_modbus':{ 'pdus':
                [
                    {'request_pdu': '0300000002', 'function_code': 3, 'slave_id': 1, 'response_pdu': '030400000001'},
                    {'request_pdu': '0100000002', 'function_code': 1, 'slave_id': 5, 'response_pdu': '010100'}
                ]
            }
        }

        expected_output = [{'session': expected_session},]

        sut = conpot_events.Conpot()
        result = sut.normalize(input_string, 'beeswarm.hive', input_submission_time)

        #test if we got the correct amount of root (document) items
        self.assertEqual(len(expected_output), len(result))
        #test if we got the correct amount of keys
        self.assertEqual(len(expected_output[0]), len(result[0]))
        self.assertEqual(expected_output[0]['session']['source_ip'], result[0]['session']['source_ip'])
        self.assertEqual(expected_output[0]['session']['source_port'], result[0]['session']['source_port'])
        self.assertEqual(expected_output[0]['session']['destination_port'], result[0]['session']['destination_port'])
        self.assertEqual(expected_output[0]['session']['honeypot'], result[0]['session']['honeypot'])
        self.assertEqual(expected_output[0]['session']['protocol'], result[0]['session']['protocol'])
        self.assertItemsEqual(expected_output[0]['session']['session_modbus']['pdus'],
                              result[0]['session']['session_modbus']['pdus'])