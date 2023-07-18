from json import dumps, load
import os
import random
from flask import Blueprint, request

from gameData import gamestate, gamestates, players, assignedRoles, roles, playerStats


api = Blueprint('API', __name__, template_folder='templates', static_folder='static')

@api.route("/api")
def api_mainpage():
	return "<h1>API</h1> <p>If you're seeing this, something probably went wrong because you shouldn't be here.</p>"

@api.route("/api/<path:subpath>")
def api_path(subpath):
	global gamestate, assignedRoles, playerStats
	# if a playertimeout is needed, uncomment this, resets the timeout value with every api request
	# if request.cookies.get("username"):
	#     playerTimeout[request.cookies.get("username")] = timeout

	if subpath == "players":
		return dumps(sorted(players))
	
	if subpath == "getAlivePlayers":
		if not gamestate:
			return dumps({"status": "failed", "data": "Error: Game not running!"})
		
		alivePlayers = []
		for player in playerStats:
			if playerStats[player]["alive"]:
				alivePlayers.append(player)
		return dumps({"status": "success", "data": sorted(alivePlayers)})
	

	if subpath == "gamestate":
		return dumps(gamestate)
	

	if subpath == "me":
		name = request.cookies.get("username")
		if not name:
			return "Error: No username cookie found!"
		
		if not gamestate:
			return "Error: Game not running!"

		if name in playerStats:
			return dumps(playerStats[name])
		
		return dumps("Looks like you're not in the game!")


	if subpath == "endround":
		gamestate += 1
		return dumps("success")


	if subpath == "endgame":
		gamestate = 0
		playerStats.clear()
		return dumps("success")


	if subpath == "startgame":
		if gamestate:
			return dumps({"status": "failed", "data": "Error: Game already running!"})
		
		gameRoles = []
		for role, amount in roles.items():
			for i in range(int(amount)):
				gameRoles.append(role)

		if len(players) > len(gameRoles):
			return dumps({"status": "failed", "data": "Error: Not enough roles for all players!"})
		
		
		random.shuffle(gameRoles)
		for index, player in enumerate(players):
			playerStats[player] = {"role": gameRoles[index], "alive": True, "inLove": False}
		
		gamestate = 1

		return dumps({"status": "success", "data": playerStats})
	

	if subpath == "getGameData":
		if gamestate:
			return dumps({"status": "success", "data": playerStats})
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
			# yea maybe sort this, TODO
			with open("meta.json") as f:
				d = load(f)
				orderToFollow = d["roleOrder"]

			sortedRoles = {}
			for key in orderToFollow:
				sortedRoles[key] = roles[key]
			    
			return dumps(sortedRoles)
	
	if "action/" in subpath:
		return dumps(action(subpath, request))

	if "settings/" in subpath:
		return dumps(settings(subpath, request))
		
	return subpath

def action(path, request):
	if "/role/" in path:
		return roleAction(path, request)
	
	try:
		player = request.args["player"]
	except KeyError:
		return "Error: No player specified!"
	

	if "hangPlayer" in path:
		if playerStats[player]["alive"]:
			# hunter
			if playerStats[player]["role"] == "hunter":
				try:
					victim = request.args["victim"]
					if victim not in players:
						return "Error: Victim not in game!"
					if not playerStats[victim]["alive"]:
						return "Error: Player already dead!"
				except KeyError:
					return "Error: No victim specified!"
			
			playerStats[victim]["alive"] = False
			playerStats[player]["alive"] = False

			# kill loved ones
			if playerStats[player]["inLove"]:
				for p in playerStats:
					if playerStats[p]["inLove"] and p != player:
						playerStats[p]["alive"] = False

			return "success"
		else:
			return "Error: Player already dead!"


	if "killPlayer" in path:
		return killPlayer(player)

def killPlayer(player):
	killedPlayers = []

	if playerStats[player]["alive"]:
		# kill loved ones
		if playerStats[player]["inLove"]:
			for p in playerStats:
				if playerStats[p]["inLove"] and p != player:
					#playerStats[p]["alive"] = False
					killedPlayers.append(p)
					lastKilledPlayers.append(p)
		#playerStats[player]["alive"] = False
		killedPlayers.append(player)
		lastKilledPlayers.append(player)

		# kill sleeping slut
		for p in playerStats:
			if playerStats[p]["role"] == "slut":
				if playerStats[p]["sleepsAt"] in killedPlayers:
					#playerStats[p]["alive"] = False
					lastKilledPlayers.append(p)
		return "success"
	else:
		return "Error: Player already dead!"
		

def roleAction(path, request):
	if not gamestate:
		return "Error: Game not running!"
	
	if "cupid" in path:
		return roleActions.cupid(request)
	
	if "thief" in path:
		return roleActions.thief(request)
	
	if "slut" in path:
		return roleActions.slut(request)
	
	if "witch" in path:
		return roleActions.witch(request)
	
	if "wolf_white" in path:
		return roleActions.wolf_white(request)


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
	print(os.getcwd())
	if "static\\roles" not in os.getcwd(): os.chdir("./static/roles/")
	roleList = os.listdir()
	roleList.remove("meta.json")
	return roleList