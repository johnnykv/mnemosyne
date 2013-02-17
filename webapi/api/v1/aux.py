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

from cork import AAAException
from helpers import jsonify, simple_group
from datetime import date, datetime
from bottle import response, HTTPError
from app import app
from app import auth

@app.get('/aux/get_hpfeeds_stats')
def get_hpfeed_stats(mongodb):
    try:
        auth.require(role='access_all')
    except AAAException as e:
        return HTTPError(401, e.message)

    result = mongodb['hpfeed'].aggregate({'$group': {'_id': {'$dayOfYear': '$timestamp'}, 'count': {'$sum': 1}}})
    del result['ok']
    for item in result['result']:
        d = datetime.strptime(str(item['_id']), '%j')
        #carefull around newyear! ;-)
        d = d.replace(date.today().year)
        item['date'] = d
        del item['_id']
        #item['_id'] = d
    return jsonify(result, response)


@app.get('/aux/get_hpfeeds_channels')
def get_hpfeed_channels(mongodb):
    """
    Returns a list of channel names and number of events in the immutable hpfeeds store.
    Example:
    {"channels": [{"count": 1206, "channel": "glastopf.events"},
                  {"count": 4, "channel": "glastopf.files"},
                   "count": 511, "channel": "thug.events"}]
    """
    try:
        auth.require(role='access_all')
    except AAAException as e:
        return HTTPError(401, e.message)

    result = simple_group('hpfeed', 'channel', mongodb)
    return jsonify(result, response)
