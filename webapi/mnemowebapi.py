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
import os
import uuid
import shared_state as shared
import logging
import types
from bottle import run, install, mount, request
from bottle.ext import mongo
from beaker.middleware import SessionMiddleware
from datetime import datetime
from kumo.loggly import Loggly
from cork import Cork

logger = logging.getLogger(__name__)

class MnemoWebAPI():
    """Exposes raw and normalized data from hpfeeds through a RESTful api"""

    def __init__(self, datebase_name, static_file_path=None, data_dir='./data', loggly_token=None):

        cork_dir = os.path.join(data_dir, 'cork')
        beaker_dir = os.path.join(data_dir, 'beaker')
        bottle.TEMPLATE_PATH.insert(0,'webapi/views/')

        #vars which must be visible across all webapi modules
        shared.static_dir = static_file_path
        shared.plug = bottle.ext.mongo.MongoPlugin(uri="localhost", db=datebase_name, json_mongo=True)

        #install mongo plugin for root app
        install(shared_state.plug)

        #check if cork files exists
        cork_files = ['users.json', 'roles.json', 'register.json']
        if not set(cork_files).issubset(set(os.listdir(cork_dir))):
            #if not, create them
            logger.info('Cork authentication files not found, creating new files.')
            shared.auth = self.populate_conf_directory(cork_dir)
        else:
            shared.auth = Cork(cork_dir)

        #admin depends on shared.auth
        import admin

        #import and mount api version 1 (stable)
        from webapi.api.v1 import app as api_v1
        mount('/api/v1/', api_v1.app)

        #import and mount development version (unstable)
        from webapi.api.d import app as api_d
        mount('/api/d/', api_d.app)

        #must be imported AFTER mounts.
        if shared.static_dir is not None:
            import default_routes

        #wrap root app in beaker middleware
        session_opts = {
            'session.type': 'file',
            'session.cookie_expires': False,
            'session.data_dir': beaker_dir,
            'session.auto': True,
            #set secure attribute on cookie
            'session.secure': True
            }

        self.app = bottle.app()
        if loggly_token:
            self.app = Loggly(bottle.app(), loggly_token)
        self.app = SessionMiddleware(self.app, session_opts)
        
        root_app = bottle.app()

        #setup logging hooks
        @root_app.hook('before_request')
        @api_d.app.hook('before_request')
        @api_v1.app.hook('before_request')
        def log_request():
            user_agent = ""
            if 'HTTP_USER_AGENT' in bottle.request.environ:
                user_agent = bottle.request.environ['HTTP_USER_AGENT']
            if 'REMOTE_ADDR' in bottle.request.environ:
                remote_addr = bottle.request.environ['REMOTE_ADDR']
            else:
                remote_addr = ""
            if 'beaker.session' in bottle.request.environ:
                session = bottle.request.environ.get('beaker.session')
                username = session.get('username', None)
            else:
                username = "None"
            logger.info("[{0}/{1}] {2} {3} ({4})".format(remote_addr, username, request.method, request.fullpath, user_agent))

        def return_text(self, e):
            return e.status

        #make sure error pages for API are pure text
        api_d.app.default_error_handler = types.MethodType(return_text, self)
        api_v1.app.default_error_handler = types.MethodType(return_text, self)

    def start_listening(self, host, port):
        logger.info('Starting web api, listening on {0}:{1}'.format(host, port))
        run(app=self.app, host=host, port=port, debug=False, server='gevent',
            log="wsgi", quiet=True, keyfile='server.key', certfile='server.crt')

    #defaults
    def populate_conf_directory(self, auth_dir):
        """
        Creation of basic auth files.
        """
        logger.info("Creating new authentication files, check STDOUT for the generated admin password.")
        cork = Cork(auth_dir, initialize=True)

        cork._store.roles['admin'] = 100
        cork._store.roles['access_all'] = 70
        cork._store.roles['access_normalized'] = 60
        cork._store.roles['public'] = 10
        cork._store.save_roles()

        tstamp = str(datetime.utcnow())

        #default admin combo: admin/admin
        username = 'admin'
        password = str(uuid.uuid4())
        cork._store.users[username] = {
            'role': 'admin',
            'hash': cork._hash(username, password),
            'email_addr': username + '@localhost.local',
            'desc': 'Default administrative account',
            'creation_date': tstamp
        }
        cork._store.save_users()
        #for security reasons we fdo not want this in the log files.
        print "A 'admin' account has been created with the password '{0}'".format(password)

        return cork


#for debugging
if __name__ == '__main__':

    m = MnemoWebAPI('mnemosyne')
    m.start_listening(host='localhost', port='8181')
