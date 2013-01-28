import sys
sys.path.append('webapi')

from bottle import Bottle
import webapi.mongoplug as mongoplug

app = Bottle()
if mongoplug.plug != None:
    app.install(mongoplug.plug)

import aux
import files
import hpfeeds
import sessions
import urls
import dorks
