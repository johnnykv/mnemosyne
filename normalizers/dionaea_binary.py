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

import magic
from basenormalizer import BaseNormalizer


class DionaeaBinary(BaseNormalizer):
    channels = ('mwbinary.dionaea.sensorunique',)

    def normalize(self, data, channel, submission_timestamp):
        decoded = data.decode('hex')
        hashes = super(DionaeaBinary, self).generate_checksum_list(decoded)
        file_ = {
            'encoding': 'hex',
            'content_guess': magic.from_buffer(decoded),
            'data': data,
            'hashes': hashes
        }

        relations = {'file': file_}
        return [relations]
