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

import bottle
import shared_state
from bottle import run, install, mount
from bottle.ext import mongo
from beaker.middleware import SessionMiddleware


class MnemoWebAPI():
    """Exposes raw and normalized data from hpfeeds through a RESTful api"""

    def __init__(self, datebase_name, static_file_path=None):
        shared_state.static_dir = static_file_path
        shared_state.plug = bottle.ext.mongo.MongoPlugin(uri="localhost", db=datebase_name, json_mongo=True)
        #install mongo plugin for root app
        install(shared_state.plug)

        #load devel api
        from webapi.api import app as develapp
        mount('/api/', develapp.app)

        #must be imported AFTER mounts.
        if shared_state.static_dir != None:
            import servestatic

        #wrap root app in beaker middleware
        session_opts = {
            'session.type': 'file',
            'session.cookie_expires': 300,
            'session.data_dir': './data',
            'session.auto': True,
            #set secure attribute on cookie
            'session.secure': True
            }
        self.app = SessionMiddleware(bottle.app(), session_opts)


    def start_listening(self, host, port):
        run(app=self.app, host=host, port=port, debug=True, server='paste', quiet=True)