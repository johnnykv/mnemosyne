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

import base64
import json
from basenormalizer import BaseNormalizer


class ThugFiles(BaseNormalizer):
    channels = ('thug.files',)

    def normalize(self, data, channel, submission_timestamp):
        data = json.loads(data)
        decoded = base64.b64decode(data['data'])
        hashes = super(ThugFiles, self).generate_checksum_list(decoded)

        file_ = {
            'encoding': 'hex',
            'content_guess': data['type'],
            'data': decoded.encode('hex'),
            'hashes': hashes
        }

        #TODO: Fix URL parsing
        url_parts = super(ThugFiles, self).make_url(data['url'])
        url = {
            'url': 'http://' + url_parts['netloc'] + url_parts['path'],
            'extractions': [
                {
                    'hashes': hashes,
                    'timestamp': submission_timestamp
                }
            ]

        }

        relations = {'file': file_,
                     'url': url}

        return [relations]
