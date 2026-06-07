import json
from players.player import Player

def load_roster(filepath):
    """
      from players.roster import load_roster
      offense, defense = load_roster("players/teams/bears.json")
    """
    with open(filepath, "r") as f:
        data = json.load(f)

    offense = []
    for p in data["offense"]:
        player = Player(
            name = p["name"], 
            position = p["position"], 
            side = "offense", 
            stats = p["stats"])
        offense.append(player)

    defense = []
    for p in data["defense"]:
        player = Player(
            name = p["name"], 
            position = p["position"], 
            side = "defense", 
            stats = p["stats"])
        defense.append(player)

    return offense, defense