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
from normalizer.modules import kippo_events
from datetime import datetime


class KippoTests(unittest.TestCase):
    def test_session(self):
        """
        Test if a valid kippo json message get parsed as expected.
        """

        input_submission_time = datetime(2012, 12, 14, 12, 22, 51)
        input_string = """{\"peerIP\": \"223.5.23.53\", \"loggedin\": null, \"ttylog\": \"01babadeadbeef\", \"hostIP\": \"192.168.6.211\", \"peerPort\": 36868, \"version\": \"SSH-2.0-libssh-0.1\", \"hostPort\": 2222, \"credentials\": [[\"root\", \"123muie123\"]]}"""
        session_ssh = {'version': 'SSH-2.0-libssh-0.1'}

        auth_attempts = [{'login': 'root',
                          'password': '123muie123'}]

        attachments = [
                {
                    'description': "Kippo session log (ttylog).",
                    'data': '01babadeadbeef'
                }, ]

        session = {
            'timestamp': datetime(2012, 12, 14, 12, 22, 51),
            'source_ip': '1.2.3.4',
            'source_port': 36228,
            'destination_port': 2222,
            'honeypot': 'kippo',
            'protocol': 'ssh',
            'session_ssh': session_ssh,
            'auth_attempts': auth_attempts,
            'attachments': attachments
        }

        expected_output = [{'session': session}, ]

        sut = kippo_events.KippoEvents()
        result = sut.normalize(input_string, 'kippo.sessions', input_submission_time)

        #test if we got the correct amount of root (document) items
        self.assertEqual(len(expected_output), len(result))

        self.assertItemsEqual(expected_output[0]['session'], result[0]['session'])
        self.assertItemsEqual(expected_output[0]['session']['session_ssh'], result[0]['session']['session_ssh'])
        self.assertItemsEqual(expected_output[0]['session']['auth_attempts'], result[0]['session']['auth_attempts'])
        self.assertItemsEqual(expected_output[0]['session']['attachments'], result[0]['session']['attachments'])
