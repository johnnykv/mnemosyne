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
from datetime import datetime
from normalizer.modules.basenormalizer import BaseNormalizer


class BeeswarmHive(BaseNormalizer):
    channels = ('beeswarm.sessions',)

    def normalize(self, data, channel, submission_timestamp):
        o_data = json.loads(data)

        auth_attempts = []
        for attempt in o_data['login_attempts']:
            auth_attempts.append({'login': attempt['username'], 'password': attempt['password']})

        session = {
            'timestamp': datetime.strptime(o_data['timestamp'], '%Y-%m-%dT%H:%M:%S.%f'),
            'source_ip': o_data['attacker_ip'],
            'source_port': o_data['attacker_source_port'],
            'destination_port': o_data['honey_port'],
            'honeypot': 'beeswarm.hive',
            'protocol': o_data['protocol'],
            'auth_attempts': auth_attempts,

        }

        #honeypot operator might have opted out of sharing his honeypot ip
        if 'honey_ip' in o_data:
            session['destination_ip'] = o_data['honey_ip']

        relations = [{'session': session},]

        return relations
