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

from normalizers import basenormalizer
from normalizers import glastopf_events
from normalizers import glastopf_files
from normalizers import thug_events
from normalizers import kippo_events
from normalizers import dionaea_capture

import gevent

import logging

class Mnemosyne(object):
    def __init__(self, database):
        self.normalizers = {}
        #injected instance of database.Database
        self.database = database
        self.enabled = True
        self.pause = 0

        #map normalizers
        for n in basenormalizer.BaseNormalizer.__subclasses__():
            normalizer = n()
            for channel in normalizer.channels:
                if channel in self.normalizers:
                    raise Exception('Only one normalizer for each channel allowed (%s).' % (channel,))
                else:
                    self.normalizers[channel] = normalizer

    def start_processing(self, warn_no_normalizers):
        while self.enabled:

            #Usefull to pause inserts while doing db resets.
            if self.pause > 0:
                gevent.sleep(self.pause)
                self.pause = 0

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
                    logging.warning('Failed to normalize and import item with hpfeed id = %s, channel = %s. (%s)' % (hpfeed_item['_id'], hpfeed_item['channel'], ex))

            if warn_no_normalizers:
                if chan_no_normalizer:
                    for key, value in chan_no_normalizer.items():
                        logging.warning('No normalizer could be found for %s. (Repeated %i times).' % (key, value))

            gevent.sleep(3)
        logging.info("Mnemosyne stopped")


    def pause(self, seconds):
        self.pause = seconds

    def stop(self):
        self.enabled = False

