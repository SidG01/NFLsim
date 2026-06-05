import config
from engine.game import GameState
from engine.play import Play
from players.roster import load_roster

def run_game():
    """Runs one full simulated game and returns the final score."""
    offense, defense = load_roster(config.TEAM)
    game = GameState()

    while not game.game_over:
        current_possession = game.possession
        if game.possession == "offense":
            play = Play(game, offense, defense)
            result = play.run()
        else:
            result = game.run_defensive_play()
        
        outcome = game.apply_play_result(result)
        
        if game.check_advance_quarter():
            game.advance_quarter()
            if not game.game_over:
                print(f"\n--- Quarter {game.quarter} ---\n")

        display_type = result['play_type']
        if outcome in ["punt", "field_goal", "missed_field_goal", "turnover_on_downs"]:
            display_type = outcome
        if outcome == "going_for_it":
            outcome = "went_for_it"
            
        print(f"  [{current_possession:7}] {display_type:15} | "
            f"{result['yards_gained']:+3d} yds -> "
            f"{outcome:20} | {game.get_hud_info()}")

    print(f"\nFINAL: OFF {game.score_offense} - DEF {game.score_defense}")
    return game.score_offense, game.score_defense

if __name__ == "__main__":
    print("--- Quarter 1 ---\n")
    run_game()