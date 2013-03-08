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
from datetime import datetime
from urlparse import urlparse

from normalizer.modules.basenormalizer import BaseNormalizer


class GlastopfEvents(BaseNormalizer):
    channels = ('glastopf.events',)

    def __init__(self):
        #dorks to be filtered out
        self.dork_filter = ['/', '/headers', '/favicon.ico', '/w00tw00t.at.ISC.SANS.DFind:)']

    def normalize(self, data, channel, submission_timestamp):
        o_data = json.loads(data)

        if self.is_RFC1918_addr(o_data['source'][0]):
            return []

        relations = {}

        relations['session'] = self.make_session(o_data)
        relations['session']['session_http'] = self.make_session_http(o_data)
        dork = self.make_dork(o_data, submission_timestamp)
        if dork:
            relations['dork'] = dork

        return [relations]

    def make_dork(self, data, timestamp):
        dork = urlparse(self.make_url(data)).path
        if dork and dork not in self.dork_filter:
            return {'content': dork,
                    'type': 'inurl',
                    'timestamp': timestamp,
                    'count': 1}

    def make_session(self, data):
        session = {}
        session['timestamp'] = datetime.strptime(
            data['time'], '%Y-%m-%d %H:%M:%S')
        session['source_ip'] = data['source'][0]
        session['source_port'] = data['source'][1]
        #TODO: Extract from header if specified
        session['destination_port'] = 80
        session['protocol'] = 'http'
        session['honeypot'] = 'glastopf'

        return session

    def make_session_http(self, data):
        session_http = {}

        request = {}
        request['header'] = json.dumps(data['request']['header'])
        if 'body' in data['request']:
            request['body'] = data['request']['body']
        if 'Host' in data['request']['header']:
            request['host'] = data['request']['header']['Host']
        request['verb'] = data['request']['method']

        request['url'] = self.make_url(data)
        #TODO: Parse response from glastopf...
        response = {}

        if len(request) != 0:
            session_http['request'] = request
        if len(response) != 0:
            session_http['response'] = response
        return session_http

    def clean_url(self, url):
        if len(url) > 2 and url[:2] == '//':
            url = url[1:]
        return url

    def make_url(self, data):
        """
        Tries to make a valid URL from the attackers request.
        note: Glastopf reports ['url'] as path + query string (omitting schema and netloc),
        """

        if 'Host' in data['request']['header'] and not data['request']['url'].startswith('http'):
            url = 'http://' + data['request']['header']['Host'] + data['request']['url']
        else:
            #best of luck!
            url = data['request']['url']
        return url
