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

from bottle import route, run, abort, Bottle, request, response, static_file, get

from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId
from bson.code import Code
from datetime import datetime, date

import bson
import os

import json
import uuid


class MnemoWebAPI(Bottle):
    """Exposes raw and normalized data from hpfeeds through a RESTful api"""

    def __init__(self, datebase_name):
        super(MnemoWebAPI, self).__init__(autojson=False)
        conn = MongoClient()
        MnemoWebAPI.db = conn[datebase_name]

    def start_listening(self, host, port):
        run(host=host, port=port, debug=False, server='paste', quiet=True)

    @route('/api/hpfeeds/')
    @route('/api/hpfeeds')
    def hpfeeds():
        query_keys = request.query.keys()
        query_dict = {}

        mongo_keys = set(('_id', 'id', 'channel'))

        #intersection
        common_keys = (set(query_keys) & mongo_keys)

        try:
            for item in common_keys:
                if item.endswith('_id'):
                    query_dict[item] = ObjectId(request.query[item])
                elif item == 'id':
                    query_dict['_' + item] = ObjectId(request.query[item])
                else:
                    query_dict[item] = request.query[item]
        except InvalidId:
            abort(400, 'Not a valid ObjectId.')

        if 'limit' in query_keys:
            limit = int(request.query.limit)
        else:
            limit = 50

        result = list(MnemoWebAPI.db.hpfeed.find(query_dict).sort('timestamp', -1).limit(limit))
        return MnemoWebAPI.jsonify({'hpfeeds': result}, response)

    @route('/api/hpfeeds/channels')
    def channels():
        """
        Returns a list of channel names and number of events in the immutable hpfeeds store.
        Example:
        {"channels": [{"count": 1206, "name": "glastopf.events"},
                      {"count": 4, "name": "glastopf.files"},
                       "count": 511, "name": "thug.events"}]
        """
        result = MnemoWebAPI.simpel_group('hpfeed', 'channel')
        return MnemoWebAPI.jsonify(result, response)

    @route('/api/sessions')
    def sessions_get_by_query():

        query_keys = request.query.keys()
        query_dict = {}

        mongo_keys = set(('id', '_id', 'protocol', 'source_ip', 'source_port', 'destination_ip',
                          'destination_port', 'honeypot'))

        #intersection
        common_keys = (set(query_keys) & mongo_keys)

        for item in common_keys:
            if item.endswith('_id'):
                query_dict[item] = ObjectId(request.query[item])
            elif item is 'id':
                query_dict['_' + item] = ObjectId(request.query[item])
            elif item.endswith('_port'):
                query_dict[item] = int(request.query[item])
            else:
                query_dict[item] = request.query[item]

        if 'limit' in query_keys:
            limit = int(request.query.limit)
        else:
            limit = 50

        result = list(MnemoWebAPI.db.session.find(query_dict).limit(limit))
        return MnemoWebAPI.jsonify({'sessions': result}, response)

    @route('/api/sessions/protocols')
    def session_protocols():
        """
        Returns a grouped list of all protocols intercepted.
        Example:
        {"protocols": [{"count": 680, "protocol": "http"},
                       {"count": 125, "protocol": "ssh},
                       {"count": 74,  "protocol": "imap}]}
        """
        result = MnemoWebAPI.simpel_group('session', 'protocol')
        return MnemoWebAPI.jsonify(result, response)

    @route('/api/urls')
    @route('/api/urls/')
    def urls():

        query_keys = request.query.keys()
        query_dict = {}

        if 'limit' in query_keys:
            limit = int(request.query.limit)
        else:
            limit = 50

        if 'url_regex' in query_keys:
            query_dict['url'] = {'$regex': request.query.url_regex}

        if 'hash' in query_keys:
            hash_length = len(query_dict['hash'])
            if hash_length is 128:
                query_dict['hash.sha512'] = query_dict['hash']
            elif hash_length is 40:
                query_dict['hash.sha1'] = query_dict['hash']
            elif hash_length is 32:
                query_dict['hash.md5'] = query_dict['hash']
            else:
                abort((400), '{0} could be recognized as a supported hash. Currently supported hashes are: SHA1, SHA512 and MD5. ')

        result = list(MnemoWebAPI.db['url'].find(query_dict).limit(limit))
        return MnemoWebAPI.jsonify({'urls': result}, response)

    @route('/api/files')
    @route('/api/files/')
    def get_files():
        query_keys = request.query.keys()
        query_dict = {}

        if 'limit' in query_keys:
            limit = int(request.query.limit)
        else:
            limit = 50

        if 'hash' in query_keys:
            hash_length = len(request.query['hash'])
            if hash_length is 128:
                query_dict['hashes.sha512'] = request.query['hash']
            elif hash_length is 40:
                query_dict['hashes.sha1'] = request.query['hash']
            elif hash_length is 32:
                print "md5"
                query_dict['hashes.md5'] = request.query['hash']
            else:
                abort((400), '{0} could be recognized as a supported hash. Currently supported hashes are: SHA1, SHA512 and MD5. ')
        else:
            abort((400), 'Only supported query parameter is "hash"')
        print query_dict
        result = list(MnemoWebAPI.db.file.find(query_dict).limit(50))
        return MnemoWebAPI.jsonify({'files': result}, response)

    @route('/api/files/types')
    def files_types():
        result = MnemoWebAPI.simpel_group('file', 'content_guess')
        return MnemoWebAPI.jsonify(result, response)

    @route('/api/helpers/get_hpfeeds_stats')
    def get_hpfeed_stats():
        result = MnemoWebAPI.db.hpfeed.aggregate({'$group': {'_id': {'$dayOfYear': '$timestamp'}, 'count': {'$sum': 1}}})
        del result['ok']
        for item in result['result']:
            d = datetime.strptime(str(item['_id']), '%j')
            #carefull around newyear! ;-)
            d = d.replace(date.today().year)
            item['_id'] = d

        return MnemoWebAPI.jsonify(result, response)

    @get('/')
    def get_index():
        return static_file('index.html', root='webapi/static')

    @get('/<filename:path>')
    def static(filename):
        return static_file(filename, root='webapi/static')

    @staticmethod
    def simpel_group(collection, attribute):
        """
        Helper method to ease group_by operations.
        """
        reducer = Code("""
            function (current, result) { result.count += 1; }
            """)
        #TODO: Convert to map/reduce. (current state sets read-lock)
        result = MnemoWebAPI.db[collection].group(key={attribute: 1}, condition={}, initial={"count": 0}, reduce=reducer)
        output_rootname = attribute + 's'
        #Why does pymongo return the aggregation as float?
        for item in result:
            item['count'] = int(item['count'])
        return {output_rootname: result}

    @staticmethod
    def jsonify(i, r):
        if isinstance(i, dict):
            #Attempt to serialize, raises exception on failure
            json_response = json.dumps(i, default=MnemoWebAPI.json_default, sort_keys=True)
            #Set content type only if serialization succesful
            r.content_type = 'application/json'
            return json_response
        else:
            abort(500, 'Error while trying to serialize to json.')

    @staticmethod
    def json_default(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, uuid.UUID):
            return str(obj)
        elif isinstance(obj, buffer):
            return str(obj)
        elif isinstance(obj, bson.objectid.ObjectId):
            return str(obj)
        else:
            return None
