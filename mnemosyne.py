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

from datetime import datetime

from normalizers import basenormalizer
from normalizers import glastopf_events
from normalizers import glastopf_files
from normalizers import thug_events
from normalizers import thug_files
from normalizers import kippo_events
from normalizers import dionaea_capture
from normalizers import dionaea_binary

import gevent

import logging
import traceback

from xml.etree.ElementTree import ParseError

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
                    raise Exception('Only one normalizer for each channel allowed (%s).'.format(channel))
                else:
                    self.normalizers[channel] = normalizer

    def start_processing(self):
        while self.enabled:

            #Usefull to pause inserts while doing db resets.
            if self.pause > 0:
                gevent.sleep(self.pause)
                self.pause = 0

            insertions = 0
            error_list = []
            to_be_processed = self.database.get_hpfeed_data(500)

            for hpfeed_item in to_be_processed:
                #Remove this line when done!
                try:
                    channel = hpfeed_item['channel']
                    if channel in self.normalizers:
                        norm = self.normalizers[channel].normalize(hpfeed_item['payload'],
                                                                   channel, hpfeed_item['timestamp'])
                        self.database.insert_normalized(norm, hpfeed_item['_id'])
                        insertions += 1
                    else:
                        error_list.append({'_id': hpfeed_item['_id'],
                                           'last_error': "No normalizer found",
                                           'last_error_timestamp': datetime.now()})
                        logging.warning('No normalizer could be found for channel: {0}.'.format(channel))
                except (TypeError, ValueError, ParseError) as err:
                    error_list.append({'_id': hpfeed_item['_id'],
                                       'last_error': err,
                                       'last_error_timestamp': datetime.now()})
                    logging.warning('Failed to normalize and import item with hpfeed id = %s, channel = %s. (%s). '
                                    'Exception details has been stored in the database.'
                                    .format(hpfeed_item['_id'], hpfeed_item['channel'], err))

            if len(error_list) > 0:
                self.database.hpfeed_set_errors(error_list)

            if insertions is 0:
                gevent.sleep(3)
        logging.info("Mnemosyne stopped")

    def pause(self, seconds):
        self.pause = seconds

    def stop(self):
        self.enabled = False
