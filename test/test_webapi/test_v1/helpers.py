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
from bottle.ext import mongo
from beaker.middleware import SessionMiddleware
from cork import Cork
from webtest import TestApp
from datetime import datetime
import os
import webapi.shared_state as shared


def prepare_app(dbname, tmppath):

    #mock auth mechanism
    setup_dir(tmppath)
    shared.auth = MockedAdminCork(tmppath)
    #must be imported AFTER mocking
    from webapi.api.v1 import app

    a = app.app
    #when unittesting we want exceptions to break stuff
    a.catchall = False


    for plug in a.plugins:
        if isinstance(plug, bottle.ext.mongo.MongoPlugin):
            a.uninstall(plug)

    plugin = bottle.ext.mongo.MongoPlugin(uri="localhost", db=dbname, json_mongo=True)
    a.install(plugin)

    #wrap root app in beaker middleware
    session_opts = {
        'session.type': 'memory',
        'session.cookie_expires': 300,
        'session.data_dir': tmppath,
        'session.auto': True,
        #set secure attribute on cookie
        'session.secure': True,
    }

    middlewared_app =  SessionMiddleware(a, session_opts)
    sut = TestApp(middlewared_app)

    return sut

#following method and two classes taken from the Cork documentation
def setup_dir(testdir):
    """Setup test directory with valid JSON files"""

    with open("%s/users.json" % testdir, 'w') as f:
        f.write("""{"admin": {"email_addr": null, "desc": null, "role": "admin", "hash": "69f75f38ac3bfd6ac813794f3d8c47acc867adb10b806e8979316ddbf6113999b6052efe4ba95c0fa9f6a568bddf60e8e5572d9254dbf3d533085e9153265623", "creation_date": "2012-04-09 14:22:27.075596"}}""")
    with open("%s/roles.json" % testdir, 'w') as f:
        f.write("""{"public": 10, "admin": 100, "hp_member": 60}""")
    with open("%s/register.json" % testdir, 'w') as f:
        f.write("""{}""")

class MockedAdminCork(Cork):
    """Mocked module where the current user is always 'admin'"""
    @property
    def _beaker_session(self):
        return RoAttrDict(username='admin')

    def _setup_cookie(self, username):
        global cookie_name
        cookie_name = username

class RoAttrDict(dict):
    """Read-only attribute-accessed dictionary.
    Used to mock beaker's session objects
    """
    def __getattr__(self, name):
        return self[name]
