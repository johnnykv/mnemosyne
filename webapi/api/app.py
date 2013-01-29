import sys
sys.path.append('webapi')

from bottle import Bottle
import webapi.shared_state as mongoplug

app = Bottle()
if shared_state.plug != None:
    app.install(shared_state.plug)

import aux
import files
import hpfeeds
import sessions
import urls
import dorks
