import random
import config

class Play:
    def __init__(self, game_state, offense, defense):
        self.game_state = game_state
        self.offense = offense
        self.defense = defense

    def run(self):
        """
        Temporary random outcomes.
        Real logic (movement, routes, RL agent) replaces this later.

        Returns dict with keys:
          - yards_gained (int)
          - play_type    (str): 'pass', 'run', 'sack', 'interception'
          - turnover     (bool)
          - touchdown    (bool)
          - safety       (bool)
        """
        return self._temp_result()

    def _temp_result(self):
        """
        Temporary random play result for testing the game loop.
        Roughly mimics real NFL play distribution:
          - 60% pass, 40% run
          - ~5% sack rate, ~3% INT rate
          - Realistic yardage distributions
        """
        roll = random.random()

        # Sack (~5% of plays)
        if roll < 0.05:
            return {
                "yards_gained": random.randint(-8, -1),
                "play_type": "sack",
                "turnover": False,
                "touchdown": False,
                "safety": False
            }

        # Interception (~3% of plays)
        if roll < 0.08:
            return {
                "yards_gained": 0,
                "play_type": "interception",
                "turnover": True,
                "touchdown": False,
                "safety": False
            }

        # Pass play (~55% of plays)
        if roll < 0.63:
            yards = random.randint(-2, 25)
            return {
                "yards_gained": yards,
                "play_type": "pass",
                "turnover": False,
                "touchdown": False,
                "safety": False
            }

        # Run play (~37% of plays)
        yards = random.randint(-3, 15)
        return {
            "yards_gained": yards,
            "play_type": "run",
            "turnover": False,
            "touchdown": False,
            "safety": False
        }