# -*- coding: UTF-8 -*-

import os

import pygame
from pygame.locals import *

from constants import BLACK, GAME_WIDTH, GAME_HEIGHT
from text import MenuBox


class HelpMenu(object):
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.select_sound = pygame.mixer.Sound(os.path.join('data', 'audio', 'select.wav'))
        self.state = 'main'
        items = [
            'WEAPONS',
            'BODY ARMOR',
            'HELMETS',
            'TACTICS',
            'ITEMS',
        ]
        self.menu = MenuBox(items, current_choice=0, border=True, title='Help')
        self.menu.focus()

    def draw(self):
        self.screen.fill(BLACK)
        self.screen.blit(self.menu.surface, (0, 0))

    def update(self, dt):
        self.menu.update(dt)

    def handle_input(self, pressed):
        self.menu.handle_input(pressed)
        if pressed[K_x]:
            self.select_sound.play()
            choice = self.menu.get_choice()