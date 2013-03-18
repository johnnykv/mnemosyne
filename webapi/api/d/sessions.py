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

from bottle import response, request, HTTPError
from cork import AAAException
from bson import ObjectId
from helpers import simple_group, jsonify
from app import app
from app import auth


@app.get('/sessions')
def sessions_get_by_query(mongodb):
    try:
        auth.require(role='access_normalized')
    except AAAException as e:
        return HTTPError(401, e.message)

    query_keys = request.query.keys()
    query_dict = {}

    mongo_keys = {'id', '_id', 'protocol', 'source_ip', 'source_port', 'destination_ip', 'destination_port', 'honeypot'}

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

    #remove ip of honeypot if user is not authorized to see it
    u = auth.current_user.role
    lvl = auth._store.roles[u]
    needed_lvl = auth._store.roles['access_normalized']

    p_limit = {'_id': False}
    if lvl < needed_lvl:
        p_limit = {'destination_ip': False}

    result = list(mongodb['session'].find(spec=query_dict, fields=p_limit).limit(limit))
    return jsonify({'sessions': result}, response)


@app.get('/sessions/protocols')
def session_protocols(mongodb):
    """
    Returns a grouped list of all protocols intercepted.
    Example:
    {"protocols": [{"count": 680, "protocol": "http"},
                   {"count": 125, "protocol": "ssh},
                   {"count": 74,  "protocol": "imap}]}
    """
    auth.require(role='access_normalized')
    result = simple_group('session', 'protocol', mongodb)
    return jsonify(result, response)
