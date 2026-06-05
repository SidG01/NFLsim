import config

class Field:
    def __init__(self):
        self.total_yards = config.FIELD_LENGTH_YARDS + (2 * config.END_ZONE_YARDS)
        self.width_yards = 53.3

        self.pixel_width   = config.FIELD_WIDTH
        self.pixel_height  = config.WINDOW_HEIGHT

        # How many pixels = 1 yard
        self.yards_to_px_x = self.pixel_width  / self.width_yards
        self.yards_to_px_y = self.pixel_height / self.total_yards

    def yards_to_pixels(self, x_yards, y_yards):
        px_x = x_yards * self.yards_to_px_x
        px_y = y_yards * self.yards_to_px_y
        return px_x, px_y

    def pixels_to_yards(self, px_x, px_y):
        x_yards = px_x / self.yards_to_px_x
        y_yards = px_y / self.yards_to_px_y
        return x_yards, y_yards

    def scrimmage_to_pixels(self, yard_line):
        """
        yard_line=0  → offense goal line
        yard_line=100 → defense goal line
        """
        # Add end zone offset so yard line 0 isn't at the top edge
        y_yards = config.END_ZONE_YARDS + yard_line
        total_px = y_yards * self.yards_to_px_y
        # Flip: subtract from total height so 0 = bottom, 100 = top
        return self.pixel_height - total_px

    # Zone Detection
    def is_in_offense_endzone(self, yard_line):
        # Safety
        return yard_line <= 0

    def is_in_defense_endzone(self, yard_line):
        # Touchdown
        return yard_line >= 100

    def is_in_redzone(self, yard_line):
        return yard_line >= 80

    def field_goal_range(self, yard_line):
        return yard_line >= 65

    def __repr__(self):
        return f"Field({self.total_yards} yards, {self.pixel_width}x{self.pixel_height}px)"