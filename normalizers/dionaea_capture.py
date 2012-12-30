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
import json


class DionaesCaptures(BaseNormalizer):
    channels = ('dionaea.capture',)

    def normalize(self, data, channel, submission_timestamp):
        o_data = json.loads(data)

        session = {
            'timestamp': submission_timestamp,
            'source_ip': o_data['saddr'],
            'source_port': int(o_data['sport']),
            'destination_ip': o_data['daddr'],
            'destination_port': int(o_data['dport']),
            'honeypot': 'Dionaea'
        }

        protocol = super(DionaesCaptures, self).port_to_service(int(o_data['dport']))
        if protocol != None:
            session['protocol'] = protocol

        relations = {'session': session}
        return [relations]
