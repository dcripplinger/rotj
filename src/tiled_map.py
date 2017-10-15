# -*- coding: UTF-8 -*-

import json

from pygame.locals import *
import pyscroll
from pytmx.util_pygame import load_pygame

from helpers import get_map_filename
from hero import Hero


class Map(object):
    def __init__(self, screen, map_name, game):
        self.name = map_name
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
        self.group = pyscroll.group.PyscrollGroup(map_layer=self.map_layer)
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

    def handle_input(self, pressed):
        if pressed[K_UP]:
            self.move_hero('n')
        elif pressed[K_DOWN]:
            self.move_hero('s')
        elif pressed[K_RIGHT]:
            self.move_hero('e')
        elif pressed[K_LEFT]:
            self.move_hero('w')
        else:
            self.move_hero(None)
