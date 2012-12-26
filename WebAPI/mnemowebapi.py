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

from bottle import route, run, abort, Bottle, request

from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId
from bson.code import Code

import datetime
import json
import uuid


class MnemoWebAPI(Bottle):
    """Exposes raw and normalized data from hpfeeds through a RESTful api"""

    def __init__(self, datebase_name):
        super(MnemoWebAPI, self).__init__()
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
        """
        query_keys = request.query.keys()
        if 'channel' in query_keys:
            result = list(MnemoWebAPI.db.hpfeed.find({'channel': request.query.channel}).sort('timestamp', -1).limit(100))
            for item in result:
                print item['timestamp']
            return json.dumps({'hpfeeds': result}, default=MnemoWebAPI.json_default)
        else:
            abort(403, 'Listing of all content forbidden.')

    @route('/hpfeeds/<hpfeed_id>')
    def hpfeeds_by_id(hpfeed_id):
        """
        Returns a specific hpfeed entry.
        Format of the return value will will be the
        """
        try:
            result = MnemoWebAPI.db.hpfeed.find_one({'_id': ObjectId(hpfeed_id)})
        except InvalidId:
            abort(400, '{0} is not a valid ObjectId.'.format(hpfeed_id))

        return json.dumps(dict(result), default=MnemoWebAPI.json_default)

    @route('/hpfeeds/channels')
    def channels():
        """
        Returns a list of channel names and number of events in the immutable hpfeeds store.
        Example:
        {"channels": [{"count": 1206, "name": "glastopf.events"},
                       "count": 511, "name": "thug.events"]}
        """
        return MnemoWebAPI.simpel_group('hpfeed', 'channel')

    @route('/sessions/protocols')
    def session_protocols():
        """
        Returns a grouped list of all protocols intercepted.
        Example:
        {"protocols": [{"count": 680, "protocol": "http"},
                       {"count": 125, "protocol": "ssh},
                       {"count": 74,  "protocol": "imap}]}
        """
        return MnemoWebAPI.simpel_group('session', 'protocol')

    @route('/sessions/honeypots')
    def session_honeypots():
        """
        Returns a grouped list of types of honeypots which has submitted data.
        Example:
        {"honeypots": [{"count": 720, "honeypot": "Glastopf"}]}
        """
        return MnemoWebAPI.simpel_group('session', 'honeypot')

    @staticmethod
    def simpel_group(collection, attribute):
        """
        Helper method to ease group_by operations.
        """
        reducer = Code("""
            function (current, result) { result.count += 1; }
            """)
        result = MnemoWebAPI.db[collection].group(key={attribute: 1}, condition={}, initial={"count": 0}, reduce=reducer)
        output_rootname = attribute + 's'
        return json.dumps({output_rootname: result}, default=MnemoWebAPI.json_default)

    @staticmethod
    def json_default(obj):
            if isinstance(obj, datetime.datetime):
                    return obj.isoformat()
            elif isinstance(obj, uuid.UUID):
                    return str(obj)
            elif isinstance(obj, buffer):
                    return str(obj)
            else:
                    return None
