import gameData
from gameData import playerStats, lastKilledPlayers, gamestate

def cupid(request):
	try:
		person1 = request.args["player1"]
		if person1 not in playerStats.keys():
			return "Error: First person not in game!"
	except KeyError:
		return "Error: First person not specified!"

	try:
		person2 = request.args["player2"]
		if person2 not in playerStats.keys():
			return "Error: Second person not in game!"
	except KeyError:
		return "Error: First person not specified!"
	
	if person1 == person2:
		return "Error: You cannot marry the same player"

	# cupid is first round only so no alive-check required

	playerStats[person1]["inLove"] = True
	playerStats[person2]["inLove"] = True
	return "success"

def thief(request):
	try:
		thief = request.args["thief"]
		if not validPlayer(thief)[0]: return validPlayer(thief)[1]
		if not playerStats[thief]["role"] == "thief":
			return "Error: Thief is not a thief!"
	except KeyError:
		return "Error: Thief not specified!"
	try:
		player = request.args["player"]
		if not validPlayer(player)[0]: return validPlayer(player)[1]
	except KeyError:
		return "Error: Player not specified!"

	playerStats[thief]["role"] = playerStats[player]["role"]
	playerStats[player]["role"] = "thief"

	return "success"

def slut(request):
	try:
		fucksWith = request.args["player"]
		if not validPlayer(fucksWith)[0]: return validPlayer(fucksWith)[1]
	except KeyError:
		return "Error: Player not specified!"
	
	try:
		slut = request.args["slut"]
		if not validPlayer(slut)[0]: return validPlayer(slut)[1]
	except KeyError:
		return "Error: Slut not specified!"
	
	if fucksWith == slut:
		return "Error: You cannot sleep alone, you are horny and desperate"

	playerStats[slut]["sleepsAt"] = fucksWith
	return "success"

def witch(request):
	global lastKilledPlayers
	try:
		witch = request.args["witch"]
		if not validPlayer(witch)[0]: return validPlayer(witch)[1]
	except KeyError:
		return "Error: Witch not specified!"
	
	try:
		action = request.args["action"]
		if action not in ["none", "heal", "kill"]: return "Error: not a valid action"
		if action not in playerStats[witch]["potions"] and action != "none": return "Error: not a valid Potion (anymore)"
	except KeyError:
		return "Error: Action not specified!"
	
	if action == "none": return "success"

	try:
		player = request.args["player"]
		if not validPlayer(player)[0]: return validPlayer(player)[1]
	except KeyError:
		return "Error: Player not specified!"
	
	if action == "heal":
		lastKilledPlayers.clear()
		playerStats[witch]["potions"].remove("heal")
		return "success"
	
	if action == "kill":
		playerStats[witch]["potions"].remove("kill")
		return killPlayer(player)
	
def wolf_white(request):
	if not gamestate: return "Error: Game not running!"

	if (gamestate % 2) == 0: return "Error: You can only kill every second night!"

	try:
		wolf = request.args["wolf"]
		if not validPlayer(wolf)[0]: return validPlayer(wolf)[1]
		if not playerStats[wolf]["role"] == "wolf_white":
			return "Error: Wolf is not a white wolf!"
	except KeyError:
		return "Error: Wolf not specified!"
	
	try:
		player = request.args["player"]
		if not validPlayer(player)[0]: return validPlayer(player)[1]
		if playerStats[player]["alive"] == False:
			return "Error: Player already dead!"
	except KeyError:
		return "Error: Player not specified!"
	
	return killPlayer(player)


def killPlayer(player):
	killedPlayers = []

	if gameData.playerStats[player]["alive"]:
		# kill loved ones
		if gameData.playerStats[player]["inLove"]:
			for p in gameData.playerStats:
				if gameData.playerStats[p]["inLove"] and p != player:
					#playerStats[p]["alive"] = False
					killedPlayers.append(p)
					gameData.lastKilledPlayers.append(p)
		#playerStats[player]["alive"] = False
		killedPlayers.append(player)
		gameData.lastKilledPlayers.append(player)

		# kill sleeping slut
		for p in gameData.playerStats:
			if gameData.playerStats[p]["role"] == "slut":
				if gameData.playerStats[p]["sleepsAt"] in killedPlayers:
					# kill loved ones
					if gameData.playerStats[p]["inLove"]:
						for pl in playerStats:
							if gameData.playerStats[pl]["inLove"] and p != player:
								#playerStats[p]["alive"] = False
								killedPlayers.append(pl)
								gameData.lastKilledPlayers.append(pl)
					#playerStats[p]["alive"] = False
					gameData.lastKilledPlayers.append(p)
		print(killedPlayers)
		return "success"
	else:
		return "Error: Player already dead!"

def validPlayer(player):
	if player not in playerStats.keys():
		return [False, "Error: Player not in game!"]
	if not playerStats[player]["alive"]:
		return [False, "Error: Player already dead!"]
	return [True]