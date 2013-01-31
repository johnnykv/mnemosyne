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
from bottle import get, post, route, static_file
import shared_state

@post('/login')
def login():
    """Authenticate users"""
    username = post_get('username')
    password = post_get('password')
    shared_state.auth.login(username, password, success_redirect='/winner', fail_redirect='/login')

@route('/logout')
def logout():
    shared_state.auth.logout(success_redirect='/login')

@get('/')
def get_index():
    return static_file('index.html', root=shared_state.static_dir)


@get('/<filename:path>')
def static(filename):
    return static_file(filename, root=shared_state.static_dir)

def post_get(name, default=''):
    return bottle.request.POST.get(name, default).strip()

