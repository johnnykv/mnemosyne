import sys
sys.path.append('webapi')

from bottle import Bottle

import webapi.shared_state as state

app = Bottle()

if state.plug != None:
    app.install(state.plug)

import aux
import files
import hpfeeds
import sessions
import urls
import dorks
