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
from BaseHTTPServer import BaseHTTPRequestHandler
from StringIO import StringIO
from stix.core import STIXPackage, STIXHeader
from stix.indicator import Indicator
from cybox.objects import http_session_object, network_connection_object, port_object
from stix.core import STIXPackage, STIXHeader

class GlastopfEvents():
    channels = ('glastopf.events',)

    def transform(self, data, channel, submission_timestamp):
        o_data = json.loads(data)

        if 'request_raw' in o_data:
            #basic parsing of the raw http request
            http_request = HTTPRequest(o_data['request_raw'])

            stix_socketAddress = network_connection_object.SocketAddress()
            stix_socketAddress.ip_address = o_data['source'][0]
            stix_port = port_object.Port()
            stix_port.port_value = o_data['source'][1]
            stix_socketAddress.port = stix_port

            stix_networkConnection = network_connection_object.NetworkConnection()
            stix_networkConnection.source_socket_address = stix_socketAddress

            stix_HttpRequestLine = http_session_object.HTTPRequestLine()
            stix_HttpRequestLine.value = http_request.raw_requestline
            stix_HttpRequestLine.http_method = http_request.command
            stix_HttpRequestLine.version = http_request.request_version

            strix_HttpClientRequest = http_session_object.HTTPClientRequest()
            strix_HttpClientRequest.http_request_line = stix_HttpRequestLine

            #no support for no server response?
            stix_serverResponse = http_session_object.HTTPServerResponse()

            stix_requestResponse = http_session_object.HTTPRequestResponse()
            stix_requestResponse.http_client_request = strix_HttpClientRequest
            stix_requestResponse.http_server_response = stix_serverResponse

            stix_HttpSession = http_session_object.HTTPSession()
            stix_HttpSession.http_request_response = [stix_requestResponse, ]

            stix_package = STIXPackage()
            stix_header = STIXHeader()
            stix_header.package_intent = 'Observations'

            stix_package.add_observable(stix_HttpSession)
            stix_package.add_observable(stix_networkConnection)

            print(stix_package.to_xml())

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

if __name__ == '__main__':
    input_string = """{\"pattern\": \"SQLI\", \"time\": \"2013-06-09 06:06:20\", \"filename\": null, \"source\": [\"1.2.3.4\", 50781], \"request_raw\": \"GET /jinglebells?id=25'); DROP TABLE USERS; -- HTTP/1.1\\r\\nAccept-Encoding: identity\\r\\nHost: woopa.mil\\r\\n\\r\\nMuhaha\", \"request_url\": \"/jinglebells\"}"""

    g = GlastopfEvents();
    g.transform(input_string, '', '')