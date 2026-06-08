# visuals/animator.py
import pygame
import math
import config

class Animator:
    def __init__(self, screen):
        self.screen       = screen
        self.font         = pygame.font.SysFont("Arial", 12, bold=True)
        self.route_trails = {}   # player name → list of (x,y) positions
        self.ball_arc     = []   # list of (x,y) for ball trajectory
        self.total_yards  = config.FIELD_LENGTH_YARDS + 2 * config.END_ZONE_YARDS
        self.ppy          = config.WINDOW_HEIGHT / self.total_yards  # pixels per yard

    def reset_play(self, players):
        """Clear trails at the start of every play."""
        self.route_trails = {p.name: [] for p in players}
        self.ball_arc     = []

    def _yard_to_y(self, yard):
        return int(config.WINDOW_HEIGHT -
                   (config.END_ZONE_YARDS + yard) * self.ppy)

    def set_player_positions(self, offense, defense, game_state):
        """
        Place all 22 players in their starting formation positions
        before the play begins. Called once per play before animation.
        """
        yard_line = game_state.yard_line
        scrimmage_y = self._yard_to_y(yard_line)
        field_cx    = config.FIELD_WIDTH // 2

        # ── Offense ───────────────────────────────────────────
        for p in offense:
            if p.position == "QB":
                p.x, p.y = field_cx, scrimmage_y + 30
            elif p.position == "RB":
                p.x, p.y = field_cx, scrimmage_y + 55
            elif p.position == "WR":
                wr_list = [o for o in offense if o.position == "WR"]
                idx     = wr_list.index(p)
                offsets = [-220, 220, -160]
                p.x     = field_cx + offsets[idx % len(offsets)]
                p.y     = scrimmage_y + 10
            elif p.position == "TE":
                p.x, p.y = field_cx + 80, scrimmage_y + 10
            elif p.position == "OL":
                ol_list  = [o for o in offense if o.position == "OL"]
                idx      = ol_list.index(p)
                p.x      = field_cx + (idx - 2) * 30
                p.y      = scrimmage_y + 10

            p.target_x = p.x
            p.target_y = p.y

        # ── Defense ───────────────────────────────────────────
        for p in defense:
            if p.position == "CB":
                cb_list = [d for d in defense if d.position == "CB"]
                idx     = cb_list.index(p)
                wr_list = [o for o in offense if o.position == "WR"]
                if idx < len(wr_list):
                    p.x = wr_list[idx].x
                else:
                    p.x = field_cx + (idx * 60 - 30)
                p.y = scrimmage_y - 25
            elif p.position == "S":
                s_list  = [d for d in defense if d.position == "S"]
                idx     = s_list.index(p)
                p.x     = field_cx + (idx * 2 - 1) * 100
                p.y     = scrimmage_y - 80
            elif p.position == "LB":
                lb_list = [d for d in defense if d.position == "LB"]
                idx     = lb_list.index(p)
                p.x     = field_cx + (idx - 1) * 80
                p.y     = scrimmage_y - 35
            elif p.position == "DL":
                dl_list = [d for d in defense if d.position == "DL"]
                idx     = dl_list.index(p)
                p.x     = field_cx + (idx - 1.5) * 35
                p.y     = scrimmage_y - 12

            p.target_x = p.x
            p.target_y = p.y

    def update_trails(self, players):
        """Append each player's current position to their route trail."""
        for p in players:
            if p.name in self.route_trails:
                self.route_trails[p.name].append((p.x, p.y))
                # Cap trail length so it doesn't get too long
                if len(self.route_trails[p.name]) > 120:
                    self.route_trails[p.name].pop(0)

    def draw_route_trails(self, offense):
        """Draw trailing lines behind offensive skill players."""
        for p in offense:
            if p.position not in ("WR", "TE", "RB"):
                continue
            trail = self.route_trails.get(p.name, [])
            if len(trail) < 2:
                continue
            for i in range(1, len(trail)):
                # Fade the trail — older points are more transparent
                alpha = int(255 * (i / len(trail)))
                color = (
                    int(config.COLOR_ROUTE_LINE[0] * alpha / 255),
                    int(config.COLOR_ROUTE_LINE[1] * alpha / 255),
                    int(config.COLOR_ROUTE_LINE[2] * alpha / 255),
                )
                pygame.draw.line(self.screen, color,
                                 (int(trail[i-1][0]), int(trail[i-1][1])),
                                 (int(trail[i][0]),   int(trail[i][1])), 2)

    def draw_players(self, offense, defense):
        """Draw all 22 players as colored circles with position labels."""
        for p in offense:
            color  = config.COLOR_OFFENSE_BLUE
            radius = 10 if p.position == "QB" else 8
            x, y   = int(p.x), int(p.y)
            pygame.draw.circle(self.screen, color, (x, y), radius)
            pygame.draw.circle(self.screen, (255, 255, 255), (x, y), radius, 1)

            # Open receiver indicator
            if getattr(p, 'is_open', False):
                pygame.draw.circle(self.screen, (0, 255, 100), (x, y), radius + 5, 2)

            # Position label
            label = self.font.render(p.name, True, (255, 255, 255))
            self.screen.blit(label, (x - label.get_width() // 2, y - radius - 13))

        for p in defense:
            color  = config.COLOR_DEFENSE_RED
            radius = 8
            x, y   = int(p.x), int(p.y)
            pygame.draw.circle(self.screen, color, (x, y), radius)
            pygame.draw.circle(self.screen, (255, 255, 255), (x, y), radius, 1)

            label = self.font.render(p.name, True, (255, 255, 255))
            self.screen.blit(label, (x - label.get_width() // 2, y - radius - 13))

    def draw_ball_arc(self, start, end, progress):
        """
        Draw a ball arc from QB to receiver.
        progress = 0.0 to 1.0 (how far through the throw we are)
        Uses a parabolic arc — ball goes up then comes down.
        """
        if not start or not end:
            return

        # How many points to draw up to current progress
        steps = 30
        points = []
        for i in range(int(steps * progress) + 1):
            t  = i / steps
            # Linear interpolation
            x  = start[0] + (end[0] - start[0]) * t
            y  = start[1] + (end[1] - start[1]) * t
            # Parabolic arc — subtract height at peak
            arc_height = 40 * math.sin(math.pi * t)
            y -= arc_height
            points.append((int(x), int(y)))

        if len(points) >= 2:
            pygame.draw.lines(self.screen, config.COLOR_BALL_YELLOW,
                              False, points, 3)

        # Ball dot at current position
        if points:
            pygame.draw.circle(self.screen, config.COLOR_BALL_YELLOW,
                               points[-1], 5)

    def draw_all(self, offense, defense, throw_start=None,
                 throw_end=None, throw_progress=0.0):
        self.draw_route_trails(offense)
        self.draw_players(offense, defense)
        if throw_start and throw_end and throw_progress > 0:
            self.draw_ball_arc(throw_start, throw_end, throw_progress)