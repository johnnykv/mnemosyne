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

from urlparse import urlparse
import hashlib


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


