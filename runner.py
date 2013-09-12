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

import os
import argparse
import logging
import sys

from ConfigParser import ConfigParser
from normalizer.normalizer import Normalizer
from persistance import mnemodb
from webapi import mnemowebapi
from feedpuller import feedpuller


logger = logging.getLogger()


def parse_config(config_file):
    if not os.path.isfile(config_file):
        sys.exit("Could not find configuration file: {0}".format(config_file))

    parser = ConfigParser()
    parser.read(config_file)

    log_file = None
    loggly_token = None

    if parser.getboolean('file_log', 'enabled'):
        log_file = parser.get('file_log', 'file')

    do_logging(log_file, loggly_token)

    config = {}

    if parser.getboolean('loggly_log', 'enabled'):
        config['loggly_token'] = parser.get('loggly_log', 'token')

    config['mongo_db'] = parser.get('mongodb', 'database')

    config['hpf_feeds'] = parser.get('hpfriends', 'channels').split(',')
    config['hpf_ident'] = parser.get('hpfriends', 'ident')
    config['hpf_secret'] = parser.get('hpfriends', 'secret')
    config['hpf_port'] = parser.getint('hpfriends', 'port')
    config['hpf_host'] = parser.get('hpfriends', 'host')

    config['webapi_port'] = parser.getint('webapi', 'port')
    config['webapi_host'] = parser.get('webapi', 'host')

    return config


def do_logging(file_log=None, loggly_token=None):
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)-15s (%(name)s) %(message)s')

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
    parser.add_argument('--webpath', default='webapi/static')
    parser.add_argument('--no_normalizer', action='store_true', default=False,
                        help='Do not start the normalizer')
    parser.add_argument('--no_feedpuller', action='store_true', default=False,
                        help='Do not start the broker which takes care of storing hpfeed data.')
    parser.add_argument('--no_webapi', action='store_true', default=False,
                        help='Do not enable the webapi.')

    args = parser.parse_args()
    c = parse_config(args.config_file)

    git_ref = "Unknown"
    if os.path.isfile('.git/refs/heads/master'):
        with open('.git/refs/heads/master', 'r') as f:
            git_ref = f.readline().rstrip()

    logger.info('Starting mnemosyne. (Git: {0})'.format(git_ref))

    greenlets = {}

    db = mnemodb.MnemoDB(c['mongo_db'])

    webapi = None
    hpfriends_puller = None
    normalizer = None

    if args.reset:
        print 'Renormalization (reset) of a large database can take several days.'
        answer = raw_input('Write YES if you want to continue: ')
        if answer == 'YES':
            db.reset_normalized()
        else:
            print 'Aborting'
            sys.exit(0)

    if not args.no_feedpuller:
        logger.info("Spawning hpfriends feed puller.")
        hpfriends_puller = feedpuller.FeedPuller(db, c['hpf_ident'], c['hpf_secret'], c['hpf_port'], c['hpf_host'], c['hpf_feeds'])
        greenlets['hpfriends-puller'] = gevent.spawn(hpfriends_puller.start_listening)

    if not args.no_webapi:
        logger.info("Spawning web api.")
        #start web api and inject mongo info
        if 'loggly_token' in c:
            loggly_token = c['loggly_token']
        else:
            loggly_token = None
        webapi = mnemowebapi.MnemoWebAPI(c['mongo_db'], static_file_path=args.webpath, loggly_token=loggly_token)
        greenlets['webapi'] = gevent.spawn(webapi.start_listening, c['webapi_host'], c['webapi_port'])


    if not args.no_normalizer:
        #start menmo and inject persistence module
        normalizer = Normalizer(db)
        logger.info("Spawning normalizer")
        greenlets['normalizer'] = gevent.spawn(normalizer.start_processing)

    try:

        if args.stats:
            while True:
                counts = db.collection_count()
                log_string = 'Mongo collection count:'
                for key, value in counts.items():
                    if key == 'hpfeed':
                        value = '{0} ({1} in error state)'.format(value, db.get_hpfeed_error_count())
                    log_string += ' {0}: {1}, '.format(key, value)
                logging.info(log_string)
                gevent.sleep(1800)

        gevent.joinall(greenlets.values())
    except KeyboardInterrupt as err:
        if hpfriends_puller:
            logger.info('Stopping HPFriends puller')
            hpfriends_puller.stop()
        if normalizer:
            logger.info('Stopping Normalizer')
            normalizer.stop()
        if 'webapi' in greenlets:
            greenlets['webapi'].kill(block=False)

    #wait for greenlets to do a graceful stop
    gevent.joinall(greenlets.values())


