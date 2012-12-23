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
from datetime import datetime
import json


class GlastopfEvents(BaseNormalizer):
    channels = ('glastopf.events',)

    def normalize(self, data, channel):
        o_data = json.loads(data)
        relations = {}

        relations['session'] = self.make_session(o_data)
        relations['session']['session_http'] = self.make_session_http(o_data)
        relations['session']['session_http']['url'] = self.make_url(o_data)
        return [relations]

    def make_session(self, data):
        session = {}
        session['timestamp'] = datetime.strptime(
            data['time'], '%Y-%m-%d %H:%M:%S')
        session['source_ip'] = data['source'][0]
        session['source_port'] = data['source'][1]
        #TODO: Extract from header if specified
        session['destination_port'] = 80
        session['session_type'] = 'http'

        return session

    def make_session_http(self, data):
        session_http = {}

        session_http['header'] = json.dumps(data['request']['header'])
        if 'body' in data['request']:
            session_http['body'] = data['request']['body']
        if 'Host' in data['request']['header']:
            session_http['host'] = data['request']['header']['Host']
        session_http['verb'] = data['request']['method']

        return session_http

    def make_url(self, data):
        #note: glastopf splits the url in an unorthodox way :)

        if 'Host' in data['request']['header']:
            url = 'http://' + data['request']['header']['Host'] + data['request']['url']
        else:
            #best of luck!
            url = data['request']['url']

        return super(GlastopfEvents, self).make_url(url)
