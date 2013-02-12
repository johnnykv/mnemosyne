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
import os
import base64
from datetime import datetime
from normalizer.modules import thug_files


class ThugFilesTest(unittest.TestCase):
    def test_channels(self):
        """
        Test that the channel variable exists.
        """
        self.assertTrue(thug_files.ThugFiles.channels)

    def test_event(self):
        """
        Test extraction of binary from thug.files
        """
        input_string = open(os.path.dirname(__file__) + '/data_samples/thug_files_sample1.txt', 'r').read()

        dt = datetime.now()


        sut = thug_files.ThugFiles()
        actual = sut.normalize(input_string, 'thug.files', dt)
        #the result must contain exactly one dictionaries
        self.assertEqual(1, len(actual))
        actual_url = actual[0]['url']
        actual_file = actual[0]['file']

        #check returned url dictionary
        #{'url': 'http://xxx.yyy.com/links/came_one_taking-others.php',
        # 'extractions': [{'hashes': {
        #     'md5': '6478baaaef1fea99d1c4520ec2d30002',
        #     'sha1': '3d44fc9b69f221b28b69b8904fa8a65686a7accb',
        #     'sha512': '123'},
        #                  'timestamp': dt}]}

        self.assertEqual('http://xxx.yyy.com/links/came_one_taking-others.php', actual_url['url'])
        self.assertEquals(1, len(actual_url['extractions']))
        self.assertEquals('6478baaaef1fea99d1c4520ec2d30002', actual_url['extractions'][0]['hashes']['md5'])
        self.assertEquals('3d44fc9b69f221b28b69b8904fa8a65686a7accb', actual_url['extractions'][0]['hashes']['sha1'])
        self.assertEquals('dd3168f82679e9d59ada7f0bfd213f744aca237f5f9e4bae3abcfed998f088a7c79d9d426a5ac0468959915d48a0586576069a51f7fa3ee6fa6affb5f14edd22', actual_url['extractions'][0]['hashes']['sha512'])
        self.assertEquals(dt, actual_url['extractions'][0]['timestamp'])

        #check returned file dictionary
        #{'encoding': 'hex',
        #'content_guess': 'SWF',
        #'data': 'xxx',
        #'hashes': {
        #    'md5': '6478baaaef1fea99d1c4520ec2d30002',
        #    'sha1': '3d44fc9b69f221b28b69b8904fa8a65686a7accb',
        #    'sha512': '123'
        #}}

        self.assertEqual('hex', actual_file['encoding'])
        self.assertEqual('SWF', actual_file['content_guess'])
        self.assertEquals('6478baaaef1fea99d1c4520ec2d30002', actual_file['hashes']['md5'])
        self.assertEquals('3d44fc9b69f221b28b69b8904fa8a65686a7accb', actual_file['hashes']['sha1'])
        self.assertEquals('dd3168f82679e9d59ada7f0bfd213f744aca237f5f9e4bae3abcfed998f088a7c79d9d426a5ac0468959915d48a0586576069a51f7fa3ee6fa6affb5f14edd22', actual_file['hashes']['sha512'])

