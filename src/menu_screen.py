# -*- coding: UTF-8 -*-

import time

import pygame
from pygame.locals import *

from constants import GAME_WIDTH, BLACK
from helpers import create_save_state, erase_save_state, is_half_second, load_save_states, copy_save_state
from text import create_prompt, MenuBox, MenuGrid, TextBox


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
        self.name_menu = None
        self.name_blurb = None
        self.name_field = None
        self.name_underline = None
        self.current_name_char = None
        self.copy_prompt = None
        self.copy_menu = None
        self.paste_menu = None
        self.paste_prompt = None

    def load_main_menu(self):
        if all(self.state): # if all three save slots are full
            self.main_menu = MenuBox([MAIN_MENU[0], MAIN_MENU[2]])
        elif any(self.state): # if any of the three save slots is populated
            self.main_menu = MenuBox(MAIN_MENU)
        else:
            self.main_menu = MenuBox([MAIN_MENU[1],])

    def load_start_menu(self):
        self.start_menu = MenuBox(self.format_populated_save_slots())
        self.start_prompt = create_prompt('Which history do you wish to continue?')

    def load_copy_menu(self):
        self.copy_menu = MenuBox(self.format_populated_save_slots())
        self.copy_prompt = create_prompt('Which history book do you wish to copy?')

    def load_paste_menu(self):
        self.paste_menu = MenuBox(self.format_unpopulated_save_slots())
        self.paste_prompt = create_prompt('Which book do you wish to copy to?')

    def load_register_menu(self):
        self.register_menu = MenuBox(self.format_unpopulated_save_slots())
        self.register_prompt = create_prompt('Which history book do you wish to begin?')

    def load_speed_menu(self):
        self.speed_menu = MenuBox(['FAST', 'FAST', 'STILL FAST'])

    def format_populated_save_slots(self):
        return ['{}~{:~<8}~L{:02}'.format(i+1, slot['name'], slot['level']) for i, slot in enumerate(self.state) if slot]

    def format_unpopulated_save_slots(self):
        return ['{}~~~~~~'.format(i+1) for i, slot in enumerate(self.state) if not slot]

    def load_erase_menu(self):
        self.erase_menu = MenuBox(self.format_populated_save_slots())
        self.erase_prompt = create_prompt('Which history book do you wish to erase?')

    def load_confirm_erase_menu(self):
        self.confirm_erase_menu = MenuBox(['YES', 'NO'])
        self.erase_prompt = create_prompt('Are you sure?')

    def load_name_menu(self):
        self.name_menu = MenuGrid([ # each list in this list is a column in the menu grid
            ['0', 'A', 'I', 'Q',  'Y', 'a', 'i', 'q', 'y'],
            ['1', 'B', 'J', 'R',  'Z', 'b', 'j', 'r', 'z'],
            ['2', 'C', 'K', 'S',  '-', 'c', 'k', 's'],
            ['3', 'D', 'L', 'T',  ',', 'd', 'l', 't'],
            ['4', 'E', 'M', 'U',  '.', 'e', 'm', 'u'],
            ['5', 'F', 'N', 'V',  '/', 'f', 'n', 'v'],
            ['6', 'G', 'O', 'W',  '?', 'g', 'o', 'w'],
            ['7', 'H', 'P', 'X', u'–', 'h', 'p', 'x'],
            ['8', '~', '"', "'"],
            ['9', '!', 'Back.', 'Fwd.', 'End.'],
        ])
        self.name_blurb = TextBox('Please enter your name')
        self.name_field = TextBox('~~~~~~~~')
        self.name_underline = TextBox('--------')
        self.current_name_char = 0

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
        elif self.screen_state == 'name':
            self.screen.blit(self.name_blurb.surface, ((GAME_WIDTH - self.name_blurb.width)/2, top_menu_vert_pos))
            self.screen.blit(self.name_field.surface, ((GAME_WIDTH - self.name_field.width)/2, top_menu_vert_pos + 16))
            self.screen.blit(self.name_underline.surface, ((GAME_WIDTH - self.name_underline.width)/2, top_menu_vert_pos + 24))
            self.screen.blit(self.name_menu.surface, ((GAME_WIDTH - self.name_menu.get_width())/2, top_menu_vert_pos + 40))
        elif self.screen_state == 'copy':
            self.screen.blit(self.copy_prompt.surface, ((GAME_WIDTH - self.copy_prompt.width)/2, prompt_vert_pos))
            self.screen.blit(self.copy_menu.surface, ((GAME_WIDTH - self.copy_menu.get_width())/2, top_menu_vert_pos))
        elif self.screen_state == 'paste':
            self.screen.blit(self.copy_menu.surface, ((GAME_WIDTH - self.copy_menu.get_width())/2, top_menu_vert_pos))
            self.screen.blit(self.paste_prompt.surface, ((GAME_WIDTH - self.paste_prompt.width)/2, prompt_vert_pos))
            self.screen.blit(self.paste_menu.surface, ((GAME_WIDTH - self.paste_menu.get_width())/2, mid_menu_vert_pos))

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
            self.start_prompt.update(dt)
        elif self.screen_state == 'register':
            self.register_menu.update(dt)
            self.register_prompt.update(dt)
        elif self.screen_state == 'erase':
            self.erase_menu.update(dt)
            self.erase_prompt.update(dt)
        elif self.screen_state == 'confirm_erase':
            self.confirm_erase_menu.update(dt)
            self.erase_prompt.update(dt)
        elif self.screen_state == 'name':
            self.name_menu.update(dt)
            underline = '--------'
            if is_half_second():
                self.name_underline = TextBox(underline)
            else:
                i = self.current_name_char
                self.name_underline = TextBox(underline[:i] + '~' + underline[i+1:])
        elif self.screen_state == 'copy':
            self.copy_menu.update(dt)
            self.copy_prompt.update(dt)
        elif self.screen_state == 'paste':
            self.paste_menu.update(dt)
            self.paste_prompt.update(dt)

    def handle_input_main(self, pressed):
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
            elif self.main_menu.get_choice() == MAIN_MENU[3]:
                self.screen_state = 'copy'
                self.load_copy_menu()
                self.copy_menu.focus()
            self.main_menu = None

    def handle_input_start(self, pressed):
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
            self.start_prompt.shutdown()
            self.start_prompt = None
            self.main_menu.focus()

    def handle_input_copy(self, pressed):
        self.copy_menu.handle_input(pressed)
        if pressed[K_x]:
            self.screen_state = 'paste'
            self.load_paste_menu()
            self.paste_menu.focus()
            self.copy_menu.unfocus()
        elif pressed[K_z]:
            self.screen_state = 'main'
            self.load_main_menu()
            self.copy_menu = None
            self.copy_prompt.shutdown()
            self.copy_prompt = None
            self.main_menu.focus()

    def handle_input_paste(self, pressed):
        self.paste_menu.handle_input(pressed)
        if pressed[K_x]:
            self.paste_prompt.shutdown()
            copy_save_state(self.copy_menu.get_choice()[0], self.paste_menu.get_choice()[0])
            self.state = load_save_states()
            self.screen_state = 'main'
            self.load_main_menu()
            self.main_menu.focus()
            self.copy_menu = None
            self.paste_menu = None
            self.paste_prompt = None
        elif pressed[K_z]:
            self.screen_state = 'copy'
            self.load_copy_menu()
            self.paste_menu = None
            self.paste_prompt.shutdown()
            self.paste_prompt = None
            self.copy_menu.focus()

    def handle_input_speed(self, pressed):
        self.speed_menu.handle_input(pressed)
        if pressed[K_x]:
            self.start_prompt.shutdown()
            time.sleep(.5)
            slot = int(self.start_menu.get_choice()[0])
            self.game.game_state = self.state[slot-1]
            self.game.slot = slot
            if self.game.game_state['level'] == 0:
                self.game.game_state['level'] = 1
                self.game.set_screen_state('beginning')
            else:
                hq_map = '{}_palace'.format(self.game.game_state['hq'])
                self.game.set_current_map(hq_map, [17,15], 'n', followers='trail', continue_current_music=True)
        elif pressed[K_z]:
            self.screen_state = 'start'
            self.start_menu.focus()
            self.speed_menu = None

    def handle_input_register(self, pressed):
        self.register_menu.handle_input(pressed)
        if pressed[K_x]:
            self.screen_state = 'name'
            self.load_name_menu()
            self.register_prompt.shutdown()
            self.register_prompt = None
            self.name_menu.focus()
        elif pressed[K_z]:
            self.screen_state = 'main'
            self.load_main_menu()
            self.register_menu = None
            self.register_prompt.shutdown()
            self.register_prompt = None
            self.main_menu.focus()

    def handle_input_erase(self, pressed):
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
            self.erase_prompt.shutdown()
            self.erase_prompt = None
            self.main_menu.focus()

    def handle_input_confirm_erase(self, pressed):
        self.confirm_erase_menu.handle_input(pressed)
        if pressed[K_x] and self.confirm_erase_menu.get_choice() == 'YES':
            erase_save_state(self.erase_menu.get_choice()[0])
            self.state = load_save_states()
            self.screen_state = 'main'
            self.load_main_menu()
            self.confirm_erase_menu = None
            self.erase_menu = None
            self.erase_prompt.shutdown()
            self.erase_prompt = None
            self.main_menu.focus()
        elif pressed[K_z] or (pressed[K_x] and self.confirm_erase_menu.get_choice() == 'NO'):
            self.screen_state = 'erase'
            self.load_erase_menu()
            self.confirm_erase_menu = None
            self.erase_menu.focus()

    def handle_input_name(self, pressed):
        self.name_menu.handle_input(pressed)
        if pressed[K_x]:
            new_char = self.name_menu.get_choice()
            if new_char == 'Back.':
                self.current_name_char = self.current_name_char-1 if self.current_name_char > 0 else 0
            elif new_char == 'Fwd.':
                self.current_name_char = self.current_name_char+1 if self.current_name_char < 7 else 7
            elif new_char == 'End.':
                create_save_state(self.register_menu.get_choice()[0], self.name_field.text)
                self.state = load_save_states()
                self.screen_state = 'main'
                self.load_main_menu()
                self.register_menu = None
                self.current_name_char = None
                self.name_blurb = None
                self.name_field = None
                self.name_underline = None
                self.name_menu = None
                self.main_menu.focus()
            else:
                text = self.name_field.text
                i = self.current_name_char
                self.name_field = TextBox(text[:i] + new_char + text[i+1:])
                self.current_name_char = self.current_name_char+1 if self.current_name_char < 7 else 7

    def handle_input(self, pressed):
        if pressed[K_x]:
            self.select_sound.play()
        if self.screen_state == 'main':
            self.handle_input_main(pressed)
        elif self.screen_state == 'start':
            self.handle_input_start(pressed)
        elif self.screen_state == 'speed':
            self.handle_input_speed(pressed)
        elif self.screen_state == 'register':
            self.handle_input_register(pressed)
        elif self.screen_state == 'erase':
            self.handle_input_erase(pressed)
        elif self.screen_state == 'confirm_erase':
            self.handle_input_confirm_erase(pressed)
        elif self.screen_state == 'name':
            self.handle_input_name(pressed)
        elif self.screen_state == 'copy':
            self.handle_input_copy(pressed)
        elif self.screen_state == 'paste':
            self.handle_input_paste(pressed)
