# -*- coding: UTF-8 -*-

import pygame
from pygame.locals import *
import pyscroll
from pytmx.util_pygame import load_pygame

from constants import TILE_SIZE
from helpers import get_map_filename

XMIN = 7.5
XMAX = 291.5
YMIN = 7
YMAX = 392
SPEED = 50 # tiles per second when moving
MAP_WIDTH = 300
MAP_HEIGHT = 400

class PauseMap(object):
    def __init__(self, screen, game, position):
        self.screen = screen
        self.game = game
        self.set_visible_tiles()
        map_filename = get_map_filename('overworld_map.tmx')
        self.tmx_data = load_pygame(map_filename)
        map_data = pyscroll.data.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(map_data, self.screen.get_size())
        self.map_layer.zoom = 1
        self.group = pyscroll.group.PyscrollGroup(map_layer=self.map_layer)
        self.bound_position(position)
        self.direction = [0, 0]

    def set_visible_tiles(self):
        self.visible_tiles = [[False] * MAP_HEIGHT for i in range(MAP_WIDTH)]
        for tile in self.game.game_state['beaten_path'].keys():
            X, Y = [int(i) for i in tile.split()]
            for x in range(X-8, X+9):
                if x < 0 or x >= MAP_WIDTH:
                    continue
                for y in range(Y-7, Y+8):
                    if y < 0 or y >= MAP_HEIGHT:
                        continue
                    self.visible_tiles[x][y] = True

    def bound_position(self, position):
        self.position = [min(XMAX, max(XMIN, position[0])), min(YMAX, max(YMIN, position[1]))]

    def get_group_center(self):
        return [int((coord + 0.5) * TILE_SIZE) for coord in self.position]

    def draw(self):
        self.group.center(self.get_group_center())
        self.group.draw(self.screen)

    def update(self, dt):
        self.position[0] += self.direction[0] * SPEED * dt
        self.position[1] += self.direction[1] * SPEED * dt
        self.bound_position(self.position)
        self.direction = [0, 0] # Keep the map from moving forever

    def handle_input(self, pressed):
        if pressed[K_UP]:
            self.direction = [0, -1]
        elif pressed[K_DOWN]:
            self.direction = [0, 1]
        elif pressed[K_LEFT]:
            self.direction = [-1, 0]
        elif pressed[K_RIGHT]:
            self.direction = [1, 0]
        else:
            self.direction = [0, 0]

        if pressed[K_z]:
            self.game.close_pause_map()
        elif pressed[K_RETURN]:
            self.game.close_pause_menu()
