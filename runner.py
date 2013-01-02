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
import gevent.monkey
gevent.monkey.patch_all()

import logging

from ConfigParser import ConfigParser
from mnemosyne import Mnemosyne
from persistance import mnemodb
from WebAPI import mnemowebapi
from hpfeeds import feedbroker
import sys
import argparse

logger = logging.getLogger()


def parse_config(config_file):
    parser = ConfigParser()
    parser.read(config_file)

    if parser.getboolean('file_log', 'enabled'):
        do_logging(parser.get('file_log', 'file'))
    else:
        do_logging()

    config = {}

    config['mongo_db'] = parser.get('mongodb', 'database')

    config['hp_feeds'] = parser.get('hpfeeds', 'channels').split(',')
    config['hp_ident'] = parser.get('hpfeeds', 'ident')
    config['hp_secret'] = parser.get('hpfeeds', 'secret')
    config['hp_port'] = parser.getint('hpfeeds', 'port')
    config['hp_host'] = parser.get('hpfeeds', 'host')

    config['webapi_port'] = parser.getint('webapi', 'port')
    config['webapi_host'] = parser.get('webapi', 'host')

    return config


def do_logging(file_log=None):
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)-15s (%(funcName)s) %(message)s')

    if file_log:
        file_log = logging.FileHandler(file_log)
        file_log.setLevel(logging.DEBUG)
        file_log.setFormatter(formatter)
        logger.addHandler(file_log)

    console_log = logging.StreamHandler()
    console_log.setLevel(logging.DEBUG)
    console_log.setFormatter(formatter)
    logger.addHandler(console_log)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Mnemosyne')
    parser.add_argument('--config', dest='config_file', default='mnemosyne.cfg')
    parser.add_argument('--reset', action='store_true', default=False)
    parser.add_argument('--stats', action='store_true', default=False)
    parser.add_argument('--no_normalizer', action='store_true', default=False,
        help='Do not start the normalizer')
    parser.add_argument('--no_broker', action='store_true', default=False,
        help='Do not start the broker which takes care of storing hpfeed data.')
    parser.add_argument('--no_webapi', action='store_true', default=False,
        help='Do not enable the webapi.')

    args = parser.parse_args()
    c = parse_config(args.config_file)

    greenlets = {}

    db = mnemodb.MnemoDB(c['mongo_db'])

    if args.reset:
        db.reset_normalized()

    if not args.no_broker:
        broker = feedbroker.FeedBroker(db, c['hp_ident'], c['hp_secret'], c['hp_port'], c['hp_host'], c['hp_feeds'])
        greenlets['broker'] = gevent.spawn(broker.start_listening)

    if not args.no_normalizer:
        #start menmo and inject persistence module
        mnemo = Mnemosyne(db)
        greenlets['mnemo'] = gevent.spawn(mnemo.start_processing, False)

    if not args.no_webapi:
        #start web api and inject mongo info
        webapi = mnemowebapi.MnemoWebAPI(c['mongo_db'])
        greenlets['webapi'] = gevent.spawn(webapi.start_listening, c['webapi_host'], c['webapi_port'])

    if args.stats:
        while True:
            counts = db.collection_count()
            log_string = 'Mongo collection count:'
            for key, value in counts.items():
                log_string += ' {0}: {1}, '.format(key, value)
            logging.info(log_string)
            gevent.sleep(5)

    try:
        gevent.joinall(greenlets.values())
    except KeyboardInterrupt as err:
        pass
