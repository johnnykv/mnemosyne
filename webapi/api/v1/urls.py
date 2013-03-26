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

from bottle import get, abort, request, response, HTTPError
from cork import AAAException
from helpers import jsonify
from app import app
from app import auth


@app.get('/urls')
@app.get('/urls/')
def urls(mongodb):
    try:
        auth.require(role='access_normalized')
    except AAAException as e:
        return HTTPError(401, e.message)

    query_keys = request.query.keys()
    query_dict = {}

    if 'limit' in query_keys:
        limit = int(request.query.limit)
    else:
        limit = 50

    if 'url_regex' in query_keys:
        query_dict['url'] = {'$regex': request.query.url_regex}

    if 'hash' in query_keys:
        hash_length = len(request.query['hash'])
        if hash_length is 128:
            query_dict['extractions.hashes.sha512'] = request.query['hash']
        elif hash_length is 40:
            query_dict['extractions.hashes.sha1'] = request.query['hash']
        elif hash_length is 32:
            query_dict['extractions.hashes.md5'] = request.query['hash']
        else:
            abort(400, '{0} could not be recognized as a supported hash. Currently supported hashes are: SHA1, SHA512 and MD5. ')

    result = list(mongodb['url'].find(query_dict).limit(limit))
    return jsonify({'urls': result}, response)
