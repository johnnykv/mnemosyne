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
from persistance import mnemodb
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

    def start_processing(self):
        while True:
            to_be_processed = self.database.get_hpfeed_data(50)
            for key, value in to_be_processed.items():
                try:
                    norm = self.normalize(value['payload'], value['channel'])
                    self.database.insert_normalized(norm, key)
                except Exception as ex:
                    print ex
                    logger.warning('Failed to normalize and import item with hpfeed_id = %i, channel = %s. (%s)' % (key, value['channel'], ex))
            sleep(5)

    def normalize(self, data, channel):
        if channel in self.normalizers:
            return self.normalizers[channel].normalize(data, channel)
        else:
            logger.warning('No normalizer could be found for %s.' % (channel,))


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
    conn_string = config_parser.get('sqlalchemy', 'connection_string')

    feeds = config_parser.get('hpfeeds', 'channels').split(',')
    ident = config_parser.get('hpfeeds', 'ident')
    secret = config_parser.get('hpfeeds', 'secret')
    port = config_parser.getint('hpfeeds', 'port')
    host = config_parser.get('hpfeeds', 'host')

    #self, database, ident, secret, port, host, feeds

    #start broker and inject persistence module
    #(pull logs from hpfeeds and persist them "raw" in database)
    db = mnemodb.MnemoDB(conn_string)
    broker = feedbroker.FeedBroker(db, ident, secret, port, host, feeds)
    feed_greenlet = gevent.spawn(broker.start_listening)

    #start menmo and inject persistence module
    mnemo = Mnemosyne(db)
    mnemo_greenlet = gevent.spawn(mnemo.start_processing)

    Greenlet.join(feed_greenlet)
