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


class Database_HP_Tests(unittest.TestCase):
    def test_valid_insert(self):
        """
        Test inseration of a valid and hpfeeds entry.
        This test only checks if the specified data can be inserted without exceptions,
        and that a correct primary key is returned
        """
        #nsert_hpfeed(self, ident, chan, payload):
        tmp_db = tempfile.mktemp()
        try:
            sut = database.Database('sqlite:///' + tmp_db)
            pk = sut.insert_hpfeed('xxxyyyzzz', 'mnemosyne.test', 'stuffstuffstuff')
        finally:
            if os.path.isfile(tmp_db):
                os.remove(tmp_db)
        self.assertEqual(pk, 1)
