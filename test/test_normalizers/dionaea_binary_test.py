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

import os
import unittest
from normalizer.modules import dionaea_binary


class DionaeaBinaryTest(unittest.TestCase):

    def test_channels(self):
        """
        Test that the channel variable exists.
        """
        self.assertTrue(dionaea_binary.DionaeaBinary.channels)

    def test_event(self):
        """
        Test extraction of binary from dionaea and generation of correct hashes.
        """

        input_string = open(os.path.dirname(__file__) + '/data_samples/dionaea_mwbinary_sample1.txt', 'r').read()

        expected_file = {'encoding': 'hex',
                         'content_guess': 'PE32 executable (DLL) (GUI) Intel 80386, for MS Windows, UPX compressed',
                         'data': input_string,
                         'hashes': {
                             'md5': '1ba31509af22ad4fbad5b0fd2de50a41',
                             'sha1': 'c5dc7b692801f9531454df8404d3ec19f0ccff94',
                             'sha512': '3b8c3182ae5936b839211df46a417ab9866eef58e5c363ad090ce7fdc4d83d6195b10c682fb4103a825fb53be44db6afcc91bdd61668e52c62e0f473607ba93e'
                         }}
        expected_relation = [{'file': expected_file}]

        sut = dionaea_binary.DionaeaBinary()
        actual = sut.normalize(input_string, 'mwbinary.dionaea.sensorunique', None)
        self.assertTrue(len(expected_relation), len(actual))
        self.assertEqual(expected_relation[0]['file'], actual[0]['file'])
