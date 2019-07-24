# -*- coding: UTF-8 -*-

import pygame
from pygame.locals import *
import pyscroll
from pytmx.util_pygame import load_pygame

from helpers import (
    get_map_filename
)
from sprite import Sprite

class Cutscene(object):
    def __init__(self, game, screen, scene):
        self.game = game
        self.screen = screen
        self.scene = scene
        map_filename = get_map_filename(
            'overworld_map.tmx' if scene == 0 else 'house_of_moroni.tmx' if scene == 1 else '_palace.tmx'
        )
        self.tmx_data = load_pygame(map_filename)
        map_data = pyscroll.data.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(map_data, self.screen.get_size())
        self.map_layer.zoom = 1
        self.group = pyscroll.group.PyscrollGroup(map_layer=self.map_layer)
        if scene == 1:
            self.sprite = Sprite(self.tmx_data, self.game, 'moroni', (15, 18), direction='n')
            self.group.add(self.sprite)
        elif scene == 2:
            self.sprite = Sprite(self.tmx_data, self.game, 'pahoran', (17, 14), direction='s')
            self.group.add(self.sprite)
        else:
            self.sprite = None

    def get_group_center(self):
        if self.scene == 0:
            return (160, 160)
        if self.scene == 1:
            return (240, 240)
        return (272, 256) # scene 2

    def draw(self):
        self.group.center(self.get_group_center())
        self.group.draw(self.screen)

    def update(self, dt):
        pass

    def handle_input(self, pressed):
        if pressed[K_x]:
            self.game.set_screen_state('fade_cutscene')