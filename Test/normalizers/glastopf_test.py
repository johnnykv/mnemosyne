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
from normalizers import glastopf_events
from datetime import datetime
from normalizerbase_test import NormalizerBaseTest


class GlastopfTests(unittest.TestCase, NormalizerBaseTest):

    def test_channels(self):
        """
        Test that the channel variable exists.
        """
        self.assertTrue(glastopf_events.GlastopfEvents.channels)

    def test_event(self):
        """
        Test if a valid glastopf json message get parsed as expected
        """
        input_string = """{"pattern": "rfi", "request": {"body": "", "parameters": ["a=b"], "url": "/someURL", "header": {"Accept-Language": "en-US", "Accept-Encoding": "gzip", "Connection": "close", "Accept": "*/*", "User-Agent": "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)", "Host": "www.something.com"}, "version": "HTTP/1.1", "method": "GET"}, "filename": null, "source": ["1.2.3.4", 49111], "time": "2012-12-14 12:22:51", "response": "HTTP/1.1 200 OK\\r\\nConnection: close\\r\\nContent-Type: text/html; charset=UTF-8\\r\\n\\r\\n"}"""
        expected_output = [{'session':
                            {
                           'timestamp': datetime(2012, 12, 14, 12, 22, 51),
                           'source_ip': '1.2.3.4',
                           'source_port': 49111,
                           'destination_port': 80,
                           'session_type': 'http',
                           'session_http':
                           {
                           'host': 'www.something.com',
                           'header': '{"Accept-Language": "en-US", "Accept-Encoding": "gzip", "Connection": "close", "Accept": "*/*", "User-Agent": "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)", "Host": "www.something.com"}',
                           'body': '',
                           'verb': 'GET',
                           'url':
                           {
            'url': 'http://www.something.com/someURL?a=b',
            'scheme': 'http',
            'netloc': 'www.something.com',
            'path': '/someURL',
            'query': 'a=b',
            'params': '',
            'fragment': ''
                           }
                           },
                           },
        },]

        sut = glastopf_events.GlastopfEvents()
        actual = sut.normalize(input_string, 'glastopf_events')

        #Test number of root items
        self.assertEqual(len(expected_output), len(actual))

        #Test session
        self.assertItemsEqual(expected_output[0]['session'], actual[0]['session'])
        #Test subtype, session_http
        self.assertItemsEqual(expected_output[0]['session']['session_http'], actual[0]['session']['session_http'])
        #Test url
        self.assertItemsEqual(expected_output[0]['session']['session_http']['url'],
                              actual[0]['session']['session_http']['url'])
        #check if dict contains keys which ends in _id
        self.assertFalse(self.does_dict_contain_illegal_keys(actual[0]))

    def test_make_url_actual(self):
        """
        Test if a valid, but wierd, http request can be parsed to a valid URL.
        """

        #Actual (and wierd) request intercepted by glastopf. (Host sanitized!)
        input_dict = {'request':
                     {'body': '', 'parameters': ['/shop.pl/page'], 'url': '/shop.pl/page',
                      'header':
                     {'Accept-Language': 'en-US', 'Accept-Encoding': 'gzip',
                      'Host': 'XXXX09.YYYYYYY.PPPP.org', 'Accept': '*/*', 'User-Agent':
                      'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)',
                      'Connection': 'close'},
                      'version': 'HTTP/1.1', 'method': 'GET'}}
        expected_url = 'http://XXXX09.YYYYYYY.PPPP.org/shop.pl/page?/shop.pl/page'

        sut = glastopf_events.GlastopfEvents()

        actual = sut.make_url(input_dict)
        self.assertEqual(expected_url, actual['url'])
        #check if dict contains keys which end in _id
        self.assertFalse(self.does_dict_contain_illegal_keys(actual))

    def test_make_url_no_host(self):
        """
        Test if a http request without Host header gets parsed to a realative url.

        """

        input_dict = {'request':
                     {'body': '', 'parameters': [], 'url': '/jimboo',
                      'header':
                     {'Accept-Language': 'en-US', 'Accept-Encoding': 'gzip',
                      'Accept': '*/*', 'User-Agent':
                      'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)',
                      'Connection': 'close'},
                      'version': 'HTTP/1.1', 'method': 'GET'}}
        expected_url = '/jimboo'

        sut = glastopf_events.GlastopfEvents()

        actual = sut.make_url(input_dict)
        self.assertEqual(expected_url, actual['url'])
        #check if dict contains keys which end in _id
        self.assertFalse(self.does_dict_contain_illegal_keys(actual))

    def test_make_url_basic_parsing(self):
        """
        Test if url can be parsed into the expected subelements
        """

        input_dict = {'request':
                     {'body': '', 'parameters': [], 'url': '/shop.pl/page;thisisaparam?a=b&c=d',
                      'header':
                     {'Accept-Language': 'en-US', 'Accept-Encoding': 'gzip',
                      'Host': 'a.b.c.d', 'Accept': '*/*', 'User-Agent':
                      'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)',
                      'Connection': 'close'},
                      'version': 'HTTP/1.1', 'method': 'GET'}}

        sut = glastopf_events.GlastopfEvents()

        actual = sut.make_url(input_dict)

        self.assertEqual('a.b.c.d', actual['netloc'])
        self.assertEqual('', actual['fragment'])
        self.assertEqual('thisisaparam', actual['params'])
        self.assertEqual('a=b&c=d', actual['query'])
        self.assertEqual('/shop.pl/page', actual['path'])
        self.assertEqual('http', actual['scheme'])

        #check if dict contains keys which end in _id
        self.assertFalse(self.does_dict_contain_illegal_keys(actual))

if __name__ == '__main__':
    unittest.main()
