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

import hpfeeds
import logging


class FeedBroker:
    def __init__(self, database, ident, secret, port, host, feeds):
        self.logger = logging.getLogger()

        self.database = database

        self.ident = ident
        self.secret = secret
        self.port = port
        self.host = host
        self.feeds = feeds

        self.stats = {}

    def start_listening(self):

        try:
            self.hpc = hpfeeds.new(self.host, self.port, self.ident, self.secret)
        except hpfeeds.FeedException, e:
            logging.error('Error: {0}'.format(e))

        def on_message(ident, chan, payload):
            self.database.insert_hpfeed(ident, chan, payload)
            if chan in self.stats:
                self.stats[chan] += 1
            else:
                self.stats[chan] = 1

        def on_error(payload):
            logging.error('Error message from broker: {0}'.format(payload))
            self.hpc.stop()

        self.hpc.subscribe(self.feeds)
        try:
            self.hpc.run(on_message, on_error)
        except hpfeeds.FeedException, e:
            self.logger.error('Error: {0}'.format(e))

    def stop(self):
        self.hpc.stop()
        self.logger.info("FeedBroker stopped.")
