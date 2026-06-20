# simulation/movement.py
import numpy as np
import config

def get_speed_px(player):
    """
    Convert a player's speed stat (0–100) to pixels per frame.
    """
    return config.MAX_SPEED * (player.get_stat("speed") / 100)

def clamp_to_field(player):
    """
    Prevent players from moving outside the field boundaries.
    """
    margin   = 10
    player.x = max(margin, min(config.FIELD_WIDTH - margin, player.x))
    player.y = max(margin, min(config.WINDOW_HEIGHT - margin, player.y))

def move_player(player):
    """
    Move a player one step toward their current target position.
    """
    dx = player.target_x - player.x
    dy = player.target_y - player.y
    distance = np.sqrt(dx ** 2 + dy ** 2)
    speed_px = get_speed_px(player)

    if distance <= speed_px:
        player.x = player.target_x
        player.y = player.target_y
    else:
        direction_x = dx / distance
        direction_y = dy / distance
        player.x += speed_px * direction_x
        player.y += speed_px * direction_y

    clamp_to_field(player)

def move_all_players(players):
    """
    Call move_player on every player in the list.
    """
    for player in players:
        move_player(player)

def check_open(receiver, defender):
    """
    Returns True if the receiver is open — far enough from
    their defender that the QB should throw to them.
    """
    dx = receiver.x - defender.x
    dy = receiver.y - defender.y
    distance = np.sqrt(dx ** 2 + dy ** 2)
    return distance > config.SEPERATION_MIN