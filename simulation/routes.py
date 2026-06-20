# simulation/routes.py
import config
import random
import math

routes = {
    "slant":  [(0, 5), (8, 10)],
    "curl":   [(0, 12), (-2, 10)],
    "out":    [(8, 10), (12, 10)],
    "in":     [(-8, 10), (-12, 10)],
    "go":     [(0, 30)],
    "post":   [(0, 10), (-8, 22)],
    "corner": [(0, 10), (8, 22)],
    "cross":  [(-12, 8)],
    "screen": [(4, 0), (4, -2)],
    "wheel":  [(6, 0), (6, 20)],
    "flat":   [(6, 2)],
    "seam":   [(0, 25)],
}

# Whether the player stops at the final waypoint or keeps running
ROUTE_BEHAVIOR = {
    "slant":  "continue",
    "curl":   "stop",
    "out":    "stop",
    "in":     "stop",
    "go":     "continue",
    "post":   "continue",
    "corner": "continue",
    "cross":  "continue",
    "screen": "stop",
    "wheel":  "continue",
    "flat":   "stop",
    "seam":   "continue",
}

def get_waypoints(route_name, start_x, start_y):
    route_offsets = routes.get(route_name, [])
    waypoints = []
    for dx, dy in route_offsets:
        px = start_x + dx * config.YARDS_TO_PIXELS
        py = start_y - dy * config.YARDS_TO_PIXELS
        waypoints.append((px, py))
    return waypoints

def assign_routes(offense):
    qb = next((p for p in offense if p.position == "QB"), None)
    if not qb:
        return

    skill_players = [p for p in offense if p.position in ("WR", "TE", "RB")]
    route_names   = list(routes.keys())

    for player in skill_players:
        route_name             = random.choice(route_names)
        waypoints              = get_waypoints(route_name, player.x, player.y)
        player.route_waypoints = waypoints
        player.route_index     = 0
        player.route_behavior  = ROUTE_BEHAVIOR.get(route_name, "stop")

        if waypoints:
            player.target_x, player.target_y = waypoints[0]
        else:
            player.target_x, player.target_y = player.x, player.y

def advance_route(player):
    if not hasattr(player, 'route_waypoints') or not player.route_waypoints:
        return

    # Player has finished all waypoints
    if player.route_index >= len(player.route_waypoints):
        if getattr(player, 'route_behavior', 'stop') == "continue":
            if len(player.route_waypoints) >= 2:
                last = player.route_waypoints[-1]
                prev = player.route_waypoints[-2]
                dx   = last[0] - prev[0]
                dy   = last[1] - prev[1]
                dist = math.sqrt(dx**2 + dy**2)
                if dist > 0:
                    player.target_x = last[0] + (dx / dist) * 999
                    player.target_y = last[1] + (dy / dist) * 999
            elif len(player.route_waypoints) == 1:
                player.target_x = player.route_waypoints[0][0]
                player.target_y = player.route_waypoints[0][1] - 999
        # If "stop" — player stays at final waypoint, do nothing
        return

    # Move toward current waypoint
    current_waypoint = player.route_waypoints[player.route_index]
    dist = math.sqrt((player.x - current_waypoint[0])**2 +
                     (player.y - current_waypoint[1])**2)

    if dist < 5:
        player.route_index += 1
        if player.route_index < len(player.route_waypoints):
            player.target_x, player.target_y = player.route_waypoints[player.route_index]