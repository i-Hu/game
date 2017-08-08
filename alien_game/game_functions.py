import json
import pygame
import random
import sys
from time import sleep
from alien import Alien
from bullet import Bullet


# 键位反馈
def check_keydown_events(event, ai_settings, screen, stats, ship, aliens, bullets, scoreboard):
    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:
        fire_bullet(ai_settings, screen, ship, bullets)
    elif event.key == pygame.K_q:
        sys.exit()
    elif event.key == pygame.K_p:
        start_game(ai_settings, screen, stats, scoreboard, ship, aliens, bullets)


def check_keyup_events(event, ship):
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    if event.key == pygame.K_LEFT:
        ship.moving_left = False


def check_events(ai_settings, screen, stats, ship, aliens, bullets, play_button, scoreboard):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, screen, stats, ship, aliens, bullets, scoreboard)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_button(ai_settings, stats, screen, play_button, mouse_x, mouse_y, ship, aliens, bullets, scoreboard)


def update_screen(ai_settings, screen, stats, ship, aliens, bullets, play_button, scoreboard):
    # 创建屏幕
    screen.fill(ai_settings.bg_color)
    # 刷新子弹、船、外星人，得分
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    ship.blitme()
    aliens.draw(screen)
    scoreboard.show_score()
    if not stats.game_active:
        play_button.draw_button()
    pygame.display.flip()


def update_bullets(ai_settings, screen, stats, ship, aliens, bullets, scoreboard):
    bullets.update()
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)

    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)

    if collisions:
        for aliens in collisions.values():
            stats.kill_num += 1 * len(aliens)
            stats.score += ai_settings.alien_points * len(aliens)
            scoreboard.prep_score()
        check_high_score(stats, scoreboard)

    # 升级
    if stats.kill_num//10 > stats.level:
        ai_settings.increase_speed()
        stats.level += 1
        scoreboard.prep_level()


def fire_bullet(ai_settings, screen, ship, bullets):
    if len(bullets) < ai_settings.bullet_allowed:
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)


def create_aline(ai_settings, screen, aliens):
    while len(aliens) < 4:
        alien = Alien(ai_settings, screen)
        alien_width = alien.rect.width
        alien_height = alien.rect.height
        alien.x = random.randint(alien_width, ai_settings.screen_width-alien_width)
        alien.y = -alien_height * 2
        alien.rect.y = alien.y
        alien.rect.x = alien.x
        aliens.add(alien)


def update_aliens(ai_settings, stats, scoreboard, screen, ship, aliens, bullets):
    create_aline(ai_settings, screen, aliens)
    aliens.update()

    check_aliens_bottom(ai_settings, stats, scoreboard, screen, ship, aliens, bullets)
    if pygame.sprite.spritecollideany(ship, aliens):
        ship_hit(ai_settings, stats, scoreboard, screen, ship, aliens, bullets)


def ship_hit(ai_settings, stats, scoreboard, screen, ship, aliens, bullets):
    if stats.ships_left > 0:
        stats.ships_left -= 1
        scoreboard.prep_ships()
        aliens.empty()
        bullets.empty()
        ship.center_ship()
        sleep(0.5)
    else:
        aliens.empty()
        bullets.empty()
        pygame.mouse.set_visible(True)
        stats.game_active = False


def check_aliens_bottom(ai_settings, stats, scoreboard, screen, ship, aliens, bullets):
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            ship_hit(ai_settings, stats, scoreboard, screen, ship, aliens, bullets)
            break


def check_play_button(ai_settings, stats, screen, play_button, mouse_x, mouse_y, ship, aliens, bullets, scoreboard):
    button_click = play_button.rect.collidepoint(mouse_x, mouse_y)
    if button_click and not stats.game_active:
        start_game(ai_settings, screen, stats, scoreboard, ship, aliens, bullets)


def start_game(ai_settings, screen, stats, scoreboard, ship, aliens, bullets):
    ai_settings.initialize_dynamic_settings()
    pygame.mouse.set_visible(False)
    stats.reset_stats()
    scoreboard.prep_ships()
    scoreboard.prep_level()
    check_high_score(stats, scoreboard)
    scoreboard.prep_score()
    stats.game_active = True
    aliens.empty()
    bullets.empty()
    ship.center_ship()
    create_aline(ai_settings, screen, aliens)


def check_high_score(stats, scoreboard):
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        with open('high_score.json', 'w') as hs:
            json.dump(stats.high_score, hs)
        scoreboard.prep_high_score(stats)

