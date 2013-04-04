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

import logging

import gevent

import hpfeeds


logger = logging.getLogger(__name__)


class FeedPuller:
    def __init__(self, database, ident, secret, port, host, feeds):

        self.database = database

        self.ident = ident
        self.secret = secret
        self.port = port
        self.host = host
        self.feeds = feeds

        self.enabled = True

    def start_listening(self):
        while self.enabled:
            try:
                self.hpc = hpfeeds.new(self.host, self.port, self.ident, self.secret)

                def on_error(payload):
                    logger.error('Error message from broker: {0}'.format(payload))
                    self.hpc.stop()

                def on_message(ident, chan, payload):
                    self.database.insert_hpfeed(ident, chan, payload)

                self.hpc.subscribe(self.feeds)
                self.hpc.run(on_message, on_error)
            except Exception as ex:
                self.hpc.stop()
                logger.exception('Exception caught: {0}'.format(ex))
                #throttle
            gevent.sleep(5)

    def stop(self):
        self.hpc.stop()
        self.enabled = False
        logger.info("FeedPuller stopped.")
