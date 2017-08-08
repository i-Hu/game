#! C:\Users\patrick\Anaconda3\python.exe
import pygame
import sys
import time
from random import sample

game_active = True
time_active = False
time_end = False

# 数据设置
block_number_width = 20
block_number_height = 20
extra_width = 10
extra_height = 40

mine_number = 50

L = [(1, 1), (1, -1), (1, 0), (0, 1), (0, -1), (-1, -1), (-1, 1), (-1, 0)]

# 屏幕数据
screen_width = block_number_width * 16 + extra_width * 2
screen_height = block_number_height * 16 + extra_height + extra_width

# 导入图片

face_image = pygame.image.load("image/face.bmp")
mine_image = pygame.image.load("image/mines.bmp")
num_image = pygame.image.load("image/num.bmp")
face_images = {}
face_name = ["down", "sunglasses", "sad", ":0", "smile"]
for i in range(5):
    face_images[face_name[i]] = face_image.subsurface((0, i * 24, 24, 24))
mine_images = {}
mine_name = ["up", "flag", "?", "boom", "wrong", "mine", "dk", 8, 7, 6, 5, 4, 3, 2, 1, 0]
for i in range(16):
    mine_images[mine_name[i]] = mine_image.subsurface((0, i * 16, 16, 16))
num_images = {}
num_name = ["-", "space", '9', '8', '7', '6', '5', '4', '3', '2', '1', '0']
for i in range(12):
    num_images[num_name[i]] = num_image.subsurface((0, i * 23, 13, 23))


# 方块类
class Block:
    def __init__(self, x_number, y_number, screen):
        self.screen = screen
        self.rect = mine_images["up"].get_rect()
        self.rect.x = extra_width + x_number * 16
        self.rect.y = extra_height + y_number * 16
        self.show_image = "up"
        self.should_image = "up"
        self.mine = 0
        self.open = False

    def update(self, x, y, block_dir, face):
        if self.show_image != "flag" and self.show_image != "?":
            if self.mine == "mine":
                boom(block_dir, face)
                self.show_image = "boom"
                self.should_image = "boom"
            else:
                self.show_image = self.mine
                self.should_image = self.mine
                self.check_near_blocks(x, y, block_dir)
                self.open = True

    def check_near_blocks(self, x, y, block_dir):
        if block_dir[(x, y)].open:
            pass
        elif self.mine == "mine":
            pass
        elif self.show_image == "flag":
            pass
        elif self.show_image == "?":
            pass
        elif self.mine == 0:
            block_dir[(x, y)].open = True
            self.show_image = self.mine
            self.should_image = self.mine
            for m, n in L:
                if 0 <= x + m < block_number_width and 0 <= y + n < block_number_height:
                    block_dir[(x + m, y + n)].check_near_blocks(x + m, y + n, block_dir)
        else:
            block_dir[(x, y)].open = True
            self.show_image = self.mine
            self.should_image = self.mine

    def blitme(self):
        self.screen.blit(mine_images[self.show_image], self.rect)


# 笑脸类
class Face:
    def __init__(self, screen):
        self.screen = screen
        self.rect = face_images["smile"].get_rect()
        self.rect.centery = extra_height / 2
        self.rect.centerx = screen_width / 2
        self.image = "smile"

    def update(self, block_dir):
        pass

    def blitme(self):
        self.screen.blit(face_images[self.image], self.rect)


# 数字类
class Num:
    def __init__(self, a, screen):
        self.screen = screen
        self.rect = num_images['0'].get_rect()
        if a < 3:
            self.rect.x = extra_width + a * 13 + 5
        else:
            self.rect.x = extra_width + block_number_width * 16 - 5 - 39 + (a - 3) * 13
        self.rect.centery = extra_height / 2
        self.image = "0"

    def blitme(self):
        self.screen.blit(num_images[self.image], self.rect)


def boom(block_dir, face):
    global game_active, time_active, time_end
    face.image = "sad"
    for block in block_dir.values():
        if block.mine == "mine" and block.show_image != "flag":
            block.show_image = "mine"
            block.should_image = "mine"
    game_active = False
    time_active = True
    time_end = True


def create_block(screen):
    block_dir = {}
    for m in range(block_number_width):
        for n in range(block_number_height):
            block_dir[(m, n)] = Block(m, n, screen)
    return block_dir


def create_mine(block_dir):
    mine_list = sample(block_dir.keys(), mine_number)
    for xy in mine_list:
        block_dir[xy].mine = "mine"


def create_mine_number(block_dir):
    for (x, y), block in block_dir.items():
        if block.mine != "mine":
            count = 0
            for m, n in L:
                if 0 <= x + m < block_number_width and 0 <= y + n < block_number_height:
                    if block_dir[(x + m, y + n)].mine == "mine":
                        count += 1
            block.mine = count


def check_events(face, block_dir):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            global left, mid, right, game_active, block_down
            if game_active:
                face.image = ":0"
            left = 0
            mid = 0
            right = 0
            pressed_array = pygame.mouse.get_pressed()
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if pressed_array == (1, 0, 0):
                if game_active is True:
                    for block in block_dir.values():
                        if block.rect.collidepoint(mouse_x, mouse_y):
                            check_left_down(block)
                left = 1
            elif pressed_array == (0, 1, 0) or pressed_array == (1, 0, 1):
                if game_active is True:
                    for (x, y), block in block_dir.items():
                        if block.rect.collidepoint(mouse_x, mouse_y):
                            check_mid_down(block_dir, block, x, y)
                mid = 1
            elif pressed_array == (0, 0, 1):
                if game_active is True:
                    right = 1
            elif game_active and face.rect.collidepoint(mouse_x, mouse_y):
                face.image = ":0"
        elif event.type == pygame.MOUSEMOTION and game_active:
            pressed_array = pygame.mouse.get_pressed()
            if pressed_array == (1, 0, 0):
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for block in block_dir.values():
                    if block.rect.collidepoint(mouse_x, mouse_y):
                        if block != block_down and block.should_image == "up":
                            block_down.show_image = block_down.should_image
                            block.show_image = 0
                            block_down = block
        elif event.type == pygame.MOUSEBUTTONUP:
            if game_active is True:
                face.image = "smile"
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if face.rect.collidepoint(mouse_x, mouse_y):
                restart(block_dir, face)
            for (x, y), block in block_dir.items():
                if block.rect.collidepoint(mouse_x, mouse_y) and game_active is True:
                    if left == 1:
                        check_left_up(block_dir, face, block, x, y)
                        break
                    elif mid == 1:
                        check_mid_up(block_dir, face, x, y)
                        break
                    elif right == 1:
                        check_right_up(block)
                        break
            for block in block_dir.values():
                block.show_image = block.should_image


def check_left_down(block):
    if block.should_image == "up":
        block.show_image = 0


def check_mid_down(block_dir, block, x, y):
    if block.show_image != "flag" and block.show_image != "?" and block.open is True:
        count = 0
        for m, n in L:
            if 0 <= x + m < block_number_width and 0 <= y + n < block_number_height:
                if block_dir[(x + m, y + n)].mine == "mine":
                    count += 1
                if block_dir[(x + m, y + n)].show_image == "flag":
                    count -= 1
        if count == 0:
            for m, n in L:
                if 0 <= x + m < block_number_width and 0 <= y + n < block_number_height:
                    if block_dir[(x + m, y + n)].show_image != "flag" and block_dir[(x + m, y + n)].open is False:
                        block_dir[(x + m, y + n)].show_image = 0


def check_left_up(block_dir, face, block, x, y):
    global time_active, block_down
    block_down.show_image = block_down.should_image
    if first_click(block_dir):
        time_active = True
        if block.mine != 0:
            restart(block_dir, face)
            check_left_up(block_dir, face, block, x, y)
        elif block.show_image != "flag":
            block.update(x, y, block_dir, face)
    else:
        block.update(x, y, block_dir, face)


def check_mid_up(block_dir, face, x, y):
    count = 0
    for m, n in L:
        if 0 <= x + m < block_number_width and 0 <= y + n < block_number_height:
            if block_dir[(x + m, y + n)].mine == "mine":
                count += 1
            if block_dir[(x + m, y + n)].show_image == "flag":
                count -= 1
    if count == 0:
        for m, n in L:
            if 0 <= x + m < block_number_width and 0 <= y + n < block_number_height:
                if block_dir[(x + m, y + n)].mine == 0:
                    block_dir[(x + m, y + n)].check_near_blocks(x + m, y + n, block_dir)
                elif block_dir[(x + m, y + n)].show_image != "flag" and block_dir[(x + m, y + n)].open is False:
                    block_dir[(x + m, y + n)].update(x + m, y + n, block_dir, face)


def check_right_up(block):
    if block.show_image == "up":
        block.show_image = "flag"
        block.should_image = "flag"
    elif block.show_image == "flag":
        block.show_image = "?"
        block.should_image = "?"
    elif block.show_image == "?":
        block.show_image = "up"
        block.should_image = "up"


def restart(block_dir, face):
    global game_active, time_active, time_end
    game_active = True
    time_active = False
    time_end = False
    for block in block_dir.values():
        block.mine = 0
        block.show_image = "up"
        block.should_image = "up"
        block.open = False
    create_mine(block_dir)
    create_mine_number(block_dir)
    face.image = "smile"


def first_click(block_dir):
    count = 0
    for block in block_dir.values():
        if block.open is True:
            count += 1
    if count == 0:
        return True
    else:
        return False


def check_end(face, block_dir):
    count = 0
    for block in block_dir.values():
        if block.open is True or block.mine == "mine":
            count += 1
    if count == block_number_width * block_number_height:
        end_game(block_dir, face)
    else:
        count = 0
        for block in block_dir.values():
            if block.mine == "mine" and block.show_image == "flag":
                count += 1
        if count == mine_number:
            end_game(block_dir, face)


def end_game(block_dir, face):
    global game_active, time_active, time_end
    time_active = True
    game_active = False
    time_end = True
    face.image = "sunglasses"
    for block in block_dir.values():
        if block.mine == "mine":
            block.show_image = "flag"
        else:
            block.show_image = block.mine


def count_mine(block_dir):
    count = 0
    for block in block_dir.values():
        if block.show_image == "flag":
            count += 1
    return mine_number - count


def create_num(screen):
    num_dir = {}
    for x in range(6):
        num_dir[x] = Num(x, screen)
    return num_dir


def show_left_mines(num_dir, left_mines):
    left_mine = list(str(left_mines))
    if left_mines < 0:
        while len(left_mine) < 3:
            left_mine.insert(1, "0")
    else:
        while len(left_mine) < 3:
            left_mine.insert(0, "0")
        while len(left_mine) > 3:
            left_mine.pop()
    for x, num in enumerate(left_mine):
        num_dir[x].image = num


def show_time(time_start, time_now, num_dir):
    if time_start:
        use_time = list(str(int(time_now - time_start)))
    else:
        use_time = ['0']
    while len(use_time) < 3:
        use_time.insert(0, "0")
    while len(use_time) > 3:
        use_time.pop()
    for x, num in enumerate(use_time):
        num_dir[x + 3].image = num
    for num in num_dir.values():
        num.blitme()


def run_game():
    global block_down
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height), 0, 32)
    pygame.display.set_caption("Minesweeper")
    block_dir = create_block(screen)
    create_mine(block_dir)
    create_mine_number(block_dir)
    num_dir = create_num(screen)
    face = Face(screen)
    block_down = block_dir[(0, 0)]

    while True:
        screen.fill((230, 230, 230))
        face.blitme()
        for block in block_dir.values():
            block.blitme()
        left_mines = count_mine(block_dir)
        show_left_mines(num_dir, left_mines)
        if not time_active:
            time_start = time.time()
        if not time_end:
            time_now = time.time()
        show_time(time_start, time_now, num_dir)
        pygame.display.update()
        check_end(face, block_dir)
        check_events(face, block_dir)


run_game()


