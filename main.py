# main.py
import sys
import random
import pygame
import config
from engine.game import GameState
from engine.play import Play
from engine.field import Field
from players.roster import load_roster
from simulation.routes import assign_routes, advance_route
from simulation.movement import move_all_players
from visuals.field_renderer import FieldRenderer
from visuals.animator import Animator

def run():
    pygame.init()
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption("NFL AI Sim")
    clock = pygame.time.Clock()

    offense, defense = load_roster(config.TEAM)
    field = Field()
    renderer = FieldRenderer(screen)
    animator = Animator(screen)
    game = GameState()

    total_frames_per_play = int(config.FPS * config.PLAY_DURATION_SECONDS)

    throw_start = None
    throw_end = None
    throw_progress = 0.0
    throwing = False

    def update_defense(offense, defense):
        qb = next((p for p in offense if p.position == "QB"), None)
        wrs = [p for p in offense if p.position == "WR"]
        cbs = [p for p in defense if p.position == "CB"]

        # CBs follow their assigned WR
        for i, cb in enumerate(cbs):
            if i < len(wrs):
                cb.target_x = wrs[i].x
                cb.target_y = wrs[i].y

        # DL rushes toward QB
        if qb:
            for p in defense:
                if p.position == "DL":
                    p.target_x = qb.x
                    p.target_y = qb.y

        # LBs drift upfield slightly
        for p in defense:
            if p.position == "LB":
                p.target_y -= 0.5

        # Safeties drift toward midfield
        for p in defense:
            if p.position == "S":
                p.target_y -= 0.3

    def setup_play():
        nonlocal throw_start, throw_end, throw_progress, throwing
        throw_start = None
        throw_end = None
        throw_progress = 0.0
        throwing = False
        for p in offense + defense:
            p.reset_play_state()
        animator.set_player_positions(offense, defense, game)
        assign_routes(offense)
        animator.reset_play(offense + defense)

    setup_play()
    frame_count = 0

    running = True
    while running and not game.game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if frame_count < total_frames_per_play:
            for p in offense:
                advance_route(p)
            update_defense(offense, defense)
            move_all_players(offense + defense)

            # Trigger throw at halfway point of the play
            halfway = total_frames_per_play // 2
            if frame_count == halfway:
                qb  = next((p for p in offense if p.position == "QB"), None)
                wrs = [p for p in offense if p.position == "WR"]
                if qb and wrs:
                    target      = random.choice(wrs)
                    throw_start = (int(qb.x), int(qb.y))
                    throw_end   = (int(target.x), int(target.y))
                    throwing    = True

            # Advance throw progress
            if throwing:
                throw_progress = min(
                    throw_progress + (1.0 / (total_frames_per_play // 2)),
                    1.0
                )

            frame_count += 1

        else:
            # ── Play is over — calculate result ───────────────
            current_possession = game.possession
            if game.possession == "offense":
                play   = Play(game, offense, defense)
                result = play.run()
            else:
                result = game.run_defensive_play()

            outcome = game.apply_play_result(result)

            display_type = result['play_type']
            if outcome in ["punt", "field_goal", "missed_field_goal",
                           "turnover_on_downs", "turnover"]:
                display_type = outcome

            print(f"  [{current_possession:7}] {display_type:15} | "
                  f"{result['yards_gained']:+3d} yds -> {outcome:20} | "
                  f"{game.get_hud_info()}")

            if game.check_advance_quarter():
                game.advance_quarter()
                if not game.game_over:
                    print(f"\n--- Quarter {game.quarter} ---\n")

            setup_play()
            frame_count = 0

        # Draw everything
        renderer.draw_all(game)
        animator.update_trails(offense)
        animator.draw_all(offense, defense, throw_start, throw_end, throw_progress)
        pygame.display.flip()
        clock.tick(config.FPS)

    print(f"\nFINAL: OFF {game.score_offense} - DEF {game.score_defense}")
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    print("--- Quarter 1 ---\n")
    run()