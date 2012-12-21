import gevent
from gevent import Greenlet
import gevent.monkey
gevent.monkey.patch_all()

import logging
import argparse
from ConfigParser import ConfigParser

from rawlogpersister import RawlogPersister
from listener import Listener


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)-15s (%(funcName)s) %(message)s')
file_log = logging.FileHandler('log.txt')
file_log.setLevel(logging.DEBUG)
file_log.setFormatter(formatter)
logger.addHandler(file_log)

console_log = logging.StreamHandler()
console_log.setLevel(logging.DEBUG)
console_log.setFormatter(formatter)
logger.addHandler(console_log)

parser = argparse.ArgumentParser(description='Mnemosyne persister')
parser.add_argument('configfile')
args = parser.parse_args()

config_parser = ConfigParser()
config_parser.read(args.configfile)
conn_string = config_parser.get('sqlalchemy', 'connection_string')

persister = RawlogPersister(conn_string)

feeds = config_parser.get('hpfeeds', 'channels').split(',')
print feeds
ident = config_parser.get('hpfeeds', 'ident')
secret = config_parser.get('hpfeeds', 'secret')
port = config_parser.getint('hpfeeds', 'port')
host = config_parser.get('hpfeeds', 'host')

listener = Listener(persister, ident, secret, port, host, feeds)
listener_greenlet = gevent.spawn(listener.start_listening())
Greenlet.join(listener_greenlet)
