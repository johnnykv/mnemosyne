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
import json
import webapi.shared_state as shared


def prepare_app(dbname, tmppath, user_name):
    #mock auth mechanism
    setup_dir(tmppath)
    shared.auth = MockedCorkAuth(tmppath, user_name)
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

    middlewared_app = SessionMiddleware(a, session_opts)
    sut = TestApp(middlewared_app)

    return sut

#following method and two classes taken from the Cork documentation
def setup_dir(testdir):
    """Setup test directory with valid JSON files"""

    #dummy users for testing (user, role)
    users = {'admin': {'role': 'admin'},
             'a_all': {'role': 'access_all'},
             'a_norm': {'role': 'access_normalized'},
             'public': {'role': 'public'}}

    with open("%s/users.json" % testdir, 'w') as f:
        f.write(json.dumps(users))
    with open("%s/roles.json" % testdir, 'w') as f:
        f.write("""{"public": 10, "admin": 100, "access_all": 70, "access_normalized": 60}""")
    with open("%s/register.json" % testdir, 'w') as f:
        f.write("""{}""")


class MockedCorkAuth(Cork):
    """Mocked module where the current user is always 'admin'"""

    def __init__(self, directory, user_name):
        super(MockedCorkAuth, self).__init__(directory)
        self.user_name = user_name

    @property
    def _beaker_session(self):
        return RoAttrDict(username='a_all')

    def _setup_cookie(self, username):
        global cookie_name
        cookie_name = username


class RoAttrDict(dict):
    """Read-only attribute-accessed dictionary.
    Used to mock beaker's session objects
    """

    def __getattr__(self, name):
        return self[name]
