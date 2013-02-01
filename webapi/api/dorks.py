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

from bottle import response, get, request
from helpers import jsonify, simple_group
from datetime import date, datetime
from app import app
from app import auth


@app.get('/aux/dorks')
def get_dorks(mongodb):
    auth.require(fail_redirect='/looser')
    query_keys = request.query.keys()
    query_dict = {}

    if 'regex' in query_keys:
        query_dict['content'] = {'$regex': request.query.regex}

    #inurl, intitle, etc.
    if 'type' in query_keys:
        query_dict['type'] = request.query.type

    if 'limit' in query_keys:
            limit = int(request.query.limit)
    else:
        limit = 200

    result = list(mongodb['dork'].find(query_dict).sort('count', -1).limit(limit))
    #delete mongo _id - better way?
    for entry in result:
        entry['firsttime'] = entry['_id'].generation_time
        del entry['_id']

    return jsonify({'dorks': result}, response)
