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
		killedPlayers = []

		if playerStats[player]["alive"]:
			# kill loved ones
			if playerStats[player]["inLove"]:
				for p in playerStats:
					if playerStats[p]["inLove"] and p != player:
						playerStats[p]["alive"] = False
						killedPlayers.append(p)
			playerStats[player]["alive"] = False
			killedPlayers.append(player)

			# kill sleeping slut
			for p in playerStats:
				if playerStats[p]["role"] == "slut":
					if playerStats[p]["sleepsAt"] in killedPlayers:
						playerStats[p]["alive"] = False
			return "success"
		else:
			return "Error: Player already dead!"
		

def roleAction(path, request):
	if not gamestate:
		return "Error: Game not running!"
	
	if "cupid" in path:
		try:
			person1 = request.args["player1"]
			if person1 not in players:
				return "Error: First person not in game!"
		except KeyError:
			return "Error: First person not specified!"
		
		try:
			person2 = request.args["player2"]
			if person2 not in players:
				return "Error: Second person not in game!"
		except KeyError:
			return "Error: First person not specified!"
		
		if person1 == person2:
			return "Error: You cannot marry the same player"

		# cupid is first round only so no alive-check required

		playerStats[person1]["inLove"] = True
		playerStats[person2]["inLove"] = True
		return "success"
	
	if "thief" in path:
		try:
			thief = request.args["thief"]
			if thief not in players:
				return "Error: Thief not in game!"
			if not playerStats[thief]["alive"]:
				return "Error: Thief already dead!"
			if not playerStats[thief]["role"] == "thief":
				return "Error: Thief is not a thief!"
		except KeyError:
			return "Error: Thief not specified!"
		try:
			player = request.args["player"]
			if player not in players:
				return "Error: Player not in game!"
			if not playerStats[player]["alive"]:
				return "Error: Player already dead!"
		except KeyError:
			return "Error: Player not specified!"
		
		playerStats[thief]["role"] = playerStats[player]["role"]
		playerStats[player]["role"] = "thief"

		return "success"
	
	if "slut" in path:
		try:
			fucksWith = request.args["player"]
			if fucksWith not in players:
				return "Error: Player not in game!"
			if not playerStats[fucksWith]["alive"]:
				return "Error: Player already dead!"
		except KeyError:
			return "Error: Player not specified!"
		
		try:
			slut = request.args["slut"]
			if slut not in players:
				return "Error: Player not in game!"
			if not playerStats[slut]["alive"]:
				return "Error: Player already dead!"
		except KeyError:
			return "Error: Player not specified!"
		
		playerStats[slut]["sleepsAt"] = fucksWith
		return "success"
		
		




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