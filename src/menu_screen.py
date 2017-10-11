# -*- coding: UTF-8 -*-

import time

import pygame
from pygame.locals import *

from constants import GAME_WIDTH, BLACK
from helpers import load_save_states
from text import MenuBox, TextBox


MAIN_MENU = [
    'GAME START',
    'REGISTER HISTORY BOOK',
    'ERASE HISTORY BOOK',
    'COPY HISTORY BOOK',
]


class MenuScreen(object):
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.select_sound = pygame.mixer.Sound('data/audio/select.wav')
        self.screen_state = 'unstarted'
        self.state = load_save_states()
        self.start_prompt = None
        self.start_menu = None
        self.main_menu = None
        self.speed_menu = None
        self.register_prompt = None
        self.register_menu = None
        self.erase_menu = None
        self.erase_prompt = None
        self.confirm_erase_menu = None

    def load_main_menu(self):
        if all(self.state): # if all three save slots are full
            self.main_menu = MenuBox([MAIN_MENU[0], MAIN_MENU[2]])
        elif any(self.state): # if any of the three save slots is populated
            self.main_menu = MenuBox(MAIN_MENU)
        else:
            self.main_menu = MenuBox([MAIN_MENU[1],])

    def load_start_menu(self):
        self.start_menu = MenuBox(self.format_populated_save_slots())
        self.start_prompt = self.create_prompt('Which history do you wish to continue?')

    def load_register_menu(self):
        self.register_menu = MenuBox(self.format_unpopulated_save_slots())
        self.register_prompt = self.create_prompt('Which history book do you wish to begin?')

    def create_prompt(self, text):
        return TextBox(text, width=160, height=80, border=True, double_space=True, appear='scroll')

    def load_speed_menu(self):
        self.speed_menu = MenuBox(['FAST', 'FAST', 'STILL FAST'])

    def format_populated_save_slots(self):
        return ['{}~{:~<8}~L{:02}'.format(i+1, slot['name'], slot['level']) for i, slot in enumerate(self.state) if slot]

    def format_unpopulated_save_slots(self):
        return ['{}~~~~~~'.format(i+1) for i, slot in enumerate(self.state) if not slot]

    def load_erase_menu(self):
        self.erase_menu = MenuBox(self.format_populated_save_slots())
        self.erase_prompt = self.create_prompt('Which history book do you wish to erase?')

    def load_confirm_erase_menu(self):
        self.confirm_erase_menu = MenuBox(['Yes', 'No'])
        self.erase_prompt = self.create_prompt('Are you sure?')

    def draw(self):
        self.screen.fill(BLACK)
        prompt_vert_pos = 160
        mid_menu_vert_pos = 80
        top_menu_vert_pos = 16
        if self.screen_state == 'main':
            self.screen.blit(self.main_menu.surface, ((GAME_WIDTH - self.main_menu.get_width())/2, top_menu_vert_pos))
        elif self.screen_state == 'start':
            self.screen.blit(self.start_prompt.surface, ((GAME_WIDTH - self.start_prompt.width)/2, prompt_vert_pos))
            self.screen.blit(self.start_menu.surface, ((GAME_WIDTH - self.start_menu.get_width())/2, top_menu_vert_pos))
        elif self.screen_state == 'speed':
            self.screen.blit(self.start_prompt.surface, ((GAME_WIDTH - self.start_prompt.width)/2, prompt_vert_pos))
            self.screen.blit(self.start_menu.surface, ((GAME_WIDTH - self.start_menu.get_width())/2, top_menu_vert_pos))
            self.screen.blit(self.speed_menu.surface, (GAME_WIDTH - self.speed_menu.get_width(), mid_menu_vert_pos))
        elif self.screen_state == 'register':
            self.screen.blit(self.register_prompt.surface, ((GAME_WIDTH - self.register_prompt.width)/2, prompt_vert_pos))
            self.screen.blit(self.register_menu.surface, ((GAME_WIDTH - self.register_menu.get_width())/2, top_menu_vert_pos))
        elif self.screen_state == 'erase':
            self.screen.blit(self.erase_prompt.surface, ((GAME_WIDTH - self.erase_prompt.width)/2, prompt_vert_pos))
            self.screen.blit(self.erase_menu.surface, ((GAME_WIDTH - self.erase_menu.get_width())/2, top_menu_vert_pos))
        elif self.screen_state == 'confirm_erase':
            self.screen.blit(self.erase_prompt.surface, ((GAME_WIDTH - self.erase_prompt.width)/2, prompt_vert_pos))
            self.screen.blit(self.erase_menu.surface, ((GAME_WIDTH - self.erase_menu.get_width())/2, top_menu_vert_pos))
            self.screen.blit(
                self.confirm_erase_menu.surface,
                ((GAME_WIDTH - self.confirm_erase_menu.get_width())/2, mid_menu_vert_pos),
            )

    def update(self, dt):
        if self.screen_state == 'unstarted':
            pygame.mixer.music.load('data/audio/music/menu.wav')
            pygame.mixer.music.play(-1)
            self.screen_state = 'main'
            self.load_main_menu()
            self.main_menu.focus()
        elif self.screen_state == 'main':
            self.main_menu.update(dt)
        elif self.screen_state == 'start':
            self.start_menu.update(dt)
            self.start_prompt.update(dt)
        elif self.screen_state == 'speed':
            self.speed_menu.update(dt)
        elif self.screen_state == 'register':
            self.register_menu.update(dt)
            self.register_prompt.update(dt)
        elif self.screen_state == 'erase':
            self.erase_menu.update(dt)
            self.erase_prompt.update(dt)
        elif self.screen_state == 'confirm_erase':
            self.confirm_erase_menu.update(dt)
            self.erase_prompt.update(dt)

    def handle_input(self, pressed):
        if pressed[K_x]:
            self.select_sound.play()
        if self.screen_state == 'main':
            self.main_menu.handle_input(pressed)
            if pressed[K_x]:
                if self.main_menu.get_choice() == MAIN_MENU[0]:
                    self.screen_state = 'start'
                    self.load_start_menu()
                    self.start_menu.focus()
                elif self.main_menu.get_choice() == MAIN_MENU[1]:
                    self.screen_state = 'register'
                    self.load_register_menu()
                    self.register_menu.focus()
                elif self.main_menu.get_choice() == MAIN_MENU[2]:
                    self.screen_state = 'erase'
                    self.load_erase_menu()
                    self.erase_menu.focus()
                self.main_menu = None
        elif self.screen_state == 'start':
            self.start_menu.handle_input(pressed)
            if pressed[K_x]:
                self.screen_state = 'speed'
                self.load_speed_menu()
                self.speed_menu.focus()
                self.start_menu.unfocus()
            elif pressed[K_z]:
                self.screen_state = 'main'
                self.load_main_menu()
                self.start_menu = None
                self.start_prompt = None
                self.main_menu.focus()
        elif self.screen_state == 'speed':
            self.speed_menu.handle_input(pressed)
            if pressed[K_x]:
                pygame.mixer.music.stop()
                time.sleep(.5)
                self.game.set_screen_state('game')
            elif pressed[K_z]:
                self.screen_state = 'start'
                self.start_menu.focus()
                self.speed_menu = None
        elif self.screen_state == 'register':
            self.register_menu.handle_input(pressed)
            if pressed[K_z]:
                self.screen_state = 'main'
                self.load_main_menu()
                self.register_menu = None
                self.register_prompt = None
                self.main_menu.focus()
        elif self.screen_state == 'erase':
            self.erase_menu.handle_input(pressed)
            if pressed[K_x]:
                self.screen_state = 'confirm_erase'
                self.load_confirm_erase_menu()
                self.confirm_erase_menu.focus()
                self.erase_menu.unfocus()
            elif pressed[K_z]:
                self.screen_state = 'main'
                self.load_main_menu()
                self.erase_menu = None
                self.erase_prompt = None
                self.main_menu.focus()
        elif self.screen_state == 'confirm_erase':
            self.confirm_erase_menu.handle_input(pressed)
            if pressed[K_z]:
                self.screen_state = 'erase'
                self.load_erase_menu()
                self.confirm_erase_menu = None
                self.erase_menu.focus()
