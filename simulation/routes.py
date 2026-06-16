from players import player
import config
import random
import math

routes = {
    "slant":    [(0, 5), (8, 10)],       # Quick inside cut
    "curl":     [(0, 12), (-2, 10)],     # Run up then curl back
    "out":      [(8, 10), (12, 10)],     # Break toward sideline
    "in":       [(-8, 10), (-12, 10)],   # Break toward middle
    "go":       [(0, 30)],               # Straight deep
    "post":     [(0, 10), (-8, 22)],     # Angle toward goalpost
    "corner":   [(0, 10), (8, 22)],      # Angle toward corner
    "cross":    [(-12, 8)],              # Crossing route
    "screen":   [(4, 0), (4, -2)],       # RB screen — flat then back
    "wheel":    [(6, 0), (6, 20)],       # RB wheel route
    "flat":     [(6, 2)],                # Quick flat — TE/RB
    "seam":     [(0, 25)],               # TE seam down the middle
}

def get_waypoints(route_name, start_x, start_y):
    """
    Convert a route name into absolute pixel positions
    on the field based on where the player lines up.

    TODO:
    - Look up the route in ROUTES dict by route_name
    - For each (dx, dy) waypoint, convert from yards to pixels
      using config.YARDS_TO_PIXELS
    - Add start_x and start_y to get absolute field positions
    - Remember: positive y in our coordinate system is UP
      (toward end zone) so dy should SUBTRACT from y
      (since in Pygame y=0 is at the top)
    - Return a list of (px_x, px_y) tuples

    Example:
      start_x=400, start_y=600, route="slant"
      waypoint (0, 5) → (400 + 0*6, 600 - 5*6) = (400, 570)
    """
    route_offsets = routes.get(route_name, [])
    waypoints = []
    for dx, dy in route_offsets:
        px = start_x + dx * config.YARDS_TO_PIXELS
        py = start_y - dy * config.YARDS_TO_PIXELS
        waypoints.append((px, py))
    return waypoints

def assign_routes(offense):
    """
    Assign a route to each offensive skill player before a play.
    Sets player.target_x and player.target_y to the first waypoint,
    and stores the full route on the player as player.route_waypoints.

    TODO:
    - Get the QB from offense (position == "QB")
    - For each skill player (WR, TE, RB) pick a route from ROUTES
      randomly for now — the RL agent will choose later
    - Call get_waypoints() to convert to pixel positions
    - Store waypoints on player as player.route_waypoints
    - Set player.target_x, player.target_y to waypoints[0]
    - OL players don't run routes — skip them
    """
    qb = next((p for p in offense if p.position == "QB"), None)
    if not qb:
        return

    skill_players = []
    for p in offense:
        if p.position in ("WR", "TE", "RB"):
            skill_players.append(p)
    
    route_names = list(routes.keys())
    for player in skill_players:
        route_name = random.choice(route_names)
        waypoints = get_waypoints(route_name, player.x, player.y)
        player.route_waypoints = waypoints
        player.route_index = 0
        
        if waypoints:
            player.target_x, player.target_y = waypoints[0]
        else:
            player.target_x, player.target_y = player.x, player.y


def advance_route(player):
    if not hasattr(player, 'route_waypoints') or not player.route_waypoints:
        return

    if player.route_index >= len(player.route_waypoints):
        return

    current_waypoint = player.route_waypoints[player.route_index]
    dist = math.sqrt((player.x - current_waypoint[0])**2 + 
                     (player.y - current_waypoint[1])**2)

    if dist < 5:
        player.route_index += 1
        if player.route_index < len(player.route_waypoints):
            player.target_x, player.target_y = player.route_waypoints[player.route_index]
        