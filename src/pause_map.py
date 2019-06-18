# -*- coding: UTF-8 -*-

import pygame
from pygame.locals import *
import pyscroll
from pytmx.util_pygame import load_pygame

from helpers import get_map_filename

class PauseMap(object):
    def __init__(self, screen, game, position):
        self.screen = screen
        self.game = game
        map_filename = get_map_filename('overworld_map.tmx')
        self.tmx_data = load_pygame(map_filename)
        map_data = pyscroll.data.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(map_data, self.screen.get_size())
        self.map_layer.zoom = 1
        self.group = pyscroll.group.PyscrollGroup(map_layer=self.map_layer)
        self.position = position # must be a tuple of two integers (x,y). this is world coordinates.

    def get_group_center(self):
        return [int((coord+0.5)*16) for coord in self.position]

    def draw(self):
        self.group.center(self.get_group_center())
        self.group.draw(self.screen)

    def update(self, dt):
        pass

    def handle_input(self, pressed):
        pass
