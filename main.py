# main.py
import sys
import random
import math
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
from agents.defense import DefensiveAI

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
    defensive_ai = DefensiveAI()
    game_log = []
    current_coverage = "cover_1"

    total_frames_per_play = int(config.FPS * config.PLAY_DURATION_SECONDS)

    throw_start = None
    throw_end = None
    throw_progress = 0.0
    throwing = False

    def log_play(possession, display_type, yards, outcome, hud, coverage):
        entry_type = "normal"
        if outcome == "touchdown": entry_type = "touchdown"
        elif outcome in ("turnover", "turnover_on_downs"): entry_type = "turnover"
        elif outcome == "field_goal": entry_type = "field_goal"
        elif outcome == "punt": entry_type = "punt"
        elif outcome == "safety": entry_type = "safety"

        parts = hud.split("|")
        down_dist = parts[0].strip() if len(parts) > 0 else ""
        yard_pos = parts[2].strip() if len(parts) > 2 else ""

        yards_str = f"{yards:+d} yds"
        outcome_clean = outcome.replace("_", " ")
        pos = possession[:3].upper()
        cov = coverage.upper().replace("_", " ")

        text = f"[{pos}]  {display_type:<13}  {yards_str:<9}  {down_dist:<12}  {yard_pos:<12}  {outcome_clean:<18}  {cov}"
        game_log.append({'text': text, 'type': entry_type})

    def assign_blocking(offense, defense):
        ol = [p for p in offense if p.position == "OL"]
        rushers = [p for p in defense if getattr(p, 'coverage_type', '') in ('rush', 'blitz')]
        for i, lineman in enumerate(ol):
            lineman.block_target = rushers[i] if i < len(rushers) else None

    def update_blocking(offense, defense):
        qb = next((p for p in offense if p.position == "QB"), None)
        for p in offense:
            if p.position != "OL":
                continue
            target = getattr(p, 'block_target', None)
            if not target or not qb:
                continue
            p.target_x = (target.x + qb.x) / 2
            p.target_y = (target.y + qb.y) / 2
            dist = math.sqrt((p.x - target.x)**2 + (p.y - target.y)**2)
            if dist < 25:
                target.target_x = target.x + (target.x - qb.x) * 0.1
                target.target_y = target.y + (target.y - qb.y) * 0.1

    def setup_play():
        nonlocal throw_start, throw_end, throw_progress, throwing, current_coverage
        throw_start = None
        throw_end = None
        throw_progress = 0.0
        throwing = False
        for p in offense + defense:
            p.reset_play_state()
        animator.set_player_positions(offense, defense, game)
        assign_routes(offense)
        animator.reset_play(offense + defense)
        current_coverage = defensive_ai.pick_coverage()
        scrimmage_y = renderer._yard_to_y(game.yard_line)
        defensive_ai.setup_coverage(offense, defense, scrimmage_y)
        assign_blocking(offense, defense)
        print(f"  Coverage: {current_coverage}")

    setup_play()
    frame_count = 0

    running = True
    while running and not game.game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                renderer.handle_click(event.pos)

        if frame_count < total_frames_per_play:
            for p in offense:
                advance_route(p)
            update_blocking(offense, defense)
            defensive_ai.update_frame(offense, defense)
            move_all_players(offense + defense)

            halfway = total_frames_per_play // 2
            if frame_count == halfway:
                qb = next((p for p in offense if p.position == "QB"), None)
                wrs = [p for p in offense if p.position == "WR"]
                if qb and wrs:
                    target = random.choice(wrs)
                    throw_start = (int(qb.x), int(qb.y))
                    throw_end = (int(target.x), int(target.y))
                    throwing = True

            if throwing:
                throw_progress = min(
                    throw_progress + (1.0 / (total_frames_per_play // 2)),
                    1.0
                )

            frame_count += 1

        else:
            current_possession = game.possession
            if game.possession == "offense":
                play = Play(game, offense, defense)
                result = play.run()
            else:
                result = game.run_defensive_play()

            outcome = game.apply_play_result(result)

            display_type = result['play_type']
            if outcome in ["punt", "field_goal", "missed_field_goal", "turnover_on_downs", "turnover"]:
                display_type = outcome

            log_play(current_possession, display_type, result['yards_gained'], outcome, game.get_hud_info(), current_coverage)
            print(f"  [{current_possession:7}] {display_type:15} | "
                f"{result['yards_gained']:+3d} yds -> {outcome:20} | "
                f"{game.get_hud_info()}")

            if game.check_advance_quarter():
                game.advance_quarter()
                if not game.game_over:
                    game_log.append({'text': f'── Quarter {game.quarter} ──', 'type': 'quarter'})
                    print(f"\n--- Quarter {game.quarter} ---\n")

            setup_play()
            frame_count = 0

        renderer.draw_all(game, game_log)
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