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
from persistance import basedatabase


class DatabaseTests(unittest.TestCase):
    def test_illegal_column_names(self):
        """
        Test if tables contains column names used by convention in Mnemosyme.
        """

        sut = basedatabase.BaseDatabase('sqlite://')

        for c in sut.tables['hpfeed'].metadata.sorted_tables:
            for name in c._columns:
                self.assertTrue('INSERTED' != name.name)
