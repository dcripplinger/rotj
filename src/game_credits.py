# -*- coding: UTF-8 -*-

import codecs
import os

import pygame
from pygame.locals import *

from constants import BLACK, GAME_WIDTH, GAME_HEIGHT
from text import TextBox


class Credits(object):
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        with codecs.open(os.path.join('data', 'credits.txt'), encoding='utf-8') as f:
            raw_text = f.read()
        self.text = TextBox(raw_text, width=GAME_WIDTH, adjust='center', double_space=True)
        self.position = GAME_HEIGHT

    def draw(self):
        self.screen.fill(BLACK)
        self.screen.blit(self.text.surface, (0, int(self.position)))

    def update(self, dt):
        self.position -= dt*16
        if self.position < -68*16 - GAME_HEIGHT:
            self.game.set_screen_state('title')

    def handle_input(self, pressed):
        pass
