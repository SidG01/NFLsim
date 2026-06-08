# test_renderer.py
import sys
import pygame
import config
from visuals.field_renderer import FieldRenderer
from visuals.animator import Animator
from engine.game import GameState
from players.roster import load_roster
from simulation.routes import assign_routes

pygame.init()
screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
pygame.display.set_caption("NFL Sim")
clock = pygame.time.Clock()

offense, defense = load_roster(config.TEAM)
renderer = FieldRenderer(screen)
animator = Animator(screen)
game     = GameState()

# Place players and assign routes
animator.set_player_positions(offense, defense, game)
assign_routes(offense)
animator.reset_play(offense + defense)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    renderer.draw_all(game)
    animator.update_trails(offense)
    animator.draw_all(offense, defense)
    pygame.display.flip()
    clock.tick(config.FPS)

pygame.quit()
sys.exit()