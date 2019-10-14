# -*- coding: UTF-8 -*-

import os

import pygame
from pygame.locals import *

from text import MenuBox


class HelpMenu(object):
    def __init__(self, game):
        self.game = game
        self.make_menu(0)
        self.select_sound = pygame.mixer.Sound(os.path.join('data', 'audio', 'select.wav'))
        self.state = 'main'
        
    def make_menu(self, current_choice):
        items = [
            'WEAPONS',
            'BODY ARMOR',
            'HELMETS',
            'TACTICS',
            'ITEMS',
        ]
        self.menu = MenuBox(items, current_choice=current_choice)
        self.menu.focus()

    def get_surface(self):
        return self.menu.surface

    def update(self, dt):
        self.menu.update(dt)

    def handle_input(self, pressed):
        self.menu.handle_input(pressed)
        if pressed[K_x]:
            self.select_sound.play()
            choice = self.menu.get_choice()