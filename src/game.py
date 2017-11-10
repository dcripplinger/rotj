# -*- coding: UTF-8 -*-

import copy
import subprocess
import sys
import time

import pygame
from pygame.locals import *

from battle import Battle
from beginning import Beginning
from constants import BLACK, GAME_HEIGHT, GAME_WIDTH, ITEMS, MAP_NAMES, MAP_MUSIC, MAX_COMPANY_SIZE
from helpers import get_max_soldiers
from menu_screen import MenuScreen
from tiled_map import Map
from title_page import TitlePage


class Game(object):
    def __init__(self, screen):
        self.real_screen = screen
        self.virtual_width = GAME_WIDTH
        self.virtual_height = GAME_HEIGHT
        self.virtual_screen = pygame.Surface((self.virtual_width, self.virtual_height))
        self.clock = pygame.time.Clock()
        self.fps = 1000
        self.current_map = None
        self.set_screen_state('title')
        pygame.event.set_blocked(MOUSEMOTION)
        pygame.event.set_blocked(ACTIVEEVENT)
        pygame.event.set_blocked(VIDEORESIZE)
        pygame.event.set_blocked(KEYUP)
        self.title_page = TitlePage(self.virtual_screen, self)
        self.menu_screen = MenuScreen(self.virtual_screen, self)
        self.beginning_screen = Beginning(self, self.virtual_screen)
        self.game_state = None
        self.fitted_screen = None # gets initialized in resize_window()
        self.window_size = screen.get_size()
        self.resize_window(self.window_size)
        self.change_map_time_elapsed = None
        self.walk_sound = pygame.mixer.Sound('data/audio/walk.wav')
        self.fade_out = False
        self.continue_current_music = False
        self.next_map = None
        self.fade_alpha = None
        self.current_music = None
        self.battle = None

        # See the bottom of this class for the defs of all these handlers
        self.condition_side_effects = {
            'talked_with_melek_merchant': self.handle_talked_with_melek_merchant,
            'ammah_and_manti_join': self.handle_ammah_and_manti_join,
        }

    def conditions_are_met(self, conditions):
        if conditions is None:
            return True
        for condition, expected in conditions.items():
            if expected and condition not in self.game_state['conditions']:
                return False
            if not expected and condition in self.game_state['conditions']:
                return False
        return True

    def get_dialog_for_condition(self, dialog):
        """
        Returns the first dialog text with a condition matching the game state.
        """
        if isinstance(dialog, basestring):
            return dialog
        if isinstance(dialog, (list, tuple)):
            for (i, potential_dialog) in enumerate(dialog):
                if potential_dialog.get('condition') in self.game_state.get('conditions', set()):
                    dialog = potential_dialog
                    break
                if i == len(dialog)-1:
                    dialog = potential_dialog

        # Now dialog is a dict with the correct dialog for the game state.
        if dialog.get('game_state_action'):
            self.set_game_state_condition(dialog['game_state_action'])
        return dialog

    def set_game_state_condition(self, condition):
        side_effect = self.condition_side_effects.get(condition)
        if side_effect:
            side_effect()
        conditions = set(self.game_state['conditions'])
        conditions.add(condition)
        self.update_game_state({
            'conditions': conditions,
        })

    def try_toggle_equip_on_item(self, user, item_index):
        user_name = user.lower()
        company = copy.deepcopy(self.game_state['company'])
        for warlord in company:
            if warlord['name'] == user_name:
                user_dict = warlord
                break
        assert user_dict
        item = user_dict['items'][item_index]
        equip_type = ITEMS[item['name']].get('equip_type')
        if not equip_type:
            return
        equipped_before = item.get('equipped', False)
        item['equipped'] = not equipped_before
        if not equipped_before:
            for other_item in user_dict['items']:
                if other_item == item:
                    continue
                if ITEMS[other_item['name']].get('equip_type') == equip_type:
                    other_item['equipped'] = False
        self.update_game_state({'company': company})

    def pass_item(self, user, recipient, item_index):
        user_name = user.lower()
        recipient_name = recipient.lower()
        company = copy.deepcopy(self.game_state['company'])
        for warlord in company:
            if warlord['name'] == recipient_name:
                recipient_dict = warlord
            elif warlord['name'] == user_name:
                user_dict = warlord
        assert recipient_dict
        assert user_dict
        item = user_dict['items'].pop(item_index)
        if 'equipped' in item:
            item['equipped'] = False
        recipient_dict['items'].append(item)
        self.update_game_state({'company': company})        

    def get_items(self, warlord):
        warlord = warlord.lower()
        for info in self.game_state['company']:
            if info['name'] == warlord:
                warlord_info = info
                break
        return list(warlord_info['items'])

    def get_teleport_cities(self):
        return [city['name'].title() for city in self.game_state['cities'] if city.get('teleport')]

    def get_level(self):
        return self.game_state['level']

    def get_equips(self, warlord):
        for info in self.game_state['company']:
            if info['name'] == warlord:
                warlord_info = info
                break
        return [item for item in warlord_info['items'] if item.get('equipped')]

    def try_set_tactician(self, warlord):
        warlord_name = warlord.lower()
        company = copy.deepcopy(self.game_state['company'])
        for warlord in company:
            if warlord['name'] == warlord_name:
                warlord['tactician'] = True
            else:
                warlord['tactician'] = False
        self.update_game_state({'company': company})
        return True

    def retire_tactician(self, warlord):
        warlord_name = warlord.lower()
        company = copy.deepcopy(self.game_state['company'])
        for warlord in company:
            if warlord['name'] == warlord_name:
                warlord['tactician'] = False
                break
        self.update_game_state({'company': company})

    def get_company_names(self, omit=None, with_empty_item_slots=False):
        return [
            (u'★' if warlord.get('tactician') else '')
            + ('*' if warlord['soldiers'] == 0 else '')
            + warlord['name'].title()
            for warlord in self.game_state['company']
            if warlord['name'] != omit and (not with_empty_item_slots or len(warlord['items']) < 8)
        ]

    def heal(self, warlord, amount):
        warlord_name = warlord.lower()
        company = copy.deepcopy(self.game_state['company'])
        for warlord in company:
            if warlord['name'] == warlord_name:
                max_soldiers = get_max_soldiers(warlord_name, self.game_state['level'])
                warlord['soldiers'] = min(warlord['soldiers']+amount, max_soldiers)
                break
        self.update_game_state({'company': company})

    def remove_item(self, warlord, index):
        warlord_name = warlord.lower()
        company = copy.deepcopy(self.game_state['company'])
        for warlord in company:
            if warlord['name'] == warlord_name:
                del warlord['items'][index]
                break
        self.update_game_state({'company': company})

    def update_company_order(self, new_order):
        new_company = []
        for name in new_order:
            for warlord in self.game_state['company']:
                if name == warlord['name']:
                    new_company.append(warlord)
                    break
        self.update_game_state({'company': new_company})

    def set_screen_state(self, state):
        '''
        Valid screen states are 'title', 'game', 'menu', 'beginning', 'change_map', 'battle'
        '''
        self._screen_state = state
        if state in ['title', 'menu', 'battle']:
            pygame.key.set_repeat(300, 300)
        else:
            pygame.key.set_repeat(50, 50)
        if state == 'change_map':
            self.fade_out = True

    def start_battle(self):
        self.set_screen_state('battle')
        allies = copy.deepcopy(self.game_state['company'][0:5])
        enemies = self.get_random_encounter_enemies()
        self.battle = Battle(self.virtual_screen, self, allies, enemies)

    def get_random_encounter_enemies(self):
        return [{'name': 'bandit'}, {'name': 'bandit'}]

    def update_game_state(self, updates):
        self.game_state.update(updates)

    def add_to_company(self, names):
        company = copy.deepcopy(self.game_state['company'])
        reserve = copy.deepcopy(self.game_state['reserve'])
        level = self.game_state['level']
        if isinstance(names, basestring):
            names = [names]
        for name in names:
            if len(company) < MAX_COMPANY_SIZE:
                company.append({
                    'name': name,
                    'soldiers': get_max_soldiers(name, level),
                    'items': [],
                })
            else:
                reserve.append(name)
        self.update_game_state({
            'company': company,
            'reserve': reserve,
        })

    def add_to_inventory(self, item):
        acquired_items = list(self.game_state['acquired_items'])
        if 'id' in item:
            acquired_items.append(item['id'])
        company = copy.deepcopy(self.game_state['company'])
        placed = False
        for warlord in company:
            if len(warlord['items']) == 8 or warload['soldiers'] == 0:
                continue
            placed = True
            warlord['items'].append(item['name'])
        surplus = list(self.game_state['surplus'])
        if not placed:
            surplus.append(item['name'])
        self.update_game_state({'acquired_items': acquired_items, 'company': company, 'surplus': surplus})

    def set_current_map(
        self, map_name, position, direction, followers='under', dialog=None, continue_current_music=False,
    ):
        assert followers in [
            'trail', # position the followers trailing behind the hero
            'under', # position the followers underneath the hero on the same tile
        ]
        self.next_map = Map(
            self.virtual_screen, map_name, self, position, direction=direction, followers=followers,
            opening_dialog=dialog,
        )
        self.continue_current_music = continue_current_music
        self.fade_alpha = 0
        self.set_screen_state('change_map')

    def resize_window(self, size):
        self.real_screen = pygame.display.set_mode(size)
        (width, height) = size
        width_multiplier = width*1.0 / self.virtual_width
        height_multiplier = height*1.0 / self.virtual_height
        multiplier = min(width_multiplier, height_multiplier)
        fitted_width = int(self.virtual_width*multiplier)
        fitted_height = int(self.virtual_height*multiplier)
        fitted_x_pos = (width - fitted_width) / 2
        fitted_y_pos = (height - fitted_height) / 2
        self.fitted_screen = self.real_screen.subsurface(
            (fitted_x_pos, fitted_y_pos, fitted_width, fitted_height)
        )

    def scale(self):
        self.real_screen.fill(BLACK)
        pygame.transform.scale(self.virtual_screen, self.fitted_screen.get_size(), self.fitted_screen)

    def draw(self):
        if self._screen_state == 'game':
            self.current_map.draw()
        elif self._screen_state == 'title':
            self.title_page.draw()
        elif self._screen_state == 'menu':
            self.menu_screen.draw()
        elif self._screen_state == 'beginning':
            self.beginning_screen.draw()
        elif self._screen_state == 'battle':
            self.battle.draw()
        self.scale()

    def update(self, dt):
        if self._screen_state == 'game':
            self.current_map.update(dt)
            if self.current_music == 'intro' and not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(MAP_MUSIC[self.current_map.name]['repeat'])
                pygame.mixer.music.play(-1)
                self.current_music = 'repeat'
        elif self._screen_state == 'title':
            self.title_page.update(dt)
        elif self._screen_state == 'menu':
            self.menu_screen.update(dt)
        elif self._screen_state == 'beginning':
            self.beginning_screen.update(dt)
        elif self._screen_state == 'change_map':
            self.update_change_map(dt)

    def update_change_map(self, dt):
        if self.change_map_time_elapsed is None:
            self.change_map_time_elapsed = 0
            self.fade_out = True
            if not self.continue_current_music:
                pygame.mixer.music.stop()
                self.current_music = None
                time.sleep(.1)
                self.walk_sound.play()
        self.change_map_time_elapsed += dt
        update_interval = .1
        alpha_step = 50 # increments within the range of 0 to 255 for transparency (255 is black)
        if self.change_map_time_elapsed >= update_interval:
            self.change_map_time_elapsed -= update_interval
            if self.fade_out:
                self.fade_alpha = min(255, self.fade_alpha + alpha_step)
                if self.fade_alpha == 255:
                    self.fade_out = False # next we need to fade in
            else:
                if self.fade_alpha == 255:
                    self.fade_alpha = 254
                    self.current_map = self.next_map
                    self.next_map = None
                else:
                    self.fade_alpha = max(0, self.fade_alpha - alpha_step)
                if self.fade_alpha == 0:
                    self.set_screen_state('game')
                    if not self.continue_current_music:
                        music = MAP_MUSIC[self.current_map.name]
                        if music['intro']:
                            pygame.mixer.music.load(music['intro'])
                            pygame.mixer.music.play()
                            self.current_music = 'intro'
                        else:
                            pygame.mixer.music.load(music['repeat'])
                            pygame.mixer.music.play(-1)
                            self.current_music = 'repeat'
                    self.change_map_time_elapsed = None
                    self.fade_alpha = None
                    return
        fade_box = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        fade_box.set_alpha(self.fade_alpha)
        fade_box.fill(BLACK)
        if self.current_map:
            self.current_map.draw()
        self.virtual_screen.blit(fade_box, (0,0))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
                pygame.quit()
                return
            if event.type == KEYDOWN:
                pressed = pygame.key.get_pressed()
                if pressed[K_ESCAPE]:
                    self.running = False
                    pygame.quit()
                    print(" ")
                    time.sleep(0.5)
                    print("Shutdown... Complete")
                    sys.exit()
                    return
                if self._screen_state == "game":
                    self.current_map.handle_input(pressed)
                elif self._screen_state == 'title':
                    self.title_page.handle_input(pressed)
                elif self._screen_state == 'menu':
                    self.menu_screen.handle_input(pressed)
                elif self._screen_state == 'beginning':
                    self.beginning_screen.handle_input(pressed)

    def run(self):
        self.running = True
        try:
            while self.running:
                dt = self.clock.tick(self.fps)/1000.0
                self.handle_input()
                self.update(dt)
                self.draw()
                pygame.display.flip()
        except KeyboardInterrupt:
            self.running = False
            pygame.quit()

    ###########################################################
    # Condition side effect handlers get defined here         #
    ###########################################################

    # Handlers should be added to self.condition_side_effects in __init__().
    # The handler cannot take any args (other than self).
    # The handler does not add the condition to self.game_state['conditions'].
    # That is the job of set_game_state_condition().

    def handle_talked_with_melek_merchant(self):
        self.update_game_state({
            'money': self.game_state['money'] + 200,
            'food': self.game_state['food'] + 1000,
        })

    def handle_ammah_and_manti_join(self):
        self.add_to_company(['ammah', 'manti'])
