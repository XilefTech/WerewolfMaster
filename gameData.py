players = []
playerTimeout = {}
timeout = 10 # in seconds
roles = {'wolf': 2, 'witch': 1, 'seer': 1, 'slut': 1, 'cupid': 1, 'thief': 1, 'winking_girl': 1} # cupid = amor
assignedRoles = {}
playerStats = {}
gamestate = 0
gamestates = ["pre-round", "running"]
lastKilledPlayers = []
knightKill = False