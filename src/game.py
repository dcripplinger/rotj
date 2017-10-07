import subprocess
import sys
import time

import pygame
from pygame.locals import *

from constants import GAME_HEIGHT, GAME_WIDTH
from tiled_map import Map
from title_page import TitlePage

MAP_NAMES = [
    'overworld',
    'tunnels_of_the_north',
    'cave_of_gadianton',
    'sierra_pass',
    'cavity_of_a_rock',
    'passage_to_gid',
]


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
        self.title_page = TitlePage(self.virtual_screen, self)
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
                return
        pressed = pygame.key.get_pressed()
        if pressed[K_ESCAPE]:
            self.running = False
            pygame.quit()
            print(" ")
            time.sleep(0.5)
            print("Shutdown... Complete")
            sys.exit()
            return
        if self.screen_state == "game":
            self.current_map.handle_input(pressed)
        elif self.screen_state == 'title':
            self.title_page.handle_input(pressed)

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
