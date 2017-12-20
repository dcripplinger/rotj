# -*- coding: UTF-8 -*-

from math import floor

import pygame

from constants import TILE_SIZE
from helpers import load_image


class Treasure(pygame.sprite.Sprite):
    def __init__(self, opened=False, invisible=False, position=None):
        super(Treasure, self).__init__()
        self.position = position
        if not invisible:
            self.image = load_image('opened_treasure.png' if opened else 'closed_treasure.png')
        else:
            self.image = load_image('invisible_treasure.png')
        self.invisible = invisible
        self.rect = self.image.get_rect()
        self.rect.topleft = [floor(TILE_SIZE*self.position[0]), floor(TILE_SIZE*self.position[1])]

    def open(self):
        if not self.invisible:
            self.image = load_image('opened_treasure.png')
