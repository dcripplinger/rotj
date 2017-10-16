# -*- coding: UTF-8 -*-

from math import ceil, floor

import pygame

from constants import TILE_SIZE
from helpers import is_half_second
from sprite import Sprite


class Hero(Sprite):
    def __init__(self, tmx_data, game, character, position, speed=10, direction='s', walking=False, cells=None):
        super(Hero, self).__init__(tmx_data, game, character, position, speed, direction, walking)
        self.cells = cells

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
