import pygame
from random import randrange, choice

number_images = {}
num_name = [0, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]
for name in num_name:
    number_images[name] = pygame.image.load('images/%s.png' % name)


class Number:
    def __init__(self, screen):
        self.screen = screen
        self.rect = number_images[2].get_rect()


class Fix:
    def __init__(self, screen):
        self.screen = screen
        self.screen_rect = screen.get_rect()

    def xyz(self):
        self.rect = self.image.get_rect()

    def blitme(self):
        self.screen.blit(self.image, self.rect)


class Button:
    def __init__(self, screen, score, best):
        self.screen = screen
        self.font = pygame.sysfont.SysFont(None, 28)
        self.restart_image = pygame.image.load('images/restart.png')
        self.restart_rect = self.restart_image.get_rect()
        self.restart_rect.centerx = score.rect.centerx
        self.restart_rect.y = 100
        self.exit_image = pygame.image.load('images/exit.png')
        self.exit_rect = self.exit_image.get_rect()
        self.exit_rect.centerx = best.rect.centerx
        self.exit_rect.y = 100

    def check_button(self, height, width, mouse_x, mouse_y, score_num):
        restart_click = self.restart_rect.collidepoint(mouse_x, mouse_y)
        exit_click = self.exit_rect.collidepoint(mouse_x, mouse_y)
        if restart_click:
            return reset(height, width, score_num)
        if exit_click:
            quit()

    def show_button(self):
        self.screen.blit(self.restart_image, self.restart_rect)
        self.screen.blit(self.exit_image, self.exit_rect)


class Scoreboard:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.sysfont.SysFont(None, 42)

    def check_score(self, score, best, score_num, highscore_num):
        if score_num > highscore_num:
            highscore_num = score_num
        self.score_image = self.font.render(str(score_num), True, (250, 250, 250))
        self.score_rect = self.score_image.get_rect()
        self.score_rect.centerx = score.rect.centerx
        self.score_rect.y = 52
        self.highscore_image = self.font.render(str(highscore_num), True, (250, 250, 250))
        self.highscore_rect = self.highscore_image.get_rect()
        self.highscore_rect.centerx = best.rect.centerx
        self.highscore_rect.y = 52
        return score_num, highscore_num

    def show_score(self):
        self.screen.blit(self.score_image, self.score_rect)
        self.screen.blit(self.highscore_image, self.highscore_rect)


def check_events(height, width, field, score_num, button):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
        elif event.type == pygame.KEYDOWN:
            movex = 0
            field, score_num = check_keydown_event(event, height, width, field, score_num, movex)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            field, score_num = button.check_button(height, width, mouse_x, mouse_y, score_num)

    return field, score_num


def check_keydown_event(event, height, width, field, score_num, movex):
    if event.key == pygame.K_w or event.key == pygame.K_UP:
        field = transpose(field)
        for i in range(height):
            if row_is_left_movable(field[i]):
                field[i], score_num = move_row_left(field[i], score_num)
                movex = 1
        if movex == 1:
            spawn(height, width, field)
        field = transpose(field)
    elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
        for i in range(height):
            if row_is_left_movable(field[i]):
                field[i], score_num = move_row_left(field[i], score_num)
                movex = 1
        if movex == 1:
            spawn(height, width, field)
    elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
        field = transpose(field)
        field = invert(field)
        for i in range(height):
            if row_is_left_movable(field[i]):
                field[i], score_num = move_row_left(field[i], score_num)
                movex = 1
        if movex == 1:
            spawn(height, width, field)
        field = invert(field)
        field = transpose(field)
    elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
        field = invert(field)
        for i in range(height):
            if row_is_left_movable(field[i]):
                field[i], score_num = move_row_left(field[i], score_num)
                movex = 1
        if movex == 1:
            spawn(height, width, field)
        field = invert(field)
    return field, score_num


def row_is_left_movable(row):
    def change(i):
        if row[i] == 0 and row[i + 1] != 0:  # 可以移动
            return True
        if row[i] != 0 and row[i + 1] == row[i]:  # 可以合并
            return True
        return False

    return any(change(i) for i in range(len(row) - 1))


def move_row_left(row, score_num):
    def tighten(row):  # 把零散的非零单元挤到一块
        new_row = [i for i in row if i != 0]
        new_row += [0 for i in range(len(row) - len(new_row))]
        return new_row

    def merge(row, score_num):  # 对邻近元素进行合并
        pair = False
        new_row = []
        for i in range(len(row)):
            if pair:
                new_row.append(2 * row[i])
                score_num += 2 * row[i]
                pair = False
            else:
                if i + 1 < len(row) and row[i] == row[i + 1]:
                    pair = True
                    new_row.append(0)
                else:
                    new_row.append(row[i])
        assert len(new_row) == len(row)
        return new_row, score_num

    row = tighten(row)
    row, score_num = merge(row, score_num)
    row = tighten(row)
    return row, score_num


def transpose(field):
    return [list(row) for row in zip(*field)]


def invert(field):
    return [row[::-1] for row in field]


def reset(height, width, score_num):
    score_num = 0
    field = [[0 for i in range(height)] for j in range(width)]
    spawn(height, width, field)
    spawn(height, width, field)
    return field, score_num


def spawn(height, width, field):
    new_element = 4 if randrange(100) > 89 else 2
    i, j = choice([(i, j) for i in range(height) for j in range(width) if field[i][j] == 0])
    field[i][j] = new_element


def show_number(height, width, field, screen):
    for i in range(height):
        for j in range(width):
            num = Number(screen)
            n = field[i][j]
            num.image = number_images[n]
            num.rect.x = 21 + j * 92
            num.rect.y = 159 + i * 92
            num.screen.blit(num.image, num.rect)
    return field


def import_images(screen):
    fix_images = {}
    fix_name = ['frame', 'best', 'score', 'title']
    for name in fix_name:
        fix_images[name] = pygame.image.load('images/%s.png' % name)
    frame = Fix(screen)
    frame.image = fix_images['frame']
    frame.xyz()
    frame.rect.centerx = frame.screen_rect.centerx
    frame.rect.y = 150
    best = Fix(screen)
    best.image = fix_images['best']
    best.xyz()
    best.rect.x = 267
    best.rect.y = 20
    score = Fix(screen)
    score.image = fix_images['score']
    score.xyz()
    score.rect.x = 143
    score.rect.y = 20
    title = Fix(screen)
    title.image = fix_images['title']
    title.xyz()
    title.rect.x = 20
    title.rect.y = 40
    return frame, best, score, title


def run_2048():
    pygame.init()
    screen = pygame.display.set_mode((400, 550))
    pygame.display.set_caption("2048")
    height = 4
    width = 4
    win_score = 2048
    score_num = 0
    highscore_num = 0
    frame, best, score, title = import_images(screen)
    scoreboard = Scoreboard(screen)
    field, score_num = reset(height, width, score_num)
    button = Button(screen, score, best)

    while True:
        pygame.display.flip()
        screen.fill((250, 248, 239))
        field = show_number(height, width, field, screen)
        field, score_num = check_events(height, width, field, score_num, button)
        score_num, highscore_num = scoreboard.check_score(score, best, score_num, highscore_num)
        frame.blitme()
        best.blitme()
        score.blitme()
        title.blitme()
        scoreboard.show_score()
        button.show_button()


run_2048()
