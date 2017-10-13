# -*- coding: UTF-8 -*-

import pyscroll
from pytmx.util_pygame import load_pygame

from helpers import get_map_filename
from sprite import Sprite


class Beginning(object):
    def __init__(self, game, screen):
        self.game = game
        map_filename = get_map_filename('beginning.tmx')
        self.screen = screen
        self.tmx_data = load_pygame(map_filename)
        map_data = pyscroll.data.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(map_data, self.screen.get_size())
        self.map_layer.zoom = 1
        self.group = pyscroll.group.PyscrollGroup(map_layer=self.map_layer)
        mid = tmx_data.width/2
        self.moroni = Sprite(self.tmx_data, self.game, 'moroni', velocity=[0,-10], direction='s', position=[mid,0])
        self.group.add(self.moroni)
        self.teancum = Sprite(self.tmx_data, self.game, 'teancum', velocity=[10,0], direction='e', position=[mid,0])
        self.group.add(self.teancum)
        self.amalickiah = Sprite(self.tmx_data, self.game, 'amalickiah', velocity=[-10,0], direction='w', position=[mid,mid*2])
        self.group.add(self.amalickiah)

    def draw(self):
        self.group.draw(self.screen)

    def update(self, dt):
        self.group.update(dt)

    def handle_input(self, pressed):
        pass
