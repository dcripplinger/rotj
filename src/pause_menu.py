# -*- coding: UTF-8 -*-

import os

import pygame
from pygame.locals import *

from constants import BLACK, GAME_WIDTH
from devtools import Devtools
from help_menu import HelpMenu
from text import MenuBox, TextBox, create_prompt


class PauseMenu(object):
    def __init__(self, screen, game):
        self.select_sound = pygame.mixer.Sound(os.path.join('data', 'audio', 'select.wav'))
        self.screen = screen
        self.game = game
        self.title = TextBox('PAUSE MENU', GAME_WIDTH, 16, adjust='center')
        menu_items = []
        menu_items.append('MAP')
        menu_items.append('HELP')
        if self.game.args.devtools:
            menu_items.append('DEV TOOLS')
        menu_items.append('QUIT TO TITLE SCREEN')
        menu_items.append('BACK')
        self.menu = MenuBox(menu_items, border=False)
        self.menu.focus()
        self.screen_state = 'menu'
        self.help_menu = None
        self.devtools_menu = None
        self.choice_box = None
        self.prompt = None

    def draw(self):
        if self.screen_state == 'help':
            self.help_menu.draw()
        else:
            self.screen.fill(BLACK)
            self.screen.blit(self.title.surface, (0, 8))
            self.screen.blit(self.menu.surface, (32, 24))
            if self.screen_state == 'devtools':
                self.screen.blit(self.devtools_menu.get_surface(), (32, 72))
            elif self.screen_state in ['quit', 'quit_choice']:
                if self.choice_box:
                    self.screen.blit(self.choice_box.surface, (160, 128))
                if self.prompt:
                    self.screen.blit(self.prompt.surface, (0, 160))

    def update(self, dt):
        if self.screen_state == 'menu':
            self.menu.update(dt)
        elif self.screen_state == 'devtools':
            self.devtools_menu.update(dt)
        elif self.screen_state == 'help':
            self.help_menu.update(dt)
        elif self.screen_state == 'quit':
            self.prompt.update(dt)
            if not self.prompt.has_more_stuff_to_show():
                self.screen_state = 'quit_choice'
                self.choice_box = MenuBox(['NO', 'YES'])
                self.choice_box.focus()
                self.prompt.shutdown()
        elif self.screen_state == 'quit_choice':
            self.choice_box.update(dt)

    def handle_input(self, pressed):
        if pressed[K_RETURN]:
            self.game.close_pause_menu()
        elif self.screen_state == 'menu':
            self.handle_input_menu(pressed)
        elif self.screen_state == 'devtools':
            self.handle_input_devtools(pressed)
        elif self.screen_state == 'help':
            self.handle_input_help_menu(pressed)
        elif self.screen_state == 'quit':
            self.prompt.handle_input(pressed)
        elif self.screen_state == 'quit_choice':
            self.handle_input_quit_choice(pressed)

    def handle_input_quit_choice(self, pressed):
        self.choice_box.handle_input(pressed)
        if pressed[K_z]:
            self.prompt = None
            self.choice_box = None
            self.screen_state = 'menu'
        elif pressed[K_x]:
            self.select_sound.play()
            choice = self.choice_box.get_choice()
            if choice == 'NO':
                self.prompt = None
                self.choice_box = None
                self.screen_state = 'menu'
            else: # choice == 'YES'
                self.game.set_screen_state('title')

    def handle_input_menu(self, pressed):
        self.menu.handle_input(pressed)
        if pressed[K_RETURN] or pressed[K_z]:
            self.game.close_pause_menu()
        elif pressed[K_x]:
            self.select_sound.play()
            choice = self.menu.get_choice()
            if choice == 'MAP':
                self.game.open_pause_map()
            elif choice == 'HELP':
                self.screen_state = 'help'
                self.help_menu = HelpMenu(self.screen, self.game)
                self.menu.unfocus()
            elif choice == 'DEV TOOLS':
                self.screen_state = 'devtools'
                self.devtools_menu = Devtools(self.game)
                self.menu.unfocus()
            elif choice == 'QUIT TO TITLE SCREEN':
                self.screen_state = 'quit'
                self.prompt = create_prompt('Are you sure you want to quit? Any unsaved gameplay will be lost.')
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

    def handle_input_help_menu(self, pressed):
        if pressed[K_RETURN]:
            self.game.close_pause_menu()
        elif pressed[K_z] and self.help_menu.state == 'main':
            self.screen_state = 'menu'
            self.help_menu = None
            self.menu.focus()
        self.help_menu.handle_input(pressed)
