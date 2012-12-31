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

from basenormalizer import BaseNormalizer
import base64


class GlastopfFiles(BaseNormalizer):
    channels = ('glastopf.files',)

    def normalize(self, data, channel, submission_timestamp):

        md5, data = data.split(' ', 1)
        decoded_data = base64.b64decode(data)
        hashes = super(GlastopfFiles, self).generate_checksum_list(decoded_data)

        file_ = {
            '_id': hashes['sha512'],
            'encoding': 'base64',
            'data': data,
            'hashes': hashes
        }

        relations = {'file': file_}

        return [relations, ]
