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

import json
from normalizer.modules.basenormalizer import BaseNormalizer


class DionaeaCaptures(BaseNormalizer):
    channels = ('dionaea.capture', 'dionaea.capture.anon', 'dionaea.captures')

    def normalize(self, data, channel, submission_timestamp):
        o_data = json.loads(data)

        if self.is_RFC1918_addr(o_data['saddr']):
            return []

        session = {
            'timestamp': submission_timestamp,
            'source_ip': o_data['saddr'],
            'source_port': int(o_data['sport']),
            'destination_ip': o_data['daddr'],
            'destination_port': int(o_data['dport']),
            'honeypot': 'dionaea'
        }

        if 'daddr' in o_data:
            session['destination_ip'] = o_data['daddr'],

        protocol = super(DionaeaCaptures, self).port_to_service(int(o_data['dport']))
        if protocol is not None:
            session['protocol'] = protocol

        attachments = [
            {
                'description': 'Binary extraction',
                'hashes':
                    {'md5': o_data['md5'],
                     'sha512': o_data['sha512']}
            }, ]

        #url = {'url': o_data['url'],
        #       'extractions': [{
        #                           'timestamp': submission_timestamp,
        #                           'hashes': {
        #                               'md5': o_data['md5'],
        #                               'sha512': o_data['sha512']
        #                           }}]}

        session['attachments'] = attachments

        relations = {'session': session}
        #relations = {'session': session, 'url': url}
        return [relations]
