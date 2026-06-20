# visuals/field_renderer.py
import pygame
import config

class FieldRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.font_hud = pygame.font.SysFont("Arial", config.FONT_SIZE_HUD, bold=True)
        self.font_label = pygame.font.SysFont("Arial", config.FONT_SIZE_LABEL + 6, bold=True)
        self.font_score = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 11, bold=False)
        self.font_log = pygame.font.SysFont("Arial", 14, bold=False)
        self.font_btn = pygame.font.SysFont("Arial", 14, bold=True)

        total_yards = config.FIELD_LENGTH_YARDS + 2 * config.END_ZONE_YARDS
        self.pixels_per_yard = config.WINDOW_HEIGHT / total_yards
        self.ez_height = int(config.END_ZONE_YARDS * self.pixels_per_yard)
        self.fw = config.FIELD_WIDTH

        self.C_GREEN_A = (34, 110, 50)
        self.C_GREEN_B = (28, 95, 42)
        self.C_EZ_OFF = (15, 60, 130)
        self.C_EZ_DEF = (140, 20, 20)
        self.C_WHITE = (255, 255, 255)
        self.C_SCRIMMAGE = (100, 220, 255)
        self.C_FIRST_DN = (255, 175, 30)
        self.C_HASH = (200, 200, 200)
        self.C_HUD_BG = (12, 12, 20)
        self.C_HUD_ACCENT = (80, 140, 255)
        self.C_ANAL_BG = (10, 12, 28)
        self.C_ANAL_LINE = (30, 35, 70)
        self.C_ANAL_TITLE = (90, 150, 255)

        self.show_log = False
        self.log_scroll = 0

        # Button sits at the bottom of the analytics panel
        btn_width = (config.ANALYTICS_WIDTH - 40) // 4
        self.log_btn_rect = pygame.Rect(
            config.FIELD_WIDTH + 20,
            config.WINDOW_HEIGHT - 56,
            btn_width,
            36
        )

        # Log panel sits above the button
        self.log_panel_top = 50
        self.log_panel_bottom = config.WINDOW_HEIGHT - 68
        self.log_panel_height = self.log_panel_bottom - self.log_panel_top

    def _yard_to_y(self, yard):
        return int(config.WINDOW_HEIGHT - (config.END_ZONE_YARDS + yard) * self.pixels_per_yard)

    def draw_field(self):
        total_yards = config.FIELD_LENGTH_YARDS + 2 * config.END_ZONE_YARDS
        strip_height = int(10 * self.pixels_per_yard)
        num_strips = total_yards // 10
        for i in range(num_strips):
            color = self.C_GREEN_A if i % 2 == 0 else self.C_GREEN_B
            pygame.draw.rect(self.screen, color, (0, i * strip_height, self.fw, strip_height))

    def draw_end_zones(self):
        pygame.draw.rect(self.screen, self.C_EZ_DEF, (0, 0, self.fw, self.ez_height))
        pygame.draw.rect(self.screen, self.C_EZ_OFF,
                         (0, config.WINDOW_HEIGHT - self.ez_height, self.fw, self.ez_height))
        pygame.draw.line(self.screen, self.C_WHITE, (0, self.ez_height), (self.fw, self.ez_height), 2)
        pygame.draw.line(self.screen, self.C_WHITE,
                         (0, config.WINDOW_HEIGHT - self.ez_height),
                         (self.fw, config.WINDOW_HEIGHT - self.ez_height), 2)
        for text, y_center, shadow_col in [
            ("DEFENSE", self.ez_height // 2, (80, 0, 0)),
            ("OFFENSE", config.WINDOW_HEIGHT - self.ez_height // 2, (0, 20, 80)),
        ]:
            surf = self.font_hud.render(text, True, self.C_WHITE)
            shadow = self.font_hud.render(text, True, shadow_col)
            cx = self.fw // 2 - surf.get_width() // 2
            cy = y_center - surf.get_height() // 2
            self.screen.blit(shadow, (cx + 2, cy + 2))
            self.screen.blit(surf, (cx, cy))

    def draw_yard_lines(self):
        for yard in range(10, 100, 10):
            y = self._yard_to_y(yard)
            display = str(yard) if yard <= 50 else str(100 - yard)
            pygame.draw.line(self.screen, self.C_WHITE, (0, y), (self.fw, y), 2)
            label = self.font_label.render(display, True, self.C_WHITE)
            left_rot = pygame.transform.rotate(label, 90)
            self.screen.blit(left_rot, (4, y - left_rot.get_height() // 2))
            right_rot = pygame.transform.rotate(label, -90)
            self.screen.blit(right_rot, (self.fw - right_rot.get_width() - 4, y - right_rot.get_height() // 2))

    def draw_hash_marks(self):
        third = self.fw // 3
        for yard in range(5, 100, 5):
            if yard % 10 == 0:
                continue
            y = self._yard_to_y(yard)
            for cx in (third, 2 * third):
                pygame.draw.line(self.screen, self.C_HASH, (cx - 10, y), (cx + 10, y), 1)

    def draw_scrimmage_line(self, yard_line):
        y = self._yard_to_y(yard_line)
        pygame.draw.line(self.screen, self.C_SCRIMMAGE, (0, y), (self.fw, y), 2)

    def draw_first_down_line(self, yard_line, yards_to_go):
        first_down_yard = yard_line + yards_to_go
        if first_down_yard >= 100:
            return
        y = self._yard_to_y(first_down_yard)
        pygame.draw.line(self.screen, self.C_FIRST_DN, (0, y), (self.fw, y), 2)

    def draw_analytics_bg(self):
        ax = config.FIELD_WIDTH
        aw = config.ANALYTICS_WIDTH
        ah = config.WINDOW_HEIGHT
        pygame.draw.rect(self.screen, self.C_ANAL_BG, (ax, 0, aw, ah))
        dot_spacing = 18
        for gx in range(ax + dot_spacing, ax + aw, dot_spacing):
            for gy in range(dot_spacing, ah, dot_spacing):
                pygame.draw.circle(self.screen, self.C_ANAL_LINE, (gx, gy), 1)
        pygame.draw.line(self.screen, (50, 55, 100), (ax, 0), (ax, ah), 2)
        bar_h = 44
        pygame.draw.rect(self.screen, (18, 22, 48), (ax, 0, aw, bar_h))
        pygame.draw.line(self.screen, (50, 80, 180), (ax, bar_h), (ax + aw, bar_h), 1)
        title = self.font_hud.render("ANALYTICS", True, self.C_ANAL_TITLE)
        self.screen.blit(title, (ax + (aw - title.get_width()) // 2, 12))

    def draw_log_button(self):
        color = (40, 80, 180) if not self.show_log else (160, 40, 40)
        label = "GAME LOG" if not self.show_log else "GAME LOG"
        pygame.draw.rect(self.screen, color, self.log_btn_rect, border_radius=6)
        pygame.draw.rect(self.screen, (80, 120, 220), self.log_btn_rect, 2, border_radius=6)
        text = self.font_btn.render(label, True, (255, 255, 255))
        self.screen.blit(text, (
            self.log_btn_rect.centerx - text.get_width() // 2,
            self.log_btn_rect.centery - text.get_height() // 2
        ))

    def draw_game_log(self, log_entries):
        if not self.show_log:
            return

        type_colors = {
            "touchdown": (80, 220, 100),
            "turnover": (220, 80, 80),
            "field_goal": (255, 200, 50),
            "punt": (160, 160, 160),
            "quarter": (100, 160, 255),
            "safety": (255, 120, 40),
            "normal": (190, 190, 190),
            "score": (255, 255, 100),
            "meta": (130, 130, 160),
            "coverage": (180, 120, 255),
        }

        ax = config.FIELD_WIDTH
        aw = config.ANALYTICS_WIDTH

        # Panel background — sits above the button, below the title bar
        panel_rect = pygame.Rect(ax + 10, self.log_panel_top, aw - 20, self.log_panel_height)
        pygame.draw.rect(self.screen, (8, 10, 22), panel_rect, border_radius=6)
        pygame.draw.rect(self.screen, (40, 50, 100), panel_rect, 1, border_radius=6)

        # Panel title
        title = self.font_btn.render("GAME LOG", True, (100, 160, 255))
        self.screen.blit(title, (ax + aw // 2 - title.get_width() // 2, self.log_panel_top + 8))
        pygame.draw.line(self.screen, (40, 50, 100),
                         (ax + 20, self.log_panel_top + 28),
                         (ax + aw - 20, self.log_panel_top + 28), 1)

        # Entries
        line_h = 20
        content_top = self.log_panel_top + 36
        content_height = self.log_panel_height - 44
        max_lines = content_height // line_h
        visible = log_entries[-max_lines:] if len(log_entries) > max_lines else log_entries

        # Clip drawing to panel bounds
        clip_rect = pygame.Rect(ax + 10, content_top, aw - 20, content_height)
        self.screen.set_clip(clip_rect)

        y = content_top + 4
        for entry in visible:
            color = type_colors.get(entry.get('type', 'normal'), (190, 190, 190))
            text = self.font_log.render(entry['text'], True, color)
            self.screen.blit(text, (ax + 18, y))
            y += line_h

        self.screen.set_clip(None)

    def handle_click(self, pos):
        if self.log_btn_rect.collidepoint(pos):
            self.show_log = not self.show_log
            return True
        return False

    def draw_hud(self, game_state):
        hud_h = 36
        hy = config.WINDOW_HEIGHT - hud_h
        pygame.draw.rect(self.screen, (22, 24, 38), (0, hy, self.fw, 3))
        pygame.draw.rect(self.screen, self.C_HUD_BG, (0, hy + 3, self.fw, hud_h - 3))
        pygame.draw.line(self.screen, self.C_HUD_ACCENT, (0, hy), (self.fw, hy), 2)
        quarter_text = f"Q{game_state.quarter}"
        q_surf = self.font_score.render(quarter_text, True, self.C_HUD_ACCENT)
        self.screen.blit(q_surf, (10, hy + (hud_h - q_surf.get_height()) // 2))
        div_x = 10 + q_surf.get_width() + 8
        pygame.draw.line(self.screen, (50, 55, 80), (div_x, hy + 6), (div_x, hy + hud_h - 6), 1)
        hud_info = game_state.get_hud_info()
        info_surf = self.font_hud.render(hud_info, True, self.C_WHITE)
        self.screen.blit(info_surf, (div_x + 10, hy + (hud_h - info_surf.get_height()) // 2))

    def draw_all(self, game_state, log_entries=None):
        self.draw_field()
        self.draw_end_zones()
        self.draw_yard_lines()
        self.draw_hash_marks()
        self.draw_scrimmage_line(game_state.yard_line)
        self.draw_first_down_line(game_state.yard_line, game_state.yards_to_go)
        self.draw_analytics_bg()
        if log_entries:
            self.draw_game_log(log_entries)
        self.draw_log_button()
        self.draw_hud(game_state)