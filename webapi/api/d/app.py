import sys
sys.path.append('webapi')

from bottle import Bottle

import webapi.shared_state as state

app = Bottle()

if state.plug is not None:
    app.install(state.plug)

auth = state.auth

import files
import hpfeeds
import sessions
import urls
import dorks
