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
from bson.objectid import ObjectId

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

    @route('/hpfeeds')
    @route('/hpfeeds/')
    def hpfeeds_get_all():
        """
        /hpfeeds - returns 403
        /hpfeeds - returns 403
        /hpfeeds/?channel=channelname - returns 100 latest entries pulled from 'channelname'
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
        if 'channel' in query_keys:
            result = list(MnemoWebAPI.db.hpfeed.find({'channel': request.query.channel}).sort('timestamp', -1).limit(100))
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
        return MnemoWebAPI.jsonify(result, response)

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

    @route('/sessions/honeypots')
    def session_honeypots():
        """
        Returns a grouped list of types of honeypots which has submitted data.
        Example:
        {"honeypots": [{"count": 720, "honeypot": "Glastopf"}]}
        """
        result = MnemoWebAPI.simpel_group('session', 'honeypot')
        return MnemoWebAPI.jsonify(result, response)

    @route('/urls')
    @route('/urls/')
    def urls_all():
        """
        Returns a list of url's reported by honeyclients (in general) with reference to the original hpfeeds data..
        Example:
        {
        "urls": [
            {
                "url": "http://inutterod.ru/count22.php",
                "_id": "50db96fa2c533872c1ba0d26",
                "hpfeed_ids": [
                    "50da8260dfe0f7b2c68c2fde"
                ]
            },
            {
                "url": "http://www.jotto-to.xx/images/M_images/t?%0D?",
                "_id": "50db96fa2c533872c1ba0d27",
                "hpfeed_ids": [
                    "50dad02bdfe0f7b4f48cd434",
                    "50dad0a6dfe0f7b4f48cd435"
                ]
            }
        }
        """
        result = list(MnemoWebAPI.db['url'].find())
        return MnemoWebAPI.jsonify({'urls': result}, response)

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
            json_response = json.dumps(i, default=MnemoWebAPI.json_default)
            #Set content type only if serialization succesful
            r.content_type = 'application/json'
            return json_response
        else:
            print i
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
