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
from datetime import datetime


class ThugEvents(BaseNormalizer):
    channels = ('thug.events',)

    def normalize(self, data, channel, submission_timestamp):
        #split up original payload, so that there are only one root element
        data = '<THUG_DATA>' + data + '</THUG_DATA>'

        fake_root = ET.fromstring(data)

        return_list = []

        #TODO: Register namespace with ElementTree?
        for root in fake_root.findall('{http://maec.mitre.org/XMLSchema/maec-core-1}MAEC_Bundle'):
            analysis = root.findall('./{http://maec.mitre.org/XMLSchema/maec-core-1}Analyses' +
                                    '/{http://maec.mitre.org/XMLSchema/maec-core-1}Analysis')
            for a in analysis:
                timestamp = datetime.strptime(
                    a.attrib['start_datetime'], '%Y-%m-%d %H:%M:%S.%f')
                a.attrib['start_datetime']

                data = {}
                object_element = a.find(
                    '{http://maec.mitre.org/XMLSchema/maec-core-1}Subject/{http://maec.mitre.org/XMLSchema/maec-core-1}Object')

                data['url'] = object_element.find(
                    './{http://maec.mitre.org/XMLSchema/maec-core-1}Internet_Object_Attributes/{http://maec.mitre.org/XMLSchema/maec-core-1}URI').text

                code_snippets = object_element.findall(
                    './{http://maec.mitre.org/XMLSchema/maec-core-1}Associated_Code/{http://maec.mitre.org/XMLSchema/maec-core-1}Associated_Code_Snippet/{http://maec.mitre.org/XMLSchema/maec-core-1}Code_Snippet')
                for snippet in code_snippets:
                    language = snippet.attrib['language']
                    source = snippet.find('./{http://maec.mitre.org/XMLSchema/maec-core-1}Code_Segment').text

                    hashes = super(ThugEvents, self).generate_checksum_list(source)

                    file_ = {
                        'encoding': 'hex',
                        'content_guess': language,
                        'data': source.encode('hex'),
                        'hashes': hashes
                    }

                    if 'extractions' not in data:
                        data['extractions'] = []
                    data['extractions'].append({'timestamp': timestamp,
                                                'hashes': hashes})

                    return_list.append({'file': file_})
                return_list.append({'url': data})
        return return_list
