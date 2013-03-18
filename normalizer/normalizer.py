# Copyright (C) 2013 Johnny Vestergaard <jkv@unixcluster.dk>
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

from modules import basenormalizer
from modules import glastopf_events
from modules import glastopf_files
from modules import thug_events
from modules import thug_files
from modules import kippo_events
from modules import dionaea_capture
from modules import dionaea_binary
from modules import beeswarm_hive
from bson import ObjectId

import gevent
from gevent.pool import Pool

import logging
import traceback

from xml.etree.ElementTree import ParseError

logger = logging.getLogger(__name__)


class Normalizer(object):
    def __init__(self, database):
        self.normalizers = {}
        #injected instance of database.Database
        self.database = database
        self.enabled = True

        #max number of concurrent mongodb inserters
        self.worker_pool = Pool(5)

        #map normalizers
        for n in basenormalizer.BaseNormalizer.__subclasses__():
            normalizer = n()
            for channel in normalizer.channels:
                if channel in self.normalizers:
                    raise Exception('Only one normalizer for each channel allowed (%s).'.format(channel))
                else:
                    self.normalizers[channel] = normalizer

    def start_processing(self, fetch_count=1500):

        oldest_id = ObjectId("ffffffffffffffffffffffff")
        while self.enabled:

            normalizations = 0
            error_list = []
            to_be_processed = self.database.get_hpfeed_data(oldest_id, fetch_count)
            to_be_inserted = []

            for hpfeed_item in to_be_processed:
                try:
                    channel = hpfeed_item['channel']
                    if hpfeed_item['_id'] < oldest_id:
                        oldest_id = hpfeed_item['_id']
                    if channel in self.normalizers:
                        norm = self.normalizers[channel].normalize(hpfeed_item['payload'],
                                                                   channel, hpfeed_item['timestamp'])

                        #batch up normalized items
                        to_be_inserted.append((norm, hpfeed_item['_id']))
                        normalizations += 1
                    else:
                        error_list.append({'_id': hpfeed_item['_id'],
                                           'last_error': "No normalizer found",
                                           'last_error_timestamp': datetime.now()})
                        logger.warning('No normalizer could be found for channel: {0}.'.format(channel))
                except Exception as err:
                    error_list.append({'_id': hpfeed_item['_id'],
                                       'last_error': err,
                                       'last_error_timestamp': datetime.now()})
                    logger.warning('Failed to normalize and import item with hpfeed id = {0}, channel = {1}. ({2}). '
                                    'Exception details has been stored in the database.'
                                    .format(hpfeed_item['_id'], hpfeed_item['channel'], err))

            if len(error_list) > 0:
                self.database.hpfeed_set_errors(error_list)

            if len(to_be_inserted):
                self.worker_pool.spawn(self.inserter, to_be_inserted)

            if normalizations is 0:
                oldest_id = ObjectId("ffffffffffffffffffffffff")
                gevent.sleep(3)

        gevent.joinall(self.worker_pool)
        logger.info("Normalizer stopped.")

    def inserter(self, to_be_inserted):
        for norm, id in to_be_inserted:
            self.database.insert_normalized(norm, id)

    def stop(self):
        self.enabled = False
