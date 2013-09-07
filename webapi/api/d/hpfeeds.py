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

import bottle
from bottle import get, abort, request, response, HTTPError
from cork import AAAException
from bson import ObjectId
from bson.errors import InvalidId
from helpers import jsonify
from app import app
from app import auth


@app.get('/hpfeeds/')
@app.get('/hpfeeds')
def hpfeeds(mongodb):
    try:
        auth.require(role='access_all')
    except AAAException as e:
        return HTTPError(401, e.message)

    query_keys = request.query.keys()
    query_dict = {}

    mongo_keys = {'_id', 'id', 'channel'}

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

    result = list(mongodb['hpfeed'].find(query_dict).sort('timestamp', -1).limit(limit))
    return jsonify({'hpfeeds': result}, response)


@app.get('/hpfeeds/stats')
def hpfeeds(mongodb):
    try:
        auth.require(role='access_all')
    except AAAException as e:
        return HTTPError(401, e.message)

    if 'date' in request.query and 'channel' in request.query:
        query = {'date': request.query.date, 'channel': request.query.channel}
    elif 'date' in request.query:
        query = {'date': request.query.date}
    elif 'channel' in request.query:
        query = {'channel': request.query.channel}
    else:
        abort(404, 'muhaha')

    results = list(mongodb['daily_stats'].find(query))

    for result in results:
        del result['_id']

    return jsonify({'stats': results}, response)


@app.get('/hpfeeds/stats/total')
def hpfeeds(mongodb):
    try:
        auth.require(role='access_all')
    except AAAException as e:
        return HTTPError(401, e.message)

    tmp_result = mongodb['daily_stats'].find_one({'_id': 'total'})
    del tmp_result['_id']

    result = []
    for key, value in tmp_result.items():
        result.append({'channel': key, 'count': value})

    return jsonify({'stats': result}, response)