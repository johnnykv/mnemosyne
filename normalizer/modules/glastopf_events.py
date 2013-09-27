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
import re
from datetime import datetime
from urlparse import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler
from StringIO import StringIO

from normalizer.modules.basenormalizer import BaseNormalizer


class GlastopfEvents(BaseNormalizer):
    channels = ('glastopf.events',)

    def __init__(self):
        #dorks to be filtered out
        self.dork_filter = '/headers|favicon.ico|w00tw00t|/robots.txt'

    def normalize(self, data, channel, submission_timestamp):
        o_data = json.loads(data)

        if self.is_RFC1918_addr(o_data['source'][0]):
            return []

        relations = {}

        #only old versions of glastopf has the request key
        relations['session'] = self.make_session(o_data)
        relations['session']['session_http'] = self.make_session_http(o_data)
        dork = self.make_dork(o_data, submission_timestamp)
        if dork:
            relations['dork'] = dork

        return [relations]

    def make_dork(self, data, timestamp):
        #only old versions of glastopf has the request key
        if 'request' in data:
            dork = urlparse(self.make_url(data)).path
        else:
            dork = urlparse(data['request_url']).path
        if len(dork) > 1 and not re.match(r'.*({0}).*'.format(self.dork_filter), dork):
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
        #glastopf's old logging format has the 'request' key
        if 'request' in data:
            request['header'] = json.dumps(data['request']['header'])
            if 'body' in data['request']:
                request['body'] = data['request']['body']
            if 'Host' in data['request']['header']:
                request['host'] = data['request']['header']['Host']
            request['verb'] = data['request']['method']

            request['url'] = self.make_url(data)
        #new glastopf logging format
        else:
            r = HTTPRequest(data['request_raw'])
            request['host'] = r.headers['host']
            #dict json loads?
            request['header'] = r.headers.items()
            request['verb'] = r.command
            request['path'] = r.path
            request['body'] = r.rfile.read()

        if len(request) != 0:
            session_http['request'] = request
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


#Thanks Brandon Rhodes!
#http://stackoverflow.com/questions/4685217/parse-raw-http-headers
class HTTPRequest(BaseHTTPRequestHandler):
    def __init__(self, request_text):
        self.rfile = StringIO(request_text)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()

    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message
