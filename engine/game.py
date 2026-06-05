import config
import random

class GameState:
    def __init__(self):
        self.possession = random.choice(["offense", "defense"])
        self.score_offense = 0
        self.score_defense = 0

        self.quarter = 1
        self.play_count = 0

        self.yard_line = 25  # Offense starts at their own 25
        self.down = 1
        self.yards_to_go = config.FIRST_DOWN_YARDS

        # Game status
        self.game_over = False
        self.last_play_result = None

    def advance_quarter(self):
        if self.quarter >= config.QUARTERS:
            self.game_over = True
        else:
            self.quarter += 1
            self.play_count = 0
            if self.quarter == 3:
                self.flip_possession()
                self.reset_drive(25)

    def reset_drive(self, yard_line=25):
        self.yard_line = yard_line
        self.down = 1
        self.yards_to_go = config.FIRST_DOWN_YARDS

    def apply_play_result(self, result):
        """
        Takes the result dict from play.py and updates game state.
        result:
          - yards_gained (int)
          - play_type    (str): 'pass', 'run', 'sack', 'interception'
          - turnover     (bool)
          - touchdown    (bool)
          - safety       (bool)
        """ 
        self.last_play_result = result
        self.play_count += 1

        if result.get("touchdown"):
            if self.possession == "offense": 
                self.score_offense += 7
            else:
                self.score_defense += 7
            self.flip_possession()
            self.reset_drive(25)
            return "touchdown"

        if result.get("safety"):
            if self.possession == "offense": 
                self.score_defense += 2
            else:
                self.score_offense += 2
            self.flip_possession()
            self.reset_drive(25)
            return "safety"

        if result.get("turnover"):
            # Flip field position. Defense takes over where offense was
            self.flip_possession()
            return "turnover"

        # Update field position
        yards = result.get("yards_gained", 0)
        self.yard_line   += yards
        self.yards_to_go -= yards

        # Check for touchdown after yardage
        if self.yard_line >= 100:
            if self.possession == "offense": 
                self.score_offense += 7
            else:
                self.score_defense += 7
            self.flip_possession()
            self.reset_drive(25)
            return "touchdown"

        # Check for safety
        if self.yard_line <= 0:
            if self.possession == "offense": 
                self.score_defense += 2
            else:
                self.score_offense += 2
            self.flip_possession()
            self.reset_drive(25)
            return "safety"

        if self.yards_to_go <= 0:
            self.down = 1
            self.yards_to_go = config.FIRST_DOWN_YARDS
            return "first_down"

        if self.down == 4:
            in_fg_range = self.yard_line >= 65
            go_for_it = random.random() < 0.20 

            if in_fg_range and not go_for_it:
                # FG
                distance = (100 - self.yard_line) + 17
                success_rate = max(0.3, 1.0 - (distance - 30) * 0.02)
                if random.random() < success_rate:
                    if self.possession == "offense": 
                        self.score_offense += 3
                    else:
                        self.score_defense += 3
                    self.flip_possession()
                    self.reset_drive(25)
                    return "field_goal"
                else:
                    self.flip_possession()
                    self.reset_drive(25)
                    return "missed_field_goal"
            elif not in_fg_range and not go_for_it:
                # Punt
                landing_yard = self.yard_line + random.randint(35, 50)
                landing_yard = min(landing_yard, 80)  
                self.flip_possession()
                self.reset_drive(100 - landing_yard)
                return "punt"
            else:
                return "going_for_it"
        elif self.down == 5:
            self.flip_possession()
            return "first_down"
            
        self.down += 1

        return "continue"

    def flip_possession(self):
        self.possession = "defense" if self.possession == "offense" else "offense"
        self.down = 1
        self.yards_to_go = config.FIRST_DOWN_YARDS

    def run_defensive_play(self):
        roll = random.random()
        if roll < 0.05:
            return {"yards_gained": random.randint(-8, -1), "play_type": "sack",
                    "turnover": False, "touchdown": False, "safety": False}
        if roll < 0.08:
            return {"yards_gained": 0, "play_type": "interception",
                    "turnover": True, "touchdown": False, "safety": False}
        if roll < 0.63:
            return {"yards_gained": random.randint(-2, 25), "play_type": "pass",
                    "turnover": False, "touchdown": False, "safety": False}
        return {"yards_gained": random.randint(-3, 15), "play_type": "run",
                "turnover": False, "touchdown": False, "safety": False}


    def check_advance_quarter(self):
        return self.play_count >= config.PLAYS_PER_QUARTER

    def get_hud_info(self):
        down_str = f"{self.down}{'st' if self.down==1 else 'nd' if self.down==2 else 'rd' if self.down==3 else 'th'}"
        return (f"Q{self.quarter}  |  "
                f"{down_str} & {self.yards_to_go}  |  "
                f"OFF {self.score_offense} - DEF {self.score_defense}  |  "
                f"Yard: {self.yard_line}")

    def __repr__(self):
        return (f"GameState(Q{self.quarter}, "
                f"Down={self.down}, "
                f"YardLine={self.yard_line}, "
                f"Score={self.score_offense}-{self.score_defense})")