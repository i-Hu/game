import pygame, random, json, sys
from pygame.sprite import Sprite, Group
from time import sleep


class Settings:
    def __init__(self):
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (230, 230, 230)

        self.ship_limit = 3

        self.fleet_drop_speed = 10

        self.bullet_width = 3
        self.bullet_height = 10
        self.bullet_color = (60, 60, 60)
        self.bullet_allowed = 5

        self.speed_scale = 1.1
        self.score_scale = 1.5
        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        self.ship_speed_factor = 1.2
        self.alien_speed_factor = 1
        self.bullet_speed_factor = 1
        self.alien_points = 50

        self.fleet_direction = 1

    def increase_speed(self):
        self.alien_speed_factor *= self.speed_scale
        self.bullet_speed_factor *= self.speed_scale
        self.alien_points = int(self.alien_points * self.score_scale)


class Ship(Sprite):
    def __init__(self, ai_settings, screen):
        super(Ship, self).__init__()
        self.screen = screen
        self.ai_settings = ai_settings

        self.image = pygame.image.load('images/ship.png')
        self.rect = self.image.get_rect()
        self.screen_rect = screen.get_rect()

        self.rect.centerx = self.screen_rect.centerx
        self.rect.bottom = self.screen_rect.bottom

        self.center = float(self.rect.centerx)

        self.moving_right = False
        self.moving_left = False

    def update(self):
        if self.moving_right and self.rect.centerx < self.screen_rect.right:
            self.center += self.ai_settings.ship_speed_factor
        if self.moving_left and self.rect.centerx > 0:
            self.center -= self.ai_settings.ship_speed_factor

        self.rect.centerx = self.center

    def blitme(self):
        self.screen.blit(self.image, self.rect)

    def center_ship(self):
        self.center = self.screen_rect.centerx


class Alien(Sprite):
    def __init__(self, ai_settings, screen):
        super(Alien, self).__init__()
        self.screen = screen
        self.ai_settings = ai_settings

        # 导入外星人图片
        self.image = pygame.image.load('images/alien.png')
        self.rect = self.image.get_rect()

        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        self.x = float(self.rect.x)

    def blitme(self):
        self.screen.blit(self.image, self.rect)

    def update(self, *args):
        self.y += (self.ai_settings.alien_speed_factor * self.ai_settings.fleet_direction * 0.15)
        self.rect.y = self.y


class Bullet(Sprite):
    def __init__(self, ai_settings, screen, ship):
        super(Bullet, self).__init__()
        self.screen = screen

        self.rect = pygame.Rect(0, 0, ai_settings.bullet_width, ai_settings.bullet_height)
        self.rect.centerx = ship.rect.centerx
        self.rect.top = ship.rect.top

        self.y = float(self.rect.y)

        self.color = ai_settings.bullet_color
        self.speed_factor = ai_settings.bullet_speed_factor

    def update(self, *args):
        self.y -= self.speed_factor
        self.rect.y = self.y

    def draw_bullet(self):
        pygame.draw.rect(self.screen, self.color, self.rect)


class Scoreboard:
    def __init__(self, ai_settings, screen, stats):
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.ai_settings = ai_settings
        self.stats = stats

        self.text_color = (30, 30, 30)
        self.font = pygame.sysfont.SysFont(None, 36)

        self.prep_ships()
        self.prep_score()
        self.prep_level()
        self.prep_high_score(stats)

    def prep_score(self):
        rounded_score = int(round(self.stats.score, -1))
        score_str = "{:,}".format(rounded_score)
        self.score_image = self.font.render("Score: " + score_str, True, self.text_color)

        self.score_rect = self.score_image.get_rect()
        self.score_rect.right = self.screen_rect.right - 20
        self.score_rect.top = 20

    def show_score(self):
        self.screen.blit(self.score_image, self.score_rect)
        self.screen.blit(self.high_score_image, self.high_score_rect)
        self.screen.blit(self.level_image, self.level_rect)
        self.ships.draw(self.screen)

    def prep_high_score(self, stats):
        high_score = stats.high_score
        high_score_str = "{:,}".format(high_score)
        self.high_score_image = self.font.render("High Score: " + high_score_str, True, self.text_color)

        self.high_score_rect = self.high_score_image.get_rect()
        self.high_score_rect.centerx = self.screen_rect.centerx
        self.high_score_rect.top = 20

    def prep_level(self):
        self.level_image = self.font.render("Level: " + str(round(self.stats.level)), True, self.text_color)

        self.level_rect = self.level_image.get_rect()
        self.level_rect.right = self.screen_rect.right - 20
        self.level_rect.top = self.score_rect.bottom + 10

    def prep_ships(self):
        self.ships = Group()
        for ship_number in range(self.stats.ships_left):
            ship = Ship(self.ai_settings, self.screen)
            ship.rect.x = 10 + ship_number * ship.rect.width
            ship.rect.y = 10
            self.ships.add(ship)


class GameStats:
    def __init__(self, ai_settings):
        try:
            with open('high_score.json') as hs:
                self.high_score = json.load(hs)
        except FileNotFoundError:
            with open('high_score.json', 'w') as hs:
                json.dump(0, hs)
                self.high_score = 0
        self.ai_settings = ai_settings
        self.reset_stats()
        self.game_active = False

    def reset_stats(self):
        self.ships_left = self.ai_settings.ship_limit
        self.score = 0
        self.level = 1
        self.kill_num = 0


class Button():
    def __init__(self, ai_settings, screen, msg):
        self.screen = screen
        self.screen_rect = screen.get_rect()

        self.width, self.height = 200, 50
        self.button_color = (0, 255, 0)
        self.text_color = (255, 255, 255)
        self.font = pygame.sysfont.SysFont(None, 48)

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.screen_rect.center

        self.prep_msg(msg)

    def prep_msg(self, msg):
        self.msg_image = self.font.render(msg, True, self.text_color, self.button_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def draw_button(self):
        self.screen.fill(self.button_color, self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)


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
            check_play_button(ai_settings, stats, screen, play_button, mouse_x, mouse_y, ship, aliens, bullets,
                              scoreboard)


def fire_bullet(ai_settings, screen, ship, bullets):
    if len(bullets) < ai_settings.bullet_allowed:
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)


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
    if stats.kill_num // 10 > stats.level:
        ai_settings.increase_speed()
        stats.level += 1
        scoreboard.prep_level()


def create_aline(ai_settings, screen, aliens):
    while len(aliens) < 4:
        alien = Alien(ai_settings, screen)
        alien_width = alien.rect.width
        alien_height = alien.rect.height
        alien.x = random.randint(alien_width, ai_settings.screen_width - alien_width)
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
        check_events(ai_settings, screen, stats, ship, aliens, bullets, play_button, scoreboard)

        if stats.game_active:
            ship.update()
            update_aliens(ai_settings, stats, scoreboard, screen, ship, aliens, bullets)
            update_bullets(ai_settings, screen, stats, ship, aliens, bullets, scoreboard)

        update_screen(ai_settings, screen, stats, ship, aliens, bullets, play_button, scoreboard)


run_game()
