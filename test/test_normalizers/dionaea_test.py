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
from normalizer.modules import dionaea_capture
from datetime import datetime


class DionaeaTests(unittest.TestCase):
    def test_channels(self):
        """
        Test that the channel variable exists.
        """
        self.assertTrue(dionaea_capture.DionaeaCaptures.channels)

    def test_valid_message(self):
        """
        Test correct parsing of a valid dionaea event.
        """
        input_time = datetime(2012, 12, 14, 12, 22, 51)
        input_string = '{\"url\": \"http://118.167.12.21:1852/psgmioap\", \"daddr\": \"134.61.128.61\", '\
                       '\"saddr\": \"118.167.12.21\", \"dport\": \"445\", \"sport\": \"3006\", '\
                       '\"sha512\": \"8cbcec5fe75ee97fc3c18bafdd79cdb5d83bfb4190ba5093907d1ee1946'\
                       '32813451b3aebfc8145452afae9ac5e413d2673746317c13b64856f3fcae12a109fd2\", '\
                       '\"md5\": \"0724c68f973e4e35391849cfb5259f86\"}'

        attachments = [
            {
                'description': 'Binary extraction',
                'hashes':
                    {'md5': '0724c68f973e4e35391849cfb5259f86',
                     'sha512': '8cbcec5fe75ee97fc3c18bafdd79cdb5d83bfb4190ba5093907d1ee194632813451b3aebfc8145452afae9ac5e413d2673746317c13b64856f3fcae12a109fd2'}
            }, ]

        expected_session = {
            'timestamp': datetime(2012, 12, 14, 12, 22, 51),
            'source_ip': '118.167.12.21',
            'source_port': 3006,
            'destination_ip': '134.61.128.61',
            'destination_port': 445,
            'honeypot': 'dionaea',
            'protocol': 'microsoft-ds',
            'attachments': attachments
        }

        url = {'url': 'http://118.167.12.21:1852/psgmioap',
               'extractions': [{
                                   'timestamp': datetime(2012, 12, 14, 12, 22, 51),
                                   'hashes': {
                                   'sha512': '8cbcec5fe75ee97fc3c18bafdd79cdb5d83bfb4190ba5093907d1ee194632813451b3aebfc8145452afae9ac5e413d2673746317c13b64856f3fcae12a109fd2',
                                   'md5': '0724c68f973e4e35391849cfb5259f86'}}]}

        expected_relations = [{'session': expected_session, 'url': url}]

        sut = dionaea_capture.DionaeaCaptures()
        actual = sut.normalize(input_string, 'dionaea.capture', input_time)

        self.assertItemsEqual(expected_relations[0]['session'],
                              actual[0]['session'])
        #self.assertItemsEqual(expected_relations[0]['url'],
        #                      actual[0]['url'])
