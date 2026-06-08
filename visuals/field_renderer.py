# visuals/field_renderer.py
import pygame
import math
import config


class FieldRenderer:
    def __init__(self, screen):
        self.screen = screen

        # ── Fonts ──────────────────────────────────────────────────────────────
        self.font_hud    = pygame.font.SysFont("Arial", config.FONT_SIZE_HUD,   bold=True)
        self.font_label  = pygame.font.SysFont("Arial", config.FONT_SIZE_LABEL + 6, bold=True)
        self.font_score  = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_small  = pygame.font.SysFont("Arial", 11, bold=False)

        # ── Geometry ───────────────────────────────────────────────────────────
        total_yards          = config.FIELD_LENGTH_YARDS + 2 * config.END_ZONE_YARDS
        self.pixels_per_yard = config.WINDOW_HEIGHT / total_yards
        self.ez_height       = int(config.END_ZONE_YARDS * self.pixels_per_yard)
        self.fw              = config.FIELD_WIDTH   # shorthand

        # ── Colours ────────────────────────────────────────────────────────────
        # Field greens – richer and more saturated
        self.C_GREEN_A   = (34,  110,  50)
        self.C_GREEN_B   = (28,   95,  42)

        # End zones
        self.C_EZ_OFF    = (15,  60, 130)   # deep navy blue  (offense)
        self.C_EZ_DEF    = (140,  20,  20)  # deep crimson    (defense)

        # Lines / glow
        self.C_WHITE     = (255, 255, 255)
        self.C_SCRIMMAGE = (100, 220, 255)
        self.C_FIRST_DN  = (255, 175,  30)
        self.C_HASH      = (200, 200, 200)

        # HUD
        self.C_HUD_BG    = (12,  12,  20)
        self.C_HUD_ACCENT= (80, 140, 255)

        # Analytics sidebar
        self.C_ANAL_BG   = (10,  12,  28)
        self.C_ANAL_LINE = (30,  35,  70)
        self.C_ANAL_TITLE= (90, 150, 255)

    # ──────────────────────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _yard_to_y(self, yard):
        """Convert a field-yard position to a screen y-coordinate."""
        return int(config.WINDOW_HEIGHT -
                   (config.END_ZONE_YARDS + yard) * self.pixels_per_yard)

    def _draw_glow_line(self, color, y, glow_alpha=60, glow_width=6, core_width=2):
        """Draw a glowing horizontal line (wide semi-transparent halo + bright core)."""
        # Glow layer via a temporary Surface with per-pixel alpha
        glow_surf = pygame.Surface((self.fw, glow_width), pygame.SRCALPHA)
        r, g, b   = color
        glow_surf.fill((r, g, b, glow_alpha))
        self.screen.blit(glow_surf, (0, y - glow_width // 2))
        # Solid core
        pygame.draw.line(self.screen, color,
                         (0, y), (self.fw, y), core_width)

    def _draw_ez_stripes(self, top, height, color, stripe_color):
        """Draw diagonal stripes inside an end-zone rect."""
        surf = pygame.Surface((self.fw, height), pygame.SRCALPHA)
        surf.fill((*color, 255))

        spacing = 18
        r, g, b = stripe_color
        for x in range(-height, self.fw + height, spacing):
            pygame.draw.line(surf, (r, g, b, 55),
                             (x, 0), (x + height, height), 2)
        self.screen.blit(surf, (0, top))

    # ──────────────────────────────────────────────────────────────────────────
    # Field layers
    # ──────────────────────────────────────────────────────────────────────────

    def draw_field(self):
        """Alternating 10-yard strips with richer greens."""
        total_yards  = config.FIELD_LENGTH_YARDS + 2 * config.END_ZONE_YARDS
        strip_height = int(10 * self.pixels_per_yard)
        num_strips   = total_yards // 10

        for i in range(num_strips):
            color = self.C_GREEN_A if i % 2 == 0 else self.C_GREEN_B
            pygame.draw.rect(self.screen, color,
                             (0, i * strip_height, self.fw, strip_height))

    def draw_end_zones(self):
        """End zones with flat color and bold labels."""
        # Defense (top) — crimson
        pygame.draw.rect(self.screen, self.C_EZ_DEF,
                         (0, 0, self.fw, self.ez_height))
        # Offense (bottom) — navy
        pygame.draw.rect(self.screen, self.C_EZ_OFF,
                         (0, config.WINDOW_HEIGHT - self.ez_height,
                          self.fw, self.ez_height))

        # Thin border lines at end-zone edges
        pygame.draw.line(self.screen, self.C_WHITE,
                         (0, self.ez_height), (self.fw, self.ez_height), 2)
        pygame.draw.line(self.screen, self.C_WHITE,
                         (0, config.WINDOW_HEIGHT - self.ez_height),
                         (self.fw, config.WINDOW_HEIGHT - self.ez_height), 2)

        # Labels — large, centred, with a subtle drop-shadow
        for text, y_center, shadow_col in [
            ("DEFENSE", self.ez_height // 2,
             (80, 0, 0)),
            ("OFFENSE", config.WINDOW_HEIGHT - self.ez_height // 2,
             (0, 20, 80)),
        ]:
            surf = self.font_hud.render(text, True, self.C_WHITE)
            shadow = self.font_hud.render(text, True, shadow_col)
            cx = self.fw // 2 - surf.get_width() // 2
            cy = y_center - surf.get_height() // 2
            self.screen.blit(shadow, (cx + 2, cy + 2))
            self.screen.blit(surf,   (cx, cy))

    def draw_yard_lines(self):
        """10-yard lines with subtle glow + rotated numbers on both sidelines."""
        for yard in range(10, 100, 10):
            y       = self._yard_to_y(yard)
            display = str(yard) if yard <= 50 else str(100 - yard)

            # Main yard line (no glow — keep the field clean)
            pygame.draw.line(self.screen, self.C_WHITE,
                             (0, y), (self.fw, y), 2)

            # ── Yard number – left side (rotated 90° CCW) ──
            label = self.font_label.render(display, True, self.C_WHITE)

            # Rotate 90° counter-clockwise for left sideline
            left_rot = pygame.transform.rotate(label, 90)
            self.screen.blit(left_rot, (4, y - left_rot.get_height() // 2))

            # Rotate 90° clockwise for right sideline
            right_rot = pygame.transform.rotate(label, -90)
            self.screen.blit(right_rot,
                             (self.fw - right_rot.get_width() - 4,
                              y - right_rot.get_height() // 2))

    def draw_hash_marks(self):
        """Hash marks at NFL-standard ⅓ / ⅔ positions."""
        third = self.fw // 3
        for yard in range(5, 100, 5):
            if yard % 10 == 0:
                continue
            y = self._yard_to_y(yard)
            for cx in (third, 2 * third):
                pygame.draw.line(self.screen, self.C_HASH,
                                 (cx - 10, y), (cx + 10, y), 1)

    def draw_scrimmage_line(self, yard_line):
        """Light-blue scrimmage line."""
        y = self._yard_to_y(yard_line)
        pygame.draw.line(self.screen, self.C_SCRIMMAGE,
                         (0, y), (self.fw, y), 2)

    def draw_first_down_line(self, yard_line, yards_to_go):
        """Orange first-down line."""
        first_down_yard = yard_line + yards_to_go
        if first_down_yard >= 100:
            return
        y = self._yard_to_y(first_down_yard)
        pygame.draw.line(self.screen, self.C_FIRST_DN,
                         (0, y), (self.fw, y), 2)

    # ──────────────────────────────────────────────────────────────────────────
    # UI panels
    # ──────────────────────────────────────────────────────────────────────────

    def draw_analytics_bg(self):
        """Dark navy sidebar with a dot-grid texture and title."""
        ax = config.FIELD_WIDTH
        aw = config.ANALYTICS_WIDTH
        ah = config.WINDOW_HEIGHT

        # Base fill
        pygame.draw.rect(self.screen, self.C_ANAL_BG, (ax, 0, aw, ah))

        # Subtle dot grid
        dot_spacing = 18
        for gx in range(ax + dot_spacing, ax + aw, dot_spacing):
            for gy in range(dot_spacing, ah, dot_spacing):
                pygame.draw.circle(self.screen, self.C_ANAL_LINE, (gx, gy), 1)

        # Divider
        pygame.draw.line(self.screen, (50, 55, 100),
                         (ax, 0), (ax, ah), 2)

        # Title bar
        bar_h = 44
        pygame.draw.rect(self.screen, (18, 22, 48), (ax, 0, aw, bar_h))
        pygame.draw.line(self.screen, (50, 80, 180),
                         (ax, bar_h), (ax + aw, bar_h), 1)

        title = self.font_hud.render("ANALYTICS", True, self.C_ANAL_TITLE)
        self.screen.blit(title, (ax + (aw - title.get_width()) // 2, 12))

    def draw_hud(self, game_state):
        """Bottom HUD bar — gradient-like layered rects + game info."""
        hud_h = 36
        hy    = config.WINDOW_HEIGHT - hud_h

        # Two-tone background (slightly lighter strip on top for depth)
        pygame.draw.rect(self.screen, (22, 24, 38), (0, hy, self.fw, 3))
        pygame.draw.rect(self.screen, self.C_HUD_BG,  (0, hy + 3, self.fw, hud_h - 3))

        # Accent line at top of HUD
        pygame.draw.line(self.screen, self.C_HUD_ACCENT,
                         (0, hy), (self.fw, hy), 2)

        # Quarter badge
        quarter_text = f"Q{game_state.quarter}"
        q_surf = self.font_score.render(quarter_text, True, self.C_HUD_ACCENT)
        self.screen.blit(q_surf, (10, hy + (hud_h - q_surf.get_height()) // 2))

        # Thin vertical divider after quarter
        div_x = 10 + q_surf.get_width() + 8
        pygame.draw.line(self.screen, (50, 55, 80),
                         (div_x, hy + 6), (div_x, hy + hud_h - 6), 1)

        # Main HUD info
        hud_info = game_state.get_hud_info()
        info_surf = self.font_hud.render(hud_info, True, self.C_WHITE)
        self.screen.blit(info_surf,
                         (div_x + 10,
                          hy + (hud_h - info_surf.get_height()) // 2))

    # ──────────────────────────────────────────────────────────────────────────
    # Master draw call
    # ──────────────────────────────────────────────────────────────────────────

    def draw_all(self, game_state):
        self.draw_field()
        self.draw_end_zones()
        self.draw_yard_lines()
        self.draw_hash_marks()
        self.draw_scrimmage_line(game_state.yard_line)
        self.draw_first_down_line(game_state.yard_line, game_state.yards_to_go)
        self.draw_analytics_bg()
        self.draw_hud(game_state)