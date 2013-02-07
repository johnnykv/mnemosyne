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

import unittest
import uuid
from bson.objectid import ObjectId
from persistance import mnemodb
from pymongo import MongoClient
from datetime import datetime, timedelta


class MnemodbTests(unittest.TestCase):
    def setUp(self):
        """
        Generate new db name for each test.
        """
        self.dbname = str(uuid.uuid4())

    def tearDown(self):
        connection = MongoClient('localhost', 27017)
        connection.drop_database(self.dbname)
        connection.drop_database(self.dbname)

    def test_insert_hpfeed(self):
        """
        Test correct insertion of raw hpfeed entry into mongodb.
        """
        sut = mnemodb.MnemoDB(self.dbname)

        #ident, channel, payload
        insert_items = [
            ('ident1', 'testchannel1', 'payload1'),
            ('ident2', 'testchannel2', 'payload2'),
            ('ident3', 'testchannel3', 'payload3')
        ]

        for item in insert_items:
            sut.insert_hpfeed(item[0], item[1], item[2])

        #Check that the hpfeed collection has the correct amount of items
        db = MongoClient('localhost', 27017)[self.dbname]
        actual = list(db.hpfeed.find())
        #TODO: assert content of actual
        self.assertEqual(len(insert_items), len(actual))

    def test_reset(self):
        """
        Check if all normalized collections get dropped and that normalized is set to False in
        all hpfeed entries.
        """

        db = MongoClient('localhost', 27017)[self.dbname]

        #prepare and insert dummy values directly into the hpfeed collection
        insert_items = [
            {'channel': 'channel1', 'ident': 'ident1', 'payload': 'payload1', 'timestamp': datetime.utcnow(),
             'normalized': True},
            {'channel': 'channel2', 'ident': 'ident2', 'payload': 'payload2', 'timestamp': datetime.utcnow(),
             'normalized': True},
            {'channel': 'channel3', 'ident': 'ident3', 'payload': 'payload3', 'timestamp': datetime.utcnow(),
             'normalized': True, 'last_error': "Some error", 'last_error_timestamp': datetime.now()}
        ]

        for item in insert_items:
            db['hpfeed'].insert(item)
            #create a few dummy collection that we expect to get dropped
        db['somecollection1'].insert({'something': 'something'})
        db['somecollection2'].insert({'something': 'something'})

        sut = mnemodb.MnemoDB(self.dbname)
        #This is the function we are testing
        sut.reset_normalized()

        #has normalized collections been removed
        self.assertNotIn('somecollection1', db.collection_names())
        self.assertNotIn('somecollection2', db.collection_names())

        #has all normalized been set to True
        self.assertEquals(0, db['hpfeed'].find({'normalized': True}).count())
        #has last_error attribute been removed
        self.assertEquals(0, db['hpfeed'].find({'last_error': {'$exists': 1}}).count())
        #has last_error_timestamp attribute been removed
        self.assertEquals(0, db['hpfeed'].find({'last_error_timestamp': {'$exists': 1}}).count())



    def test_insert_dorks(self):
        """
        Test insertion into the dorks collection.
        """
        sut = mnemodb.MnemoDB(self.dbname)

        insert_items = [
            {'dork':
                 {'type': 'inurl', 'content': '/somedork.php', 'count': 1, 'timestamp': datetime.now()}},
            {'dork':
                 {'type': 'inurl', 'content': '/somedork.php', 'count': 1, 'timestamp': datetime.now()}},
            {'dork':
                 {'type': 'inurl', 'content': '/otherdork.php', 'count': 1, 'timestamp': datetime.now()}},
        ]

        sut.insert_normalized(insert_items, ObjectId())

        db = MongoClient('localhost', 27017)[self.dbname]

        #we expect two entries in the database
        db_entries = db['dork'].find().count()
        self.assertEqual(2, db_entries)

        result_one = db['dork'].find_one({'content': '/somedork.php'})
        self.assertIn('lasttime', result_one)
        self.assertEqual(2, result_one['count'])
        self.assertEqual('inurl', result_one['type'])

        result_one = db['dork'].find_one({'content': '/otherdork.php'})
        self.assertIn('lasttime', result_one)
        self.assertEqual(1, result_one['count'])
        self.assertEqual('inurl', result_one['type'])

    def test_set_errors(self):
        """
        Test that error state is correctly set in the specified hpfeed entries.
        """

        #the entry we are going to manipulate
        o = ObjectId()
        insert_items = [
            {'channel': 'channel1', 'ident': 'ident1', 'payload': 'payload1', 'timestamp': datetime.utcnow(),
             'normalized': True},
            {'_id': o, 'channel': 'channel2', 'ident': 'ident2', 'payload': 'payload2', 'timestamp': datetime.utcnow(),
             'normalized': True},
            {'channel': 'channel3', 'ident': 'ident3', 'payload': 'payload3', 'timestamp': datetime.utcnow(),
             'normalized': True}
                ]

        db = MongoClient('localhost', 27017)[self.dbname]

        for item in insert_items:
            db['hpfeed'].insert(item)

        sut = mnemodb.MnemoDB(self.dbname)
        #set a single item in error state
        dt = datetime.now()
        sut.hpfeed_set_errors([ {'_id': o,
                               'last_error': "Some error message",
                               'last_error_timestamp': dt} ])

        #retrieve it again and check if the error state was set.
        r = db['hpfeed'].find_one({'_id': o})
        self.assertEqual('Some error message', r['last_error'])
        self.assertAlmostEqual(dt, r['last_error_timestamp'], delta=timedelta(seconds=1))

    def test_reset_errors_on_successful_normalization(self):
        """
        Test that error state is removed from hpfeed entries on successful normalizations.
        """

        #the entry we are going to manipulate
        o = ObjectId()



        db = MongoClient('localhost', 27017)[self.dbname]

        db['hpfeed'].insert( {'_id': o,
                              'channel': 'channel3', 'ident': 'ident3',
                              'payload': 'payload3', 'timestamp': datetime.utcnow(),
                              'normalized': False,
                              'last_error': 'Some error',
                              'last_error_timestamp': datetime.now()})

        sut = mnemodb.MnemoDB(self.dbname)

        #insert dummy url entry
        sut.insert_normalized([{'url': {'url': '/dummy/url'}}], o)

        #retrieve the item from the database
        r = db['hpfeed'].find_one({'_id': o})
        #check that stats is as expected
        self.assertTrue(r['normalized'])
        self.assertNotIn('last_error', r)
        self.assertNotIn('last_error_timestamp', r)



