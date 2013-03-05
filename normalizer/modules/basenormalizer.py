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

import hashlib
import socket
import struct
from urlparse import urlparse


class BaseNormalizer(object):
    ports_map = {22: 'ssh', 80: 'http', 135: 'dcom-scm', 445: 'microsoft-ds', 443: 'https"'}

    def normalize(self, data, channel_name, submission_timestamp):
        pass

    def make_url(self, url):
        url_dict = {}
        result = urlparse(url)
        url_dict['url'] = url
        url_dict['scheme'] = result.scheme
        url_dict['netloc'] = result.netloc
        url_dict['path'] = result.path
        url_dict['params'] = result.params
        url_dict['query'] = result.query
        url_dict['fragment'] = result.fragment
        return url_dict

    def port_to_service(self, port_number):
        if port_number in BaseNormalizer.ports_map:
            return BaseNormalizer.ports_map[port_number]
        else:
            return None

    def generate_checksum_list(self, data):
        result = {}
        result['md5'] = hashlib.md5(data).hexdigest()
        result['sha1'] = hashlib.sha1(data).hexdigest()
        result['sha512'] = hashlib.sha512(data).hexdigest()
        return result

    def is_RFC1918_addr(self, ip):
        #10.0.0.0 = 167772160
        #172.16.0.0 = 2886729728
        #192.168.0.0 = 3232235520
        RFC1918_net_bits = ((167772160, 8), (2886729728, 12), (3232235520, 16))

        #ip to decimal
        ip = struct.unpack("!L", socket.inet_aton(ip))[0]

        for net, mask_bits in RFC1918_net_bits:
            ip_masked = ip & (2 ** 32 - 1 << (32 - mask_bits))
            if ip_masked == net:
                return True

        return False

