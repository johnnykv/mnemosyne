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

import xml.etree.ElementTree as ET


class ThugEvents(BaseNormalizer):

    channels = ('thug.events',)

    def normalize(self, data, channel):

        root = ET.fromstring(data)

        #TODO: Register namespace with ElementTree?
        analysis = root.findall('./{http://maec.mitre.org/XMLSchema/maec-core-1}Analyses' +
                                '/{http://maec.mitre.org/XMLSchema/maec-core-1}Analysis')

        url_list = []
        for a in analysis:
            for uri in a.iter('{http://maec.mitre.org/XMLSchema/maec-core-1}URI'):
                url_list.append(uri.text)

        #TODO: The interesting stuff from behaviors. (and correlate with .files)
        return_list = []
        for url in url_list:
            url_dict = super(ThugEvents, self).make_url('...')
            return_list.append({'url': url_dict})

        return return_list
