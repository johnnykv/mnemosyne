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

from bottle import abort, HTTPError
from cork import AAAException, AuthException
from datetime import datetime
from bson import ObjectId
from bson.code import Code

import json
import uuid


def simple_group(collection, attribute, mongodb):
    """
    Helper method to ease group_by operations.
    """
    #Disabled due to bringing the system down
    reducer = Code("""
        function (current, result) { result.count += 1; }
        """)
    #TODO: Convert to map/reduce. (current state sets read-lock)
    result = mongodb[collection].group(key={attribute: 1}, condition={}, initial={"count": 0}, reduce=reducer)
    output_rootname = attribute + 's'
    #Why does pymongo return the aggregation as float?
    for item in result:
        item['count'] = int(item['count'])
    return {output_rootname: result}


def jsonify(i, r):
    if i is None:
        i = {}
    if isinstance(i, dict):
        #Attempt to serialize, raises exception on failure
        json_response = json.dumps(i, default=json_default, sort_keys=True)
        #Set content type only if serialization succesful
        r.content_type = 'application/json'
        return json_response
    else:
        abort(500, 'Error while trying to serialize to json.')


def json_default(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, buffer):
        return str(obj)
    elif isinstance(obj, ObjectId):
        return str(obj)
    else:
        return None

