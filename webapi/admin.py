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
from bottle import get, post, route, static_file, view, HTTPError
import shared_state
import logging

logger = logging.getLogger(__name__)

@route('/unauth')
def login():
    return HTTPError(401, 'Unauthorized')


@post('/login')
def login():
    """Authenticate users"""
    username = post_get('username')
    password = post_get('password')
    logger.info("Authentication attempt with username: [{0}]".format(username))
    if shared_state.auth.login(username, password):
        return "You provided valid credentials"
    else:
        return HTTPError(401, 'Invalid credentials')


@route('/logout')
def logout():
    shared_state.auth.logout(success_redirect='/unauth')


@route('/admin')
@view('admin_page')
def admin():
    """Only admin users can see this"""
    shared_state.auth.require(role='admin', fail_redirect='/unauth')
    return dict(
        current_user=shared_state.auth.current_user,
        users=shared_state.auth.list_users(),
        roles=shared_state.auth.list_roles()
    )


@post('/create_user')
def create_user():
    try:
        shared_state.auth.create_user(postd().username, postd().role, postd().password)
        return dict(ok=True, msg='')
    except Exception, e:
        return dict(ok=False, msg=e.message)


@post('/delete_user')
def delete_user():
    try:
        shared_state.auth.delete_user(post_get('username'))
        return dict(ok=True, msg='')
    except Exception, e:
        return dict(ok=False, msg=e.message)


@post('/create_role')
def create_role():
    try:
        shared_state.auth.create_role(post_get('role'), post_get('level'))
        return dict(ok=True, msg='')
    except Exception, e:
        return dict(ok=False, msg=e.message)


@post('/delete_role')
def delete_role():
    try:
        shared_state.auth.delete_role(post_get('role'))
        return dict(ok=True, msg='')
    except Exception, e:
        return dict(ok=False, msg=e.message)


def postd():
    return bottle.request.forms


def post_get(name, default=''):
    return bottle.request.POST.get(name, default).strip()