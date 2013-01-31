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
from datetime import datetime
from cork import Cork
import shared_state as shared

from cork import Cork, AAAException, AuthException
from cork import Mailer

class MnemoWebAPI():
    """Exposes raw and normalized data from hpfeeds through a RESTful api"""

    def __init__(self, datebase_name, static_file_path=None, auth_dir='./data/auth'):
        app = bottle.app()
        app.catchall = True
        shared.static_dir = static_file_path
        shared.plug = bottle.ext.mongo.MongoPlugin(uri="localhost", db=datebase_name, json_mongo=True)
        #install mongo plugin for root app
        install(shared_state.plug)

        shared.auth = Cork('./data/auth')

        #load devel api
        from webapi.api import app as develapp
        #develapp.auth = shared_state.auth
        print "------"
        print develapp.auth
        mount('/api/', develapp.app)

        #must be imported AFTER mounts.
        if shared.static_dir != None:
            import default_routes

        #wrap root app in beaker middleware
        session_opts = {
            'session.type': 'file',
            'session.cookie_expires': 300,
            'session.data_dir': './data/beaker',
            'session.auto': True,
            #set secure attribute on cookie
            'session.secure': True
            }

        self.app = SessionMiddleware(app, session_opts)


    def start_listening(self, host, port):
        run(app=self.app, host=host, port=port, debug=True, server='paste', quiet=True)

    def populate_conf_directory(self, auth_dir):
        """
        Creation of basic auth files.
        """
        cork = Cork(auth_dir, initialize=True)

        cork._store.roles['admin'] = 100
        cork._store.roles['hp_member'] = 60
        cork._store.save_roles()

        tstamp = str(datetime.utcnow())

        #default admin combo: admin/admin
        username = password = 'admin'
        cork._store.users[username] = {
            'role': 'admin',
            'hash': cork._hash(username, password),
            'email_addr': username + '@localhost.local',
            'desc': username + ' test user',
            'creation_date': tstamp
        }

        #default admin combo: hp/hp
        username = password = 'hp'
        cork._store.users[username] = {
            'role': 'hp_member',
            'hash': cork._hash(username, password),
            'email_addr': username + '@localhost.local',
            'desc': username + ' test user',
            'creation_date': tstamp
        }
        cork._store.save_users()


#for debugging
if __name__ == '__main__':

    m = MnemoWebAPI('mnemosyne')
    m.start_listening(host='localhost', port='8181')