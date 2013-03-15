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
import string
import time
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from bson.errors import InvalidStringData
import threading

logger = logging.getLogger(__name__)


class MnemoDB(object):
    def __init__(self, database_name):
        logger.info('Connecting to mongodb, using "{0}" as database.'.format(database_name))
        conn = MongoClient(auto_start_request=False)
        self.db = conn[database_name]
        self.ensure_index()
        self.being_processed = {}
        self.hpfeed_lock = threading.Lock()

    def ensure_index(self):
        self.db.hpfeed.ensure_index('normalized', unique=False)
        self.db.hpfeed.ensure_index('last_error', unique=False)
        self.db.url.ensure_index('url', unique=True)
        self.db.file.ensure_index('hashes', unique=True)
        self.db.dork.ensure_index('content', unique=False)
        self.db.session.ensure_index('protocol', unique=False)
        self.db.session.ensure_index('source_ip', unique=False)
        self.db.session.ensure_index('source_port', unique=False)
        self.db.session.ensure_index('destination_ip', unique=False)
        self.db.session.ensure_index('source_port', unique=False)
        self.db.session.ensure_index('honeypot', unique=False)
        self.db.session.ensure_index('timestamp', unique=False)

    def insert_normalized(self, ndata, hpfeed_id):
        assert isinstance(hpfeed_id, ObjectId)
        #ndata is a collection of dictionaries
        for item in ndata:
            #key = collection name, value = content
            for collection, document in item.items():
                if collection is 'url':
                    if 'extractions' in document:
                        self.db[collection].update({'url': document['url']},
                                                   {'$pushAll': {'extractions': document['extractions']},
                                                    '$push': {'hpfeeds_ids': hpfeed_id}},
                                                   upsert=True)
                    else:
                        self.db[collection].update({'url': document['url']}, {'$push': {'hpfeeds_ids': hpfeed_id}},
                                                   upsert=True)
                elif collection is 'file':
                    self.db[collection].update({'hashes.sha512': document['hashes']['sha512']},
                                               {'$set': document, '$push': {'hpfeed_ids': hpfeed_id}},
                                               upsert=True)
                elif collection is 'session':
                    document['hpfeed_id'] = hpfeed_id
                    self.db[collection].insert(document)
                elif collection is 'dork':
                    self.db[collection].update({'content': document['content'], 'type': document['type']},
                                               {'$set': {'lasttime': document['timestamp']},
                                                '$inc': {'count': document['count']}},
                                               upsert=True)
                else:
                    raise Warning('{0} is not a know collection type.'.format(collection))
            #if we end up here everything if ok - setting hpfeed entry to normalized
            if hpfeed_id in self.being_processed:
                del self.being_processed[hpfeed_id]
        self.db.hpfeed.update({'_id': hpfeed_id}, {'$set': {'normalized': True},
                                                   '$unset': {'last_error': 1, 'last_error_timestamp': 1}})

    def insert_hpfeed(self, ident, channel, payload):
        #thanks rep!
        #mongo can't handle non-utf-8 strings, therefore we must encode
        #raw binaries
        if [i for i in payload[:20] if i not in string.printable]:
            payload = str(payload).encode('hex')
        else:
            payload = str(payload)

        entry = {'channel': channel,
                 'ident': ident,
                 'payload': payload,
                 'timestamp': datetime.utcnow(),
                 'normalized': False}
        try:
            self.db.hpfeed.insert(entry)
        except InvalidStringData as err:
            logger.error(
                'Failed to insert hpfeed data on {0} channel due to invalid string data. ({1})'.format(entry['channel'],
                                                                                                       err))

    def hpfeed_set_errors(self, items):
        for item in items:
            if item['_id'] in self.being_processed:
                del self.being_processed['_id']
            self.db.hpfeed.update({'_id': item['_id']},
                                  {'$set':
                                       {'last_error': str(item['last_error']),
                                        'last_error_timestamp': item['last_error_timestamp']}
                                  })

    def get_hpfeed_data(self, max=250):
        #entries which are not normalized and not in error state
        with self.hpfeed_lock:
            data = list(self.db.hpfeed.find({'normalized': False, 'last_error': {'$exists': False}}, limit=max))
            for d in data:
                self.being_processed[d['_id']] = 1
        return data

    def reset_normalized(self):
        """
        Deletes all normalized data from the mongo instance.
        """
        logger.info('Initiating database reset - all normalized data will be deleted. (Starting timer)')
        start = time.time()
        for collection in self.db.collection_names():
            if collection not in ['system.indexes', 'hpfeed', 'hpfeeds']:
                logger.warning('Dropping collection: {0}.'.format(collection))
                self.db.drop_collection(collection)
        logger.info('All collections dropped. (Elapse: {0})'.format(time.time() - start))
        self.db.hpfeed.update({}, {"$set": {'normalized': False},
                                   '$unset': {'last_error': 1, 'last_error_timestamp': 1}},
                                  multi=True)
        logger.info('Error states removed from hpfeeds data (Elapse: {0}'.format(time.time() - start))
        self.ensure_index()
        logger.info('Done ensuring indexes (Elapse: {0})'.format(time.time() - start))
        logger.info('Full reset done in {0} seconds'.format(time.time() - start))

    def collection_count(self):
        result = {}
        for collection in self.db.collection_names():
            if collection not in ['system.indexes']:
                count = self.db[collection].count()
                result[collection] = count
        return result

    def get_hpfeed_error_count(self):
        count = self.db.hpfeed.find({'last_error': {'$exists': 1}}).count()
        return count
