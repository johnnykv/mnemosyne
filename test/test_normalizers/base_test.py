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

from normalizer.modules import basenormalizer


class BaseNormalizerTest(unittest.TestCase):
    def test_RFC1918_filter(self):
        """
        Tests if RFC1918 (private networks) addresses are recognized
        """

        sut = basenormalizer.BaseNormalizer()
        #test if RFC1918 addresses returns true
        self.assertTrue(sut.is_RFC1918_addr('192.168.4.4'))
        self.assertTrue(sut.is_RFC1918_addr('10.1.2.3'))
        self.assertTrue(sut.is_RFC1918_addr('172.16.5.5'))

        #test if non-RFC1918 addresses returns false
        self.assertFalse(sut.is_RFC1918_addr('4.4.4.4'))
        self.assertFalse(sut.is_RFC1918_addr('8.8.8.8'))
        self.assertFalse(sut.is_RFC1918_addr('212.111.1.2'))
