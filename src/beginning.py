# -*- coding: UTF-8 -*-

from pygame.locals import *
import pyscroll
from pytmx.util_pygame import load_pygame

from constants import BLACK
from helpers import get_map_filename, load_image
from sprite import Sprite
from text import create_prompt


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
        mid = self.tmx_data.width/2
        speed = 1.5
        self.moroni = Sprite(self.tmx_data, self.game, 'moroni', [mid,1], speed=speed, direction='s', walking=True)
        self.group.add(self.moroni)
        self.teancum = Sprite(self.tmx_data, self.game, 'teancum', [1,mid], speed=speed, direction='e', walking=True)
        self.group.add(self.teancum)
        self.amalickiah = Sprite(self.tmx_data, self.game, 'amalickiah', [mid*2-1,mid], speed=speed, direction='w', walking=True)
        self.group.add(self.amalickiah)
        self.paces_left = 6
        self.pledge_image = load_image('pledge.png')
        self.prompt = create_prompt('Testing, testing, 1, 2, 3...')

    def draw(self):
        if self.paces_left > 0:
            self.group.draw(self.screen)
        else:
            self.screen.fill(BLACK)
            self.screen.blit(self.pledge_image, (0,0))
            self.screen.blit(self.prompt.surface, ((GAME_WIDTH - self.prompt.get_width())/2, 160))

    def update(self, dt):
        if self.paces_left > 0:
            moved = False
            for sprite in [self.moroni, self.teancum, self.amalickiah]:
                m = sprite.move(sprite.direction)
                if sprite == self.moroni:
                    moved = m
            if moved:
                self.paces_left -= 1
            self.group.update(dt)
        else:
            self.prompt.update(dt)

    def handle_input(self, pressed):
        if self.paces_left == 0:
            if pressed[K_x]:
                self.game.screen_state = 'game'
                self.prompt.shutdown()
