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
import logging
from datetime import datetime

from pymongo import MongoClient

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates pre-aggregated reports.
    """

    def __init__(self, database_name):
        logger.info('Connecting to mongodb, using "{0}" as database.'.format(database_name))
        conn = MongoClient(w=0)
        self.db = conn[database_name]

    def hpfeeds(self, entry):
        hour = entry['timestamp'].hour
        date = entry['timestamp'].strftime('%Y%m%d')
        query = {'channel': entry['channel'], 'date': date}

        update = {'$inc': {'hourly.{0}'.format(hour): 1}}
        self.db.daily_stats.update(query, update, upsert=True)

        #update total document
        channel = entry['channel'].replace('.', '_')
        self.db.daily_stats.update({'_id': 'total'},
                                   {'$inc': {channel: 1}}, upsert=True)

    def do_legacy_hpfeeds(self):
        max_objectid = self.db.hpfeed.find({}, fields={'_id': 1}).sort('_id', -1).limit(1)[0]['_id']
        logger.info('Doing pre-aggregation of historic hpfeeds data.')
        result = self.db.hpfeed.find({'_id': {'$lte': max_objectid}}, fields=['channel', 'timestamp'])
        items = 0
        for item in result:
            self.hpfeeds(item)
            items += 1
        logger.info('Finished pre-aggregation of historic hpfeeds data. ({0} items.)'.format(items))

