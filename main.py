from html import escape
import os
import random
from flask import Flask, make_response, redirect, render_template, request
from json import dumps, load
from sites.api import api
from sites.ui import ui

from gameData import players, roles, assignedRoles, gamestate, gamestates #, timeout, playerTimeout

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.register_blueprint(api)
app.register_blueprint(ui)


def getAvailableRoles():
	if "static\\roles" not in os.getcwd(): os.chdir("static/roles/")
	return os.listdir()


for role in getAvailableRoles():
	if role not in roles:
		roles[role] = 0

print(roles)

# import logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)
app.run(host='0.0.0.0', port=3000)
