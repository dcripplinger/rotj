# -*- coding: UTF-8 -*-

from math import floor
import os

import pygame

from constants import TILE_SIZE
from helpers import load_image


class ShopMat(pygame.sprite.Sprite):
    def __init__(self, typ=None, position=None):
        super(ShopMat, self).__init__()
        self.name = 'mat'
        self.image = load_image(os.path.join('shop_mats', '{}.png'.format(typ)))
        self.rect = self.image.get_rect()
        self.rect.topleft = [floor(TILE_SIZE*position[0]), floor(TILE_SIZE*position[1])]
