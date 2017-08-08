import game_functions as gf
import pygame
from button import Button
from game_stats import GameStats
from pygame.sprite import Group
from settings import Settings
from ship import Ship
from scoreboard import Scoreboard


def run_game():
    pygame.init()
    ai_settings = Settings()
    screen = pygame.display.set_mode((ai_settings.screen_width, ai_settings.screen_height))
    pygame.display.set_caption("Alien Invasion")
    play_button = Button(ai_settings, screen, 'Play')
    stats = GameStats(ai_settings)
    scoreboard = Scoreboard(ai_settings, screen, stats)
    ship = Ship(ai_settings, screen)
    aliens = Group()
    bullets = Group()


    while True:
        gf.check_events(ai_settings, screen, stats, ship, aliens, bullets, play_button, scoreboard)

        if stats.game_active:
            ship.update()
            gf.update_aliens(ai_settings, stats, scoreboard, screen, ship, aliens, bullets)
            gf.update_bullets(ai_settings, screen, stats, ship, aliens, bullets, scoreboard)

        gf.update_screen(ai_settings, screen, stats, ship, aliens, bullets, play_button, scoreboard)

run_game()