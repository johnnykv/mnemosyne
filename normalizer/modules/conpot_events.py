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

import json

from normalizer.modules.basenormalizer import BaseNormalizer


class Conpot(BaseNormalizer):
    channels = ('conpot.events',)

    def normalize(self, data, channel, submission_timestamp):
        o_data = json.loads(data)

        if self.is_RFC1918_addr(o_data['remote'][0]):
            return []

        session = {
            'timestamp': submission_timestamp,
            'source_ip': o_data['remote'][0],
            'source_port': o_data['remote'][1],
            'destination_port': 502,
            'honeypot': 'conpot',
            'protocol': 'modbus',
            'session_modbus': { 'pdus': o_data['data']}

            }

        relations = [{'session': session},]

        return relations