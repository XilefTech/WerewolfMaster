from json import dumps, load
import os
import random
from flask import Blueprint, request

from gameData import gamestate, gamestates, players, assignedRoles, roles


api = Blueprint('API', __name__, template_folder='templates', static_folder='static')

@api.route("/api")
def api_mainpage():
	return "<h1>API</h1> <p>If you're seeing this, something probably went wrong because you shouldn't be here.</p>"

@api.route("/api/<path:subpath>")
def api_path(subpath):
	global gamestate, assignedRoles
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


	if subpath == "endgame":
		gamestate = 0
		assignedRoles.clear()
		return dumps("success")


	if subpath == "startgame":
		if gamestate:
			return dumps({"status": "failed", "data": "Error: Game already running!"})
		
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
	

	if subpath == "getGameData":
		if gamestate:
			return dumps(assignedRoles)
		else:
			return dumps({"status": "failed", "data": "Error: Game not running!"})
    

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