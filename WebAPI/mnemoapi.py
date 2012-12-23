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

from sqlalchemy import select

from bottle import route, run, abort, Bottle

import datetime
import json
import uuid


class MnemoWebAPI(Bottle):
    """Exposes raw and normalized data from hpfeeds through a RESTful api"""

    def __init__(self, db):
        super(MnemoWebAPI, self).__init__()
        MnemoWebAPI.db = db
        run(host='localhost', port=8181, debug=True)

    @route('/hpfeeds')
    @route('/hpfeeds/')
    def hpfeeds_get_all():
        abort(403, 'Listing of all content forbidden.')

    @route('/hpfeeds/<hpfeed_id>')
    def hpfeeds_by_id(hpfeed_id):
        conn = MnemoWebAPI.db.engine.connect()
        table = MnemoWebAPI.db.tables['hpfeed']
        result = conn.execute(select([table], table.c.hpfeed_id == hpfeed_id)).fetchone()
        return json.dumps(dict(result), default=MnemoWebAPI.json_default)

    @route('/hpfeeds/channels')
    def channels():
        conn = MnemoWebAPI.db.engine.connect()
        table = MnemoWebAPI.db.tables['hpfeed']
        result = conn.execute(select([table.c.channel]).distinct())

        channels = []
        for i in result:
            channels.append(i['channel'])

        return json.dumps({'channels': channels}, default=MnemoWebAPI.json_default)

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
