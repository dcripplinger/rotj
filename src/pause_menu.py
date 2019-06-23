# -*- coding: UTF-8 -*-

import os

import pygame
from pygame.locals import *

from constants import BLACK, GAME_WIDTH
from devtools import Devtools
from text import MenuBox, TextBox


class PauseMenu(object):
    def __init__(self, screen, game):
        self.select_sound = pygame.mixer.Sound(os.path.join('data', 'audio', 'select.wav'))
        self.screen = screen
        self.game = game
        self.title = TextBox('PAUSE MENU', GAME_WIDTH, 16, adjust='center')
        menu_items = []
        menu_items.append('MAP')
        if self.game.args.devtools:
            menu_items.append('DEV TOOLS')
        menu_items.append('BACK')
        self.menu = MenuBox(menu_items, border=False)
        self.menu.focus()
        self.screen_state = 'menu'
        self.devtools_menu = None

    def draw(self):
        self.screen.fill(BLACK)
        self.screen.blit(self.title.surface, (0, 8))
        self.screen.blit(self.menu.surface, (32, 24))
        if self.screen_state == 'devtools':
            self.screen.blit(self.devtools_menu.get_surface(), (32, 56))

    def update(self, dt):
        if self.screen_state == 'menu':
            self.menu.update(dt)
        elif self.screen_state == 'devtools':
            self.devtools_menu.update(dt)

    def handle_input(self, pressed):
        if self.screen_state == 'menu':
            self.handle_input_menu(pressed)
        elif self.screen_state == 'devtools':
            self.handle_input_devtools(pressed)

    def handle_input_menu(self, pressed):
        self.menu.handle_input(pressed)
        if pressed[K_RETURN] or pressed[K_z]:
            self.game.close_pause_menu()
        elif pressed[K_x]:
            self.select_sound.play()
            choice = self.menu.get_choice()
            if choice == 'MAP':
                self.game.open_pause_map()
            elif choice == 'DEV TOOLS':
                self.screen_state = 'devtools'
                self.devtools_menu = Devtools(self.game)
                self.menu.unfocus()
            elif choice == 'BACK':
                self.game.close_pause_menu()

    def handle_input_devtools(self, pressed):
        self.devtools_menu.handle_input(pressed)
        if pressed[K_RETURN]:
            self.game.close_pause_menu()
        elif pressed[K_z]:
            self.screen_state = 'menu'
            self.devtools_menu = None
            self.menu.focus()
