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

from bottle import response, get
from helpers import jsonify, simple_group
from datetime import date, datetime
from app import app
from app import auth


@app.get('/aux/dorks')
def get_dorks(mongodb):
    auth.require(fail_redirect='/looser')
    result = list(mongodb['dork'].find())
    for entry in result:
        entry['firsttime'] = entry['_id'].generation_time
        del entry['_id']

    return jsonify({'dorks': result}, response)
