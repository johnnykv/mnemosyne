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

from bottle import route, run, abort, Bottle, request, response

from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId
from bson.code import Code
import bson

import datetime
import json
import uuid


class MnemoWebAPI(Bottle):
    """Exposes raw and normalized data from hpfeeds through a RESTful api"""

    def __init__(self, datebase_name):
        super(MnemoWebAPI, self).__init__(autojson=False)
        conn = MongoClient()
        MnemoWebAPI.db = conn[datebase_name]

    def start_listening(self, host, port):
        run(host=host, port=port, debug=True)

    @route('/hpfeeds/')
    @route('/hpfeeds')
    def hpfeeds_get_all():
        """
        /hpfeeds/channel/glastopf.events - returns 100 latest entries pulled from 'channelname'
        Example:
        {
        "hpfeeds": [
            {
                "ident": "2l3if@hp8",
                "timestamp": "2012-12-26T20:01:46.908000",
                "normalized": true,
                "_id": "5deadbeef0e0f7b874e8088d",
                "payload": "<payload>",
                "channel": "glastopf.events"
            },
            {
                "ident": "2l3if@hp8",
                "timestamp": "2012-12-26T20:05:32.773000",
                "normalized": false,
                "_id": "50db57aadfe0f7b8deadbeef",
                "payload": "<payload>",
                "channel": "glastopf.events"
            }]
        }
        """
        query_keys = request.query.keys()

        if 'limit' in query_keys:
            limit = int(request.query.limit)
        else:
            limit = 50

        if 'channel' in query_keys:
            result = list(MnemoWebAPI.db.hpfeed.find({'channel': request.query.channel}).sort('timestamp', -1).limit(limit))
            return json.dumps({'hpfeeds': result}, default=MnemoWebAPI.json_default)
        else:
            abort(403, 'Listing of all content forbidden.')

    @route('/hpfeeds/<hpfeed_id>')
    def hpfeeds_by_id(hpfeed_id):
        """
        Returns a specific hpfeed entry.
        Example:
        {
            "ident": "2l3if@hp8",
            "timestamp": "2012-12-26T19:49:22.212000",
            "normalized": true,
            "_id": "50dbdeadbeeff7b874e806ba",
            "payload": "<payload>",
            "channel": "glastopf.events"
        }
        """
        try:
            result = MnemoWebAPI.db.hpfeed.find_one({'_id': ObjectId(hpfeed_id)})
        except InvalidId:
            abort(400, '{0} is not a valid ObjectId.'.format(hpfeed_id))
        return MnemoWebAPI.jsonify(result, response)

    @route('/hpfeeds/channels')
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

    @route('/sessions/<session_id>')
    def sessions_by_id(session_id):
        """
        Returns a specific sessions entry.
        Example:
        {
            ...
        }
        """
        try:
            result = MnemoWebAPI.db.session.find_one({'_id': ObjectId(session_id)})
        except InvalidId:
            abort(400, '{0} is not a valid ObjectId.'.format(session_id))
        return MnemoWebAPI.jsonify({'sessions': result}, response)

    @route('/sessions/protocols')
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

    @route('/sessions')
    def sessions_get_by_query():

        query_keys = request.query.keys()
        query_dict = {}

        mongo_keys = set(('protocol', 'source_ip', 'source_port', 'destination_ip',
                          'destination_port', 'honeypot'))

        #intersection
        common_keys = (set(query_keys) & mongo_keys)

        for item in common_keys:
            if item.endswith('_port'):
                query_dict[item] = int(request.query[item])
            else:
                query_dict[item] = request.query[item]

        if 'limit' in query_keys:
            limit = int(request.query.limit)
        else:
            limit = 50

        print query_dict
        result = list(MnemoWebAPI.db.session.find(query_dict).limit(limit))
        return MnemoWebAPI.jsonify({'sessions': result}, response)

    @route('/urls')
    @route('/urls/')
    def urls():

        query_keys = request.query.keys()
        query_dict = {}

        if 'limit' in query_keys:
            limit = int(request.query.limit)
        else:
            limit = 50

        if 'url_regex' in query_keys:
            query_dict['url'] = {'$regex': request.query.url_regex}

        result = list(MnemoWebAPI.db['url'].find(query_dict).limit(limit))
        return MnemoWebAPI.jsonify({'urls': result}, response)

    @route('/files/types')
    def files_types():
        result = MnemoWebAPI.simpel_group('file', 'content_guess')
        return MnemoWebAPI.jsonify(result, response)

    @route('/files/<the_hash>')
    def file_search_by_hash(the_hash):
        hash_length = len(the_hash)
        result = ""
        if hash_length is 128:
            result = list(MnemoWebAPI.db.file.find({'hash.sha512': the_hash}))
        elif hash_length is 40:
            result = list(MnemoWebAPI.db.file.find({'hashes.sha1': the_hash}))
        elif hash_length is 32:
            result = list(MnemoWebAPI.db.file.find({'hashes.md5': the_hash}))
        return MnemoWebAPI.jsonify({'files': result}, response)

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
            if isinstance(obj, datetime.datetime):
                return obj.isoformat()
            elif isinstance(obj, uuid.UUID):
                return str(obj)
            elif isinstance(obj, buffer):
                return str(obj)
            elif isinstance(obj, bson.objectid.ObjectId):
                return str(obj)
            else:
                return None
