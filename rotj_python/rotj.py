import json
from math import ceil, floor
import os
import pygame
from pygame.locals import *
import pyscroll
from pyscroll.group import PyscrollGroup
from pytmx.util_pygame import load_pygame
import subprocess
import sys
import time

RESOURCES_DIR = '../data'
MAP_NAMES = [
    'overworld',
    'tunnels_of_the_north',
    'cave_of_gadianton',
]
HERO_MOVE_SPEED = 10  # tiles per second.
TILE_SIZE = 16 # pixels
GAME_WIDTH = 256 # pixels (before scaling)
GAME_HEIGHT = 240 # pixels (before scaling)
EVENT_NAMES = {
    QUIT: 'QUIT',
    ACTIVEEVENT: 'ACTIVEEVENT',
    KEYDOWN: 'KEYDOWN',
    KEYUP: 'KEYUP',
    MOUSEMOTION: 'MOUSEMOTION',
    MOUSEBUTTONDOWN: 'MOUSEBUTTONDOWN',
    MOUSEBUTTONUP: 'MOUSEBUTTONUP',
    JOYAXISMOTION: 'JOYAXISMOTION',
    JOYBALLMOTION: 'JOYBALLMOTION',
    JOYHATMOTION: 'JOYHATMOTION',
    JOYBUTTONDOWN: 'JOYBUTTONDOWN',
    JOYBUTTONUP: 'JOYBUTTONUP',
    VIDEORESIZE: 'VIDEORESIZE',
    VIDEOEXPOSE: 'VIDEOEXPOSE',
}

os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"


def is_half_second():
    t = pygame.time.get_ticks()/1000.0
    return round(t - int(t)) == 0


def load_image(filename):
    return pygame.image.load(os.path.join(RESOURCES_DIR, filename))


def get_map_filename(filename):
    return os.path.join(RESOURCES_DIR, "maps", filename)


class Hero(pygame.sprite.Sprite):
    def __init__(self, tmx_data, cells, game):
        pygame.sprite.Sprite.__init__(self)
        self.velocity = [0.0, 0.0]
        self.position = [153.0, 187.0]
        self.old_position = self.position
        self.tmx_data = tmx_data
        self.cells = cells
        self.game = game

        side_stand = load_image('../gextract/tiles16/000000030.png').convert_alpha()
        side_walk = load_image('../gextract/tiles16/000000031.png').convert_alpha()
        self.images = {
            'e': {
                'stand': side_stand,
                'walk': side_walk,
            },
            'n': {
                'stand': load_image('../gextract/tiles16/000000028.png').convert_alpha(),
                'walk': load_image('../gextract/tiles16/000000029.png').convert_alpha(),
            },
            's': {
                'stand': load_image('../gextract/tiles16/000000026.png').convert_alpha(),
                'walk': load_image('../gextract/tiles16/000000027.png').convert_alpha(),
            },
            'w': {
                'stand': pygame.transform.flip(side_stand, True, False),
                'walk': pygame.transform.flip(side_walk, True, False),
            },
        }
        self.direction = 's'
        self.image = self.images[self.direction]['stand']
        self.walking = True

        self.rect = self.image.get_rect()
        self.rect.topleft = [floor(TILE_SIZE*self.position[0]), floor(TILE_SIZE*self.position[1])]

    def update(self, dt):
        self.update_position(dt)
        self.update_image()

    def update_image(self):
        stand_walk = 'stand' if is_half_second() else 'walk'
        self.image = self.images[self.direction][stand_walk]

    def move(self, direction):
        if self.velocity != [0, 0]:
            return
        if direction is None:
            self.velocity = [0,0]
            return
        self.direction = direction
        if direction == 'n' and not self.is_a_wall([0, -1]):
            self.velocity = [0, -HERO_MOVE_SPEED]
        elif direction == 's' and not self.is_a_wall([0, 1]):
            self.velocity = [0, HERO_MOVE_SPEED]
        elif direction == 'w' and not self.is_a_wall([-1, 0]):
            self.velocity = [-HERO_MOVE_SPEED, 0]
        elif direction == 'e' and not self.is_a_wall([1, 0]):
            self.velocity = [HERO_MOVE_SPEED, 0]
        else:
            self.velocity = [0, 0]

    def update_position(self, dt):
        self.old_position = self.position[:]

        self.position[0] += self.velocity[0] * dt
        if self.velocity[0] > 0 and floor(self.position[0]) != floor(self.old_position[0]):
            self.position[0] = floor(self.position[0])
            self.velocity[0] = 0
            self.handle_cell()
        elif self.velocity[0] < 0 and ceil(self.position[0]) != ceil(self.old_position[0]):
            self.position[0] = ceil(self.position[0])
            self.velocity[0] = 0
            self.handle_cell()

        self.position[1] += self.velocity[1] * dt
        if self.velocity[1] > 0 and floor(self.position[1]) != floor(self.old_position[1]):
            self.position[1] = floor(self.position[1])
            self.velocity[1] = 0
            self.handle_cell()
        elif self.velocity[1] < 0 and ceil(self.position[1]) != ceil(self.old_position[1]):
            self.position[1] = ceil(self.position[1])
            self.velocity[1] = 0
            self.handle_cell()

        self.rect.topleft = [floor(TILE_SIZE*self.position[0]), floor(TILE_SIZE*self.position[1])]

    def handle_cell(self):
        props = self.cells.get(tuple(self.position))
        if not props:
            return
        teleport = props.get('teleport')
        if teleport:
            new_map = teleport.get('map')
            new_direction = teleport.get('direction', self.direction)
            if new_map:
                self.game.set_current_map(new_map, [teleport['x'], teleport['y']], new_direction)
            else:
                self.position = [teleport['x'], teleport['y']]
                self.direction = new_direction

    def is_a_wall(self, offset):
        x = self.position[0] + offset[0]
        y = self.position[1] + offset[1]
        if x < 0 or y < 0 or x >= self.tmx_data.width or y >= self.tmx_data.height:
            return True
        props = self.tmx_data.get_tile_properties(x, y, 0) or {}
        return props.get('wall') == 'true'


class Map(object):
    def __init__(self, screen, map_name, game):
        self.game = game
        map_filename = get_map_filename('{}.tmx'.format(map_name))
        json_filename = get_map_filename('{}.json'.format(map_name))
        self.screen = screen
        self.tmx_data = load_pygame(map_filename)
        with open(json_filename) as f:
            json_data = json.loads(f.read())
        self.cells = {(cell['x'], cell['y']): cell for cell in json_data}
        map_data = pyscroll.data.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(map_data, self.screen.get_size())
        self.map_layer.zoom = 1
        self.group = PyscrollGroup(map_layer=self.map_layer)
        self.hero = Hero(self.tmx_data, self.cells, self.game)
        self.group.add(self.hero)

    def draw(self):
        self.group.center(self.hero.rect.center)
        self.group.draw(self.screen)

    def update(self, dt):
        self.group.update(dt)

    def move_hero(self, direction):
        self.hero.move(direction)
        # when I add followers, they would move here too


class TitlePage(object):
    def __init__(self, screen):
        self.screen = screen
        self.title_image = load_image('../data/images/title.png').convert_alpha()

    def draw(self):
        self.screen.fill((0,0,0))
        self.screen.blit(self.title_image, ((GAME_WIDTH - self.title_image.get_width())/2, 16))

    def update(self, dt):
        pass


class Game(object):
    def __init__(self, screen):
        self.real_screen = screen
        self.virtual_width = GAME_WIDTH
        self.virtual_height = GAME_HEIGHT
        self.virtual_screen = pygame.Surface((self.virtual_width, self.virtual_height))
        self.clock = pygame.time.Clock()
        self.fps = 1000
        self.screen_state = "title"
        self.maps = {name: Map(self.virtual_screen, name, self) for name in MAP_NAMES}
        self.current_map = self.maps['overworld']
        pygame.key.set_repeat(10, 10)
        pygame.event.set_blocked(MOUSEMOTION)
        pygame.event.set_blocked(ACTIVEEVENT)
        pygame.event.set_blocked(VIDEORESIZE)
        pygame.event.set_blocked(KEYUP)
        self.title_page = TitlePage(self.virtual_screen)
        self.fitted_screen = None # gets initialized in resize_window()
        self.window_size = screen.get_size()
        self.resize_window(self.window_size)

    def set_current_map(self, map_name, position, direction):
        self.current_map = self.maps[map_name]
        self.current_map.hero.position = position
        self.current_map.hero.direction = direction

    def resize_window(self, size):
        self.real_screen = pygame.display.set_mode(size)
        (width, height) = size
        width_multiplier = width*1.0 / self.virtual_width
        height_multiplier = height*1.0 / self.virtual_height
        multiplier = min(width_multiplier, height_multiplier)
        fitted_width = int(self.virtual_width*multiplier)
        fitted_height = int(self.virtual_height*multiplier)
        fitted_x_pos = (width - fitted_width) / 2
        fitted_y_pos = (height - fitted_height) / 2
        self.fitted_screen = self.real_screen.subsurface(
            (fitted_x_pos, fitted_y_pos, fitted_width, fitted_height)
        )

    def scale(self):
        self.real_screen.fill((0,0,0))
        pygame.transform.scale(self.virtual_screen, self.fitted_screen.get_size(), self.fitted_screen)

    def draw(self):
        if self.screen_state == 'game':
            self.current_map.draw()
        elif self.screen_state == 'title':
            self.title_page.draw()
        self.scale()

    def update(self, dt):
        if self.screen_state == 'game':
            self.current_map.update(dt)
        elif self.screen_state == 'title':
            self.title_page.update(dt)

    def is_a_wall(self, offset):
        x = self.hero.position[0] + offset[0]
        y = self.hero.position[1] + offset[1]
        if x < 0 or y < 0 or x >= self.tmx_data.width or y >= self.tmx_data.height:
            return True
        props = self.tmx_data.get_tile_properties(x, y, 0)
        return props['wall'] == 'true'

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
                pygame.quit()
                break

            elif event.type == KEYDOWN:
                pressed = pygame.key.get_pressed()

                if self.screen_state == "game":
                    if pressed[K_UP]:
                        self.current_map.move_hero('n')
                    elif pressed[K_DOWN]:
                        self.current_map.move_hero('s')
                    elif pressed[K_RIGHT]:
                        self.current_map.move_hero('e')
                    elif pressed[K_LEFT]:
                        self.current_map.move_hero('w')
                    else:
                        self.current_map.move_hero(None)

                    if pressed[K_ESCAPE]:
                        self.running = False
                        pygame.quit()
                        print(" ")
                        time.sleep(0.5)
                        print("Shutdown... Complete")
                        sys.exit()
                        break

                elif self.screen_state == 'title':
                    if pressed[K_RETURN]:
                        self.screen_state = 'game'

    def get_new_window_size_and_fit_screen(self):
        p = subprocess.Popen(['xwininfo', '-name', 'pygame window'], stdout=subprocess.PIPE)
        (win_info, _) = p.communicate()
        for line in win_info.split('\n'):
            data = line.split()
            if len(data) != 2:
                continue
            if data[0] == 'Width:':
                new_width = int(data[1])
            elif data[0] == 'Height:':
                new_height = int(data[1])
        if self.window_size[0] != new_width or self.window_size[1] != new_height:
            self.resize_window((new_width, new_height))


    def run(self):
        self.running = True
        try:
            while self.running:
                dt = self.clock.tick(self.fps)/1000.0
                self.handle_input()
                self.update(dt)
                self.draw()
                pygame.display.flip()
        except KeyboardInterrupt:
            self.running = False
            pygame.quit()


if __name__ == '__main__':
    screen = pygame.display.set_mode((1600, 900))
    try:
        game = Game(screen)
        game.run()
    except:
        pygame.quit()
        raise
