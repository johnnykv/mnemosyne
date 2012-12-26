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
from normalizers import thug_events
import os


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
        expected_output = [{'url':
                            {
                           'url': 'http://xxx.yyy.zzz/wfgv.htm?php=receipt',
                           'scheme': 'http',
                           'netloc': 'xxx.yyy.zzz',
                           'path': '/wfgv.htm',
                           'query': 'php=receipt',
                           'params': '',
                           'fragment': '',
                           }
        }]

        sut = thug_events.ThugEvents()
        actual = sut.normalize(input_xml, 'thug.events')

        self.assertEqual(len(expected_output), len(actual))
        self.assertItemsEqual(expected_output[0], actual[0])

    def test_event_multiple_entried(self):
        """
        Test that hpfeeds data with multiple root elements get's parsed as expected.
        """

        input_xml = open(os.path.dirname(__file__) + '/data_samples/thug_events_sample1.xml', 'r').read()

        expected_output = [
            {'url':
             {
             'url': 'http://xxx.yyy.zzz/CBYCSBJHYZ.php?php=receipt',
             'scheme': 'http',
             'netloc': 'xxx.yyy.zzz',
             'path': '/CBYCSBJHYZ.php',
             'query': 'php=receipt',
                     'params': '',
                     'fragment': '',
                     }
                     },
            {'url':
             {
             'url': 'http://uuu.uu:8080/forum/links/column.php',
             'scheme': 'http',
             'netloc': 'uuu.uu:8080',
             'path': '/forum/links/column.php',
                     'query': '',
                     'params': '',
                     'fragment': '',
                     }
                     },
            {'url':
             {
             'url': 'http://ppp.aaa.mmm/wfgv.htm?php=receipt',
             'scheme': 'http',
             'netloc': 'ppp.aaa.mmm',
             'path': '/wfgv.htm',
                     'query': 'php=receipt',
                     'params': '',
                     'fragment': '',
                     }
                     }]

        sut = thug_events.ThugEvents()
        actual = sut.normalize(input_xml, 'thug.events')
        #print actual
        self.assertItemsEqual(expected_output, actual)

    def test_event_complex_sample(self):
        """
        Test parsing of a complex sample of thug data.
        """

        input_xml = open(os.path.dirname(__file__) + '/data_samples/thug_events_sample2.xml', 'r').read()

        expected_output = []

        sut = thug_events.ThugEvents()
        actual = sut.normalize(input_xml, 'thug.events')
        #print actual
        #self.assertItemsEqual(expected_output, actual)
