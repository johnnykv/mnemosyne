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
import mongoplug
from bottle import run, static_file, get, install, Bottle, mount
from bottle.ext import mongo

class MnemoWebAPI():
    """Exposes raw and normalized data from hpfeeds through a RESTful api"""

    def __init__(self, datebase_name, static_file_path=None):
        mongoplug.plug = bottle.ext.mongo.MongoPlugin(uri="localhost", db=datebase_name, json_mongo=True)
        print mongoplug.plug
        install(mongoplug.plug)
        from webapi.api import app as develapp
        mount('/api/', develapp.app)
        #if static_file_path != None:

    def start_listening(self, host, port):
        run(host=host, port=port, debug=True, server='paste', quiet=True)


#@get('/')
#def get_index():
#    return static_file('index.html', root=MnemoWebAPI.static_file_path)


#@get('/<filename:path>')
#def static(filename):
#    return static_file(filename, root=MnemoWebAPI.static_file_path)