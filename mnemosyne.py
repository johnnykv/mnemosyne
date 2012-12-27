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

import gevent
from gevent import Greenlet
import gevent.monkey
gevent.monkey.patch_all()

import logging

from normalizers import basenormalizer
from normalizers import glastopf_events
from normalizers import thug_events
from normalizers import kippo_events
from persistance import mnemodb
from WebAPI import mnemowebapi

from hpfeeds import feedbroker
from ConfigParser import ConfigParser

from time import sleep


class Mnemosyne(object):
    def __init__(self, database):
        self.normalizers = {}
        #injected instance of database.Database
        self.database = database

        #map normalizers
        for n in basenormalizer.BaseNormalizer.__subclasses__():
            normalizer = n()
            for channel in normalizer.channels:
                if channel in self.normalizers:
                    raise Exception('Only one normalizer for each channel allowed (%s).' % (channel,))
                else:
                    self.normalizers[channel] = normalizer

    def start_processing(self, warn_no_normalizers):
        while True:
            chan_no_normalizer = {}
            to_be_processed = self.database.get_hpfeed_data(50)
            for hpfeed_item in to_be_processed:
                try:
                    channel = hpfeed_item['channel']
                    if channel in self.normalizers:
                        norm = self.normalizers[channel].normalize(hpfeed_item['payload'], channel, hpfeed_item['timestamp'])
                        self.database.insert_normalized(norm, hpfeed_item)
                    else:
                        if channel in chan_no_normalizer:
                            chan_no_normalizer[channel] = chan_no_normalizer[channel] + 1
                        else:
                            chan_no_normalizer[channel] = 1
                except Exception as ex:
                    logger.warning('Failed to normalize and import item with hpfeed id = %s, channel = %s. (%s)' % (hpfeed_item['_id'], hpfeed_item['channel'], ex))

            if warn_no_normalizers:
                if chan_no_normalizer:
                    for key, value in chan_no_normalizer.items():
                        logger.warning('No normalizer could be found for %s. (Repeated %i times).' % (key, value))

            sleep(5)

if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)-15s (%(funcName)s) %(message)s')
    #file_log = logging.FileHandler('log.txt')
    #file_log.setLevel(logging.DEBUG)
    #file_log.setFormatter(formatter)
    #logger.addHandler(file_log)

    console_log = logging.StreamHandler()
    console_log.setLevel(logging.DEBUG)
    console_log.setFormatter(formatter)
    logger.addHandler(console_log)

    config_parser = ConfigParser()
    config_parser.read('mnemosyne.cfg')
    mongo_database = config_parser.get('mongodb', 'database')

    feeds = config_parser.get('hpfeeds', 'channels').split(',')
    ident = config_parser.get('hpfeeds', 'ident')
    secret = config_parser.get('hpfeeds', 'secret')
    hp_port = config_parser.getint('hpfeeds', 'port')
    hp_host = config_parser.get('hpfeeds', 'host')

    webapi_port = config_parser.getint('webapi', 'port')
    webapi_host = config_parser.get('webapi', 'host')

    #start broker and inject persistence module
    #(pull logs from hpfeeds and persist them pseudo-raw in database)
    db = mnemodb.MnemoDB(mongo_database)
    broker = feedbroker.FeedBroker(db, ident, secret, hp_port, hp_host, feeds)
    feed_greenlet = gevent.spawn(broker.start_listening)

    #start menmo and inject persistence module
    mnemo = Mnemosyne(db)
    mnemo_greenlet = gevent.spawn(mnemo.start_processing, False)

    #start web api and inject mongo info
    webapi = mnemowebapi.MnemoWebAPI(mongo_database)
    webapi_greenlet = gevent.spawn(webapi.start_listening, webapi_host, webapi_port)

    Greenlet.join(feed_greenlet)
