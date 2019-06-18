# -*- coding: UTF-8 -*-

import os

from constants import GAME_WIDTH
from helpers import load_image
from text import create_prompt


class BattleIntro(object):
    def __init__(self, screen, warlord, text):
        self.screen = screen
        self.portrait = load_image(os.path.join('portraits', '{}.png'.format(warlord)))
        self.dialog = create_prompt(text)

    def draw(self):
        self.screen.blit(self.dialog.surface, (0, 144))
        self.screen.blit(self.portrait, (GAME_WIDTH-64, 160))

    def update(self, dt):
        self.dialog.update(dt)

    def handle_input(self, pressed):
        self.dialog.handle_input(pressed)
