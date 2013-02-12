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

import unittest
import datetime
import os
from normalizer.modules import thug_events


class ThugTests(unittest.TestCase):

    def test_channels(self):
        """
        Test that channel variable exists.
        """
        self.assertTrue(thug_events.ThugEvents.channels)

    def test_event_url_not_found(self):
        """
        Test normalization of basic thug event.
        """

        input_xml = '''<MAEC_Bundle xmlns:ns1="http://xml/metadataSharing.xsd" xmlns="http://maec.mitre.org/XMLSchema/maec-core-1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maec.mitre.org/XMLSchema/maec-core-1 file:MAEC_v1.1.xsd" id="maec:thug:bnd:1" schema_version="1.100000">
    <Analyses>
        <Analysis start_datetime="2012-12-23 20:16:55.151345" id="maec:thug:ana:2" analysis_method="Dynamic">
            <Subject>
                <Object object_name="http://xxx.yyy.zzz/wfgv.htm?php=receipt" type="URI" id="maec:thug:obj:3">
                    <Internet_Object_Attributes>
                        <URI>http://xxx.yyy.zzz/wfgv.htm?php=receipt</URI>
                    </Internet_Object_Attributes>
                </Object>
            </Subject>
            <Tools_Used>
                <Tool id="maec:thug:tol:1">
                    <Name>Thug</Name>
                    <Version>0.4.15</Version>
                    <Organization>The Honeynet Project</Organization>
                </Tool>
            </Tools_Used>
        </Analysis>
    </Analyses>
    <Behaviors>
        <Behavior id="maec:thug:bhv:4">
            <Description>
                <Text>[HTTP] URL: http://xxx.yyy.zzz/wfgv.htm?php=receipt (Status: 404, Referrer: None)</Text>
            </Description>
            <Discovery_Method tool_id="maec:thug:tol:5" method="Dynamic Analysis"/>
        </Behavior>
        <Behavior id="maec:thug:bhv:6">
            <Description>
                <Text>[File Not Found] URL: http://xxx.yyy.zzz/wfgv.htm?php=receipt</Text>
            </Description>
            <Discovery_Method tool_id="maec:thug:tol:7" method="Dynamic Analysis"/>
        </Behavior>
    </Behaviors>
    <Pools/>
</MAEC_Bundle>
'''
        expected_output = [{'url': {'url': 'http://xxx.yyy.zzz/wfgv.htm?php=receipt'}}]

        sut = thug_events.ThugEvents()
        actual = sut.normalize(input_xml, 'thug.events', None)

        self.assertEqual(len(expected_output), len(actual))

        self.assertEqual(expected_output, actual)

    def test_event_multiple_entried(self):
        """
        Test that hpfeeds data with multiple root elements get's parsed as expected.
        """

        input_xml = open(os.path.dirname(__file__) + '/data_samples/thug_events_sample1.xml', 'r').read()

        expected_output = [
            {'url': {'url': 'http://xxx.yyy.zzz/CBYCSBJHYZ.php?php=receipt'}},
            {'url': {'url': 'http://uuu.uu:8080/forum/links/column.php'}},
            {'url': {'url': 'http://ppp.aaa.mmm/wfgv.htm?php=receipt'}},
        ]

        sut = thug_events.ThugEvents()
        actual = sut.normalize(input_xml, 'thug.events', None)
        #print actual
        self.assertEqual(expected_output, actual)

    def test_event_complex_sample(self):
        """
        Test parsing of a complex sample of thug data.
        """

        input_xml = open(os.path.dirname(__file__) + '/data_samples/thug_events_sample2.xml', 'r').read()

        file_1 = {
            'encoding': 'hex',
            'content_guess': 'Javascript',
            'data': 'placeholder',
            'hashes': {'sha1': 'c80d2b26eec6a49068fdfda874e68b7aeb7669fa', 'sha512': '5a4ff355ba48b9c11ced27e06d32afa29a11c8ba230fd587288623d53f9927cbf84743884322182649c3c8fd706118541d54dfd7da68a82c606dd9e17c836887', 'md5': '864fff7df4a027049ed855dafc71e94d'}
        }

        file_2 = {
            'encoding': 'hex',
            'content_guess': 'Javascript',
            'data': 'placeholder',
            'hashes': {'sha1': '65854a75eac74a727c7714b78f5cd4a9602063ab', 'sha512': '1c0c85f1c33c3da94c8015acbe8f7a54849081af590ad1493037e340e59ad34fd06a38a27ee48e84d9a0710d4a0e5c85fd0510bb9bb09319dec65be53d173af8', 'md5': '58a2ac97c6e16870a758ebc8501ebf7f'}
        }

        file_3 = {
            'encoding': 'hex',
            'content_guess': 'Javascript',
            'data': 'placeholder',
            'hashes': {'sha1': '78a4a03e86463a0c624ac5077caeda00321da721', 'sha512': 'f9234c4afe440c3597d9d6c56e34e74fa746579fe15556f2e741625aaaf31ee6f1e63f17dbaffd5dd668b0b0f66e5d4cda0f756ad4ea505afdadc92566a17171', 'md5': '6d5a985d0e9bd02cdd6970c10770da0c'}
        }

        url = {'url':
               'http://1212122sss222.tankplay.com/news/guarantee-detain.html',
               'extractions':
               [{
                'timestamp': datetime.datetime(2012, 12, 23, 22, 8, 19, 467103),
                'hashes': {
                    'sha1': 'c80d2b26eec6a49068fdfda874e68b7aeb7669fa',
                    'sha512': '5a4ff355ba48b9c11ced27e06d32afa29a11c8ba230fd587288623d53f9927cbf84743884322182649c3c8fd706118541d54dfd7da68a82c606dd9e17c836887',
                    'md5': '864fff7df4a027049ed855dafc71e94d'}
                }, {
                'timestamp': datetime.datetime(2012, 12, 23, 22, 8, 19, 467103),
                'hashes': {
                    'sha1': '65854a75eac74a727c7714b78f5cd4a9602063ab',
                    'sha512': '1c0c85f1c33c3da94c8015acbe8f7a54849081af590ad1493037e340e59ad34fd06a38a27ee48e84d9a0710d4a0e5c85fd0510bb9bb09319dec65be53d173af8',
                    'md5': '58a2ac97c6e16870a758ebc8501ebf7f'}
                }, {
                'timestamp': datetime.datetime(2012, 12, 23, 22, 8, 19, 467103),
                'hashes': {
                    'sha1': '78a4a03e86463a0c624ac5077caeda00321da721',
                    'sha512': 'f9234c4afe440c3597d9d6c56e34e74fa746579fe15556f2e741625aaaf31ee6f1e63f17dbaffd5dd668b0b0f66e5d4cda0f756ad4ea505afdadc92566a17171',
                    'md5': '6d5a985d0e9bd02cdd6970c10770da0c'}
                }]
               }

        expected = [
            {'url': url},
            {'file': file_1},
            {'file': file_2},
            {'file': file_3},
        ]

        sut = thug_events.ThugEvents()
        actual = sut.normalize(input_xml, 'thug.events', None)

        #do not compare the actual data, hashes are good enough...
        for d in actual:
            for key, value in d.items():
                if key is 'file':
                    value['data'] = 'placeholder'

        self.assertEqual(len(expected), len(actual))

        self.assertEqual(sorted(expected), sorted(actual))
