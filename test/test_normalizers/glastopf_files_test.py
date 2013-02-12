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
import os
import base64
from normalizer.modules import glastopf_files


class GlastopfFilesTest(unittest.TestCase):
    def test_channels(self):
        """
        Test that the channel variable exists.
        """
        self.assertTrue(glastopf_files.GlastopfFiles.channels)

    def test_event(self):
        """
        Test extraction of binary from dionaea and generation of correct hashes.
        """
        input_string = open(os.path.dirname(__file__) + '/data_samples/glastopf_files_sample1.txt', 'r').read()
        tmp, encoded = input_string.split(' ', 1)

        expected_file = {'encoding': 'hex',
                         'content_guess': 'GIF image data, version 89a, 16129 x 16129',
                         'data': base64.b64decode(encoded).encode('hex'),
                         'hashes': {
                             'md5': '755c4f9270db48f51f601638d2c4b4b0',
                             'sha1': '9ed97ccdd683aa8842a5473315e8b45bda168556',
                             'sha512': 'bb1d9c92a7cdc8dbd61365c5d757729a2c8d131fb5f49da3e4a6818635f5e8eb40a2bf06e9a25a069b618d934c53b367f3327a37b65c50e66d60580ee178a135'
                         }}
        expected_relation = [{'file': expected_file}]

        sut = glastopf_files.GlastopfFiles()
        actual = sut.normalize(input_string, 'glastopf.files', None)

        self.assertTrue(len(expected_relation), len(actual))
        self.assertEqual(expected_relation[0]['file'], actual[0]['file'])
