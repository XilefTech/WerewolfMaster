from html import escape
import os
import random
from flask import Flask, make_response, redirect, render_template, request
from json import dumps, load

app = Flask(__name__)
players = []
playerTimeout = {}
timeout = 10 # in seconds
roles = {'wolf': 2, 'witch': 1, 'seer': 1, 'slut': 1, 'cupid': 1, 'bearleader': 0, 'fox': 0, 'knight': 0, 'maiden': 0, 'thief': 0, 'wild_kiddo': 0, 'winking_girl': 0, 'wolf_primeval': 0, 'wolf_white': 0} # cupid = amor
gameRoles = []
assignedRoles = {}
gamestate = 0
gamestates = ["pre-round", "running"]


@app.get("/")
def index_get():
	# If the user is already logged in, redirect to the user page
	if request.cookies.get("username"):
		return redirect("/user")
	else:
		return render_template("index.html")


@app.post("/")
def index_post():
	# Check entered name and redirect to user page if it is not taken
	name = request.form["name"].lower()
	if name == "":
		return render_template("index.html", error="Please enter a name")

	if name in players:
		return render_template("index.html", error="Name already taken")

	players.append(name)
	# idk maybe you can inject a js/json payload here, but fuck security
	response = make_response(redirect(f"/user"))
	response.set_cookie("username", name)
	return response


@app.route("/user")
def userpage():
	username = request.cookies.get("username")
	if username:
		if username not in players:
			players.append(username)
		return render_template("user.html", username=escape(username.capitalize()))
	else:
		return redirect("/")


@app.route("/logout")
def logout():
	name = request.cookies.get("username")
	players.remove(name) if name in players else None

	response = make_response(redirect("/"))
	response.set_cookie("username", "", expires=0)
	return response


@app.route("/narrator")
def narratorMain():
	return render_template("narrator.html")

@app.route("/narrator/settings")
def narratorSettings():
	return render_template("settings.html")


@app.route("/api")
def api():
	return "<h1>API</h1> <p>If you're seeing this, something probably went wrong because you shouldn't be here.</p>"

@app.route("/api/<path:subpath>")
def api_path(subpath):
	global gamestate
	# if a playertimeout is needed, uncomment this, resets the timeout value with every api request
	# if request.cookies.get("username"):
	#     playerTimeout[request.cookies.get("username")] = timeout

	if subpath == "players":
		return dumps(sorted(players))
	

	if subpath == "gamestate":
		return dumps(gamestates[gamestate])
	

	if subpath == "myrole":
		name = request.cookies.get("username")
		if not name:
			return "Error: No username cookie found!"
		
		if not gamestate:
			return "Error: Game not running!"

		if name in assignedRoles:
			return dumps(assignedRoles[name])
		
		return dumps("Looks like you're not in the game!")


	if subpath == "startgame":
		# if gamestate:
		# 	return dumps({"status": "failed", "data": "Error: Game already running!"})
		
		if len(players) > len(roles):
			return dumps({"status": "failed", "data": "Error: Not enough roles for all players!"})
		
		gameRoles = []
		for role, amount in roles.items():
			for i in range(int(amount)):
				gameRoles.append(role)
		random.shuffle(gameRoles)
		for index, player in enumerate(players):
			assignedRoles[player] = gameRoles[index]
		
		gamestate = 1

		return dumps({"status": "success", "data": assignedRoles})
	
    
	if subpath == "getAvailableRoles":
		return dumps(getAvailableRoles())
	
	if subpath == "getRoleMappings":
		roleMappings = {}

		for role in getAvailableRoles():
			if "static\\roles" not in os.getcwd(): os.chdir("static/roles/")
			with open('%s/info.json' % role, encoding="utf-8") as f:
				d = load(f)
			roleMappings[role] = d["de"] ["roleName"]

		return dumps(roleMappings)
	
	if subpath == "getRoleEntries":
			return dumps(roles)

	if "settings/" in subpath:
		return dumps(settings(subpath, request))
		
	return subpath

def settings(path, request):
	role = request.args.get("role")
		
	if "setRoleEntry" in path:
		if role in getAvailableRoles():
			try:
				roles[role] = request.args["value"]
				print(roles)
			except KeyError:
				return "Error: No position specified!"
			except IndexError:
				return "Error: The specified position doesn't exist!"
		else:
			return "Error: No role specified!"
	
	return "success"


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
