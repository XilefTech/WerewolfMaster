import os
import time
from json import dumps, load
from flask import Flask, make_response, redirect, render_template, request
from flask_socketio import SocketIO, send, emit


import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
sentry_sdk.init(
    dsn="https://ebf0850457914ecfba223658eff985dc@sentry.thegreydiamond.de/13",
    integrations=[
        FlaskIntegration(),
    ],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)

import gameData

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode="threading")

from sites import api
from sites import ui

app.register_blueprint(api)
app.register_blueprint(ui)


def getAvailableRoles():
	if "static\\roles" not in os.getcwd(): os.chdir("static/roles/")
	return os.listdir()

@socketio.on('connect')
def connect(auth):
	print('New client connected!')
	emit('gameStatus', {"status": "ok", "playerList": gameData.players, "gameState": gameData.gamestate}, broadcast=True)

@socketio.on('disconnect')
def disconnect():
	print('Client disconnected')
	time.sleep(0.2) # wait for playerlist to update
	emit('gameStatus', {"status": "ok", "playerList": gameData.players, "gameState": gameData.gamestate}, broadcast=True)

def background_task_gamestate():
	while(True):
		socketio.emit('gameStatus', {"status": "ok", "playerList": gameData.players, "gameState": gameData.gamestate})
		time.sleep(2) # -> increase to 20 or smth when api changes can also send status updates

# import logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)
if __name__ == '__main__':
	print('starting...')

	for role in getAvailableRoles():
		if role not in gameData.roles:
			gameData.roles[role] = 0
	print(gameData.roles)

	socketio.start_background_task(background_task_gamestate)
	socketio.run(app, host='0.0.0.0', port=3000)
	# app.run(host='0.0.0.0', port=3000)


