class Player:
    def __init__(self, name, position, side, stats):
        self.name = name
        self.position = position
        self.side = side

        # stats from bears.json
        self.stats = stats

        self.x = 0.0
        self.y = 0.0

        self.target_x = 0.0
        self.target_y = 0.0
        self.route_index = 0
        self.is_open = False
        self.has_ball = False

    # Returns 50 for route running as CB (CB doesnt have route running)
    def get_stat(self, stat_name, default=50):
        return self.stats.get(stat_name, default)

    def reset_play_state(self):
        self.route_index = 0
        self.is_open = False
        self.has_ball = False

    def __repr__(self):
        speed = self.get_stat("speed")
        return f"Player({self.name}, {self.position}, {self.side}, spd={speed})"