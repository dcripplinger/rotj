# -*- coding: UTF-8 -*-

import copy
import math
import subprocess
import sys
import time

import pygame
from pygame.locals import *

from battle import Battle
from battle_intro import BattleIntro
from beginning import Beginning
from constants import (
    BATTLE_MUSIC, BLACK, EXP_REQUIRED_BY_LEVEL, GAME_HEIGHT, GAME_WIDTH, HQ, ITEMS, MAP_MUSIC, MAX_COMPANY_SIZE,
    MAX_ITEMS_PER_PERSON, MAX_NUM, SHOP_MUSIC,
)
from helpers import (
    get_armor_class_by_level,
    get_attack_points_by_level,
    get_max_soldiers,
    get_max_tactical_points,
    get_tactics,
    load_stats,
    save_game_state,
)
from menu_screen import MenuScreen
from tiled_map import Map
from title_page import TitlePage


class Game(object):
    def __init__(self, screen):
        self.battle_intro = None
        self.real_screen = screen
        self.virtual_width = GAME_WIDTH
        self.virtual_height = GAME_HEIGHT
        self.virtual_screen = pygame.Surface((self.virtual_width, self.virtual_height))
        self.clock = pygame.time.Clock()
        self.fps = 1000
        self.current_map = None
        self.title_page = TitlePage(self.virtual_screen, self)
        self.set_screen_state('title')
        pygame.event.set_blocked(MOUSEMOTION)
        pygame.event.set_blocked(ACTIVEEVENT)
        pygame.event.set_blocked(VIDEORESIZE)
        pygame.event.set_blocked(KEYUP)
        self.menu_screen = MenuScreen(self.virtual_screen, self)
        self.beginning_screen = Beginning(self, self.virtual_screen)
        self.game_state = None
        self.fitted_screen = None # gets initialized in resize_window()
        self.window_size = screen.get_size()
        self.resize_window(self.window_size)
        self.change_map_time_elapsed = None
        self.walk_sound = pygame.mixer.Sound('data/audio/walk.wav')
        self.encounter_sound = pygame.mixer.Sound('data/audio/encounter.wav')
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
            'talked_with_jeneum': self.handle_talked_with_jeneum,
            'talked_with_nehor': self.handle_talked_with_nehor,
        }

    def conditions_are_met(self, conditions):
        if conditions is None or len(conditions) == 0:
            return True
        if isinstance(conditions, basestring):
            conditions = {conditions: True}
        elif isinstance(conditions, (tuple, list)):
            conditions = {condition: True for condition in conditions}
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
                if potential_dialog.get('condition') in self.game_state.get('conditions', []):
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
        conditions = list(self.game_state['conditions'])
        conditions.append(condition)
        self.update_game_state({
            'conditions': conditions,
        })
        the_map = self.current_map or self.next_map
        if the_map:
            the_map.handle_game_state_condition(condition)

    def get_music(self, map_name):
        return MAP_MUSIC.get(map_name, SHOP_MUSIC)

    def delete_member(self, warlord_index):
        company = copy.deepcopy(self.game_state['company'])
        surplus = copy.deepcopy(self.game_state['surplus'])
        reserve = copy.deepcopy(self.game_state['reserve'])
        for item in company[warlord_index]['items']:
            surplus.insert(0, item['name'])
        warlord = company.pop(warlord_index)
        reserve.insert(0, warlord['name'])
        self.update_game_state({'company': company, 'surplus': surplus, 'reserve': reserve})
        self.current_map.load_company_sprites(
            self.current_map.hero.position,
            self.current_map.hero.direction,
            'inplace',
        )

    def recruit(self, reserve_index):
        company = copy.deepcopy(self.game_state['company'])
        reserve = copy.deepcopy(self.game_state['reserve'])
        warlord_name = reserve.pop(reserve_index)
        level = self.game_state['level']
        company.append({
            'name': warlord_name,
            'soldiers': get_max_soldiers(warlord_name, level),
            'tactical_points': get_max_tactical_points(warlord_name, level),
            'items': [],
        })
        self.update_game_state({'company': company, 'reserve': reserve})
        self.current_map.load_company_sprites(
            self.current_map.hero.position,
            self.current_map.hero.direction,
            'inplace',
        )

    def fire(self, reserve_index):
        reserve = copy.deepcopy(self.game_state['reserve'])
        reserve.pop(reserve_index)
        self.update_game_state({'reserve': reserve})

    def get_surplus_item(self, surplus_index, warlord_index):
        company = copy.deepcopy(self.game_state['company'])
        surplus = copy.deepcopy(self.game_state['surplus'])
        item_name = surplus.pop(surplus_index)
        company[warlord_index]['items'].append({'name': item_name})
        self.update_game_state({'company': company, 'surplus': surplus})

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
            for index, other_item in enumerate(user_dict['items']):
                if index == item_index:
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

    def get_leader(self):
        for warlord in self.game_state['company']:
            if warlord['soldiers'] > 0:
                return copy.deepcopy(warlord)

    def get_equips(self, warlord):
        for info in self.game_state['company']:
            if info['name'] == warlord:
                warlord_info = info
                break
        return [item for item in warlord_info['items'] if item.get('equipped')]

    def get_tactician(self):
        for warlord in self.game_state['company']:
            if warlord.get('tactician'):
                return warlord

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

    def start_sleep(self, sleep_music, dialog, heal=False):
        self.set_current_map(
            self.current_map.name, self.current_map.hero.position, self.current_map.hero.direction, followers='trail',
            dialog=dialog,
        )
        self.set_screen_state('sleep')
        if heal:
            company = copy.deepcopy(self.game_state['company'])
            for warlord in company:
                if warlord['soldiers'] > 0:
                    warlord['soldiers'] = get_max_soldiers(warlord['name'], self.game_state['level'])
                    warlord['tactical_points'] = get_max_tactical_points(warlord['name'], self.game_state['level'])
            self.update_game_state({'company': company})
        self.sleep_music = sleep_music

    def save(self):
        save_game_state(self.slot, self.game_state)

    def set_screen_state(self, state):
        '''
        Valid screen states are 'title', 'game', 'menu', 'beginning', 'change_map', 'battle', 'start_battle', 'sleep'
        '''
        self._screen_state = state
        if state in ['title', 'menu', 'battle']:
            pygame.key.set_repeat(300, 300)
        else:
            pygame.key.set_repeat(50, 50)

        if state in ['change_map', 'sleep']:
            self.fade_out = True
        elif state == 'battle':
            battle_music_files = BATTLE_MUSIC[self.battle.battle_type]
            if battle_music_files.get('intro'):
                self.current_music = 'intro'
                music_file = battle_music_files['intro']
            else:
                self.current_music = 'repeat'
                music_file = battle_music_files['repeat']
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.play()
        elif state == 'title':
            self.battle = None
            self.current_map = None
            self.title_page.reset()
            self.menu_screen = MenuScreen(self.virtual_screen, self)
            self.beginning_screen = Beginning(self, self.virtual_screen)

    def start_battle(self, enemies, battle_type, near_water, intro=None, exit=None, battle_name=None, narration=None):
        self.set_screen_state('start_battle')
        allies = copy.deepcopy([warlord for warlord in self.game_state['company'][0:5] if warlord['soldiers'] > 0])
        tactician = self.get_tactician()
        if tactician:
            tactical_points = tactician['tactical_points']
            tactics = get_tactics(load_stats(tactician['name']), self.game_state['level'], pretty=False)
        else:
            tactical_points = 0
            tactics = None
        self.battle = Battle(
            self.virtual_screen, self, allies, enemies, battle_type, tactical_points, tactics, near_water, exit=exit,
            battle_name=battle_name, narration=narration,
        )
        if intro:
            self.battle_intro = BattleIntro(self.virtual_screen, enemies[0]['name'], intro)
        pygame.mixer.music.stop()
        self.continue_current_music = False
        self.current_music = None
        time.sleep(.1)
        self.encounter_sound.play()

    def collect_spoils(self, experience, money, food):
        self.update_game_state({
            'money': min(self.game_state['money'] + money, MAX_NUM),
            'food': min(self.game_state['food'] + food, MAX_NUM),
            'experience': min(self.game_state['experience'] + experience, EXP_REQUIRED_BY_LEVEL[90]),
        })
        adjustments = 0
        if 'talked_with_exp_guy' in self.game_state['conditions']:
            adjustments += 1
        if 'talked_with_exp_guy_again' in self.game_state['conditions']:
            adjustments += 1
        levels_earned = []
        level_to_check = self.game_state['level'] + 1
        level_reached = True
        while level_reached:
            exp_required = EXP_REQUIRED_BY_LEVEL.get(level_to_check - adjustments)
            if exp_required is not None and self.game_state['experience'] >= exp_required:
                levels_earned.append(level_to_check)
                level_to_check += 1
            else:
                level_reached = False
        if len(levels_earned) > 0:
            self.update_game_state({'level': levels_earned[-1]})
        return levels_earned

    def increment_tactical_points(self):
        company = copy.deepcopy(self.game_state['company'])
        level = self.game_state['level']
        for warlord in company:
            if warlord['tactical_points'] < get_max_tactical_points(warlord['name'], level):
                warlord['tactical_points'] += 1
        self.update_game_state({'company': company})

    def end_battle(self, battle_company, tactical_points, battle_name=None):
        self.next_map = self.current_map
        self.current_map = None
        self.fade_alpha = 0
        self.continue_current_music = False
        self.set_screen_state('change_map')
        company = []
        for warlord in self.game_state['company']:
            if warlord['name'] in battle_company:
                battle_guy = battle_company[warlord['name']]
                new_warlord = {
                    'name': warlord['name'],
                    'soldiers': battle_guy['soldiers'],
                    'tactical_points': (
                        battle_guy['tactical_points']
                        if 'liahona' in (item['name'] for item in battle_guy['items'])
                        else warlord['tactical_points']
                    ),
                    'items': battle_guy['items'],
                    'tactician': False if battle_guy['soldiers'] == 0 else warlord.get('tactician', False),
                }
            else:
                new_warlord = warlord
            if warlord.get('tactician'):
                new_warlord['tactical_points'] = tactical_points
            company.append(new_warlord)
        self.update_game_state({'company': company})
        self.next_map.load_company_sprites(self.next_map.hero.position, self.next_map.hero.direction, 'inplace')
        if battle_name:
            self.set_game_state_condition(battle_name)

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
                    'tactical_points': get_max_tactical_points(name, level),
                })
            else:
                reserve.append(name)
        self.update_game_state({
            'company': company,
            'reserve': reserve,
        })

    def add_to_inventory(self, item, warlord_index=None):
        """
        This is for picking up items when warlord_index is None.
        This is used for buying items when warlord_index is not None, since the warlord who buys it is specified.
        """
        company = copy.deepcopy(self.game_state['company'])
        placed = False
        if warlord_index is not None:
            assert len(company[warlord_index]['items']) < MAX_ITEMS_PER_PERSON
            company[warlord_index]['items'].append({'name': item})
            placed = True
        else:
            for warlord in company:
                if len(warlord['items']) >= MAX_ITEMS_PER_PERSON or warlord['soldiers'] == 0:
                    continue
                placed = True
                warlord['items'].append({'name': item})
                break
        surplus = list(self.game_state['surplus'])
        if not placed:
            surplus.insert(0, {'name': item})
        self.update_game_state({'company': company, 'surplus': surplus})

    def sell_item(self, warlord_index, item_index):
        company = copy.deepcopy(self.game_state['company'])
        item = company[warlord_index]['items'].pop(item_index)['name']
        value = int(ITEMS[item]['cost'] * 0.75)
        self.update_game_state({
            'money': min(MAX_NUM, self.game_state['money'] + value),
            'company': company,
        })

    def try_set_hq(self):
            city = self.current_map.name.split('_')[0]
            if city not in HQ:
                return "I'm sorry, but this city does not have sufficient space for you to set up a base of operations."
            self.update_game_state({'hq': city})
            return None

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
        elif self._screen_state == 'battle_intro' and self.battle_intro:
            self.battle_intro.draw()
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
        elif self._screen_state == 'sleep':
            self.update_sleep(dt)
        elif self._screen_state == 'start_battle':
            self.update_battle_fade(dt)
        elif self._screen_state == 'battle':
            self.battle.update(dt)
            if self.current_music == 'intro' and not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(BATTLE_MUSIC[self.battle.battle_type]['repeat'])
                pygame.mixer.music.play(-1)
                self.current_music = 'repeat'
        elif self._screen_state == 'battle_intro':
            if self.battle_intro:
                self.battle_intro.update(dt)
            else:
                self.set_screen_state('battle')

    def update_battle_fade(self, dt):
        if self.change_map_time_elapsed is None:
            self.change_map_time_elapsed = 0
            self.show_map = True
            self.triangle_size = 0
        self.change_map_time_elapsed += dt
        update_interval = .02
        if self.change_map_time_elapsed >= update_interval:
            self.change_map_time_elapsed -= update_interval
            self.show_map = not self.show_map
            self.triangle_size += 10*update_interval
            if self.show_map and self.current_map:
                self.current_map.draw()
                self.draw_triangle_transition()
            else:
                self.virtual_screen.fill(BLACK)

    def draw_triangle_transition(self):
        """
        Okay, okay, it's not really triangles. It's a reference to the triangle transition of DOAE.
        """
        block_size = 8
        for x in range(0, GAME_WIDTH, block_size):
            for y in range(0, GAME_HEIGHT, block_size):
                pygame.draw.rect(
                    self.virtual_screen,
                    BLACK,
                    (x,y,block_size,block_size),
                    min(int(math.ceil(self.triangle_size)), block_size),
                )
        if self.triangle_size > block_size:
            self.set_screen_state('battle_intro' if self.battle_intro else 'battle')

    def update_sleep(self, dt):
        if self.change_map_time_elapsed is None:
            self.change_map_time_elapsed = 0
            self.fade_out = True
            pygame.mixer.music.stop()
            self.current_music = None
            time.sleep(.3)
        self.change_map_time_elapsed += dt
        update_interval = .1
        alpha_step = 50 # increments within the range of 0 to 255 for transparency (255 is black)
        if self.change_map_time_elapsed >= update_interval:
            self.change_map_time_elapsed -= update_interval
            if self.fade_out:
                self.fade_alpha = min(255, self.fade_alpha + alpha_step)
                if self.fade_alpha == 255:
                    self.fade_out = False # next we need to fade in
                    if self.sleep_music:
                        pygame.mixer.music.load(self.sleep_music)
                        pygame.mixer.music.play()
                    self.current_map = self.next_map
                    self.next_map = None
            elif not pygame.mixer.music.get_busy():
                if self.fade_alpha == 255:
                    self.fade_alpha = 254
                else:
                    self.fade_alpha = max(0, self.fade_alpha - alpha_step)
                if self.fade_alpha == 0:
                    self.set_screen_state('game')
                    music = self.get_music(self.current_map.name)
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
        self.current_map.draw()
        self.virtual_screen.blit(fade_box, (0,0))

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
                        music = self.get_music(self.current_map.name)
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
        elif self.battle:
            self.battle.draw()
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
                elif self._screen_state == 'battle':
                    self.battle.handle_input(pressed)
                elif self._screen_state == 'battle_intro' and self.battle_intro:
                    self.battle_intro.handle_input(pressed)
                    if pressed[K_x] and not self.battle_intro.dialog.has_more_stuff_to_show():
                        self.set_screen_state('battle')
                        self.battle_intro.dialog.shutdown()
                        self.battle_intro = None

    def run(self):
        self.running = True
        dt = 0.0
        try:
            while self.running:
                dt += self.clock.tick(self.fps)/1000.0
                if dt >= 0.01:
                    self.handle_input()
                    self.update(dt)
                    self.draw()
                    pygame.display.flip()
                    dt = 0.0
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

    def handle_talked_with_jeneum(self):
        battle_data = {
            'enemies': [
                {'name': 'jeneum', 'level': 9},
                {'name': 'limhah', 'level': 7},
                {'name': 'zenos', 'level': 7},
            ],
            'battle_type': 'story',
            'exit': (
                "Look, I'll tell you whatever you want to know! You're looking for Nehor? He's hiding out somewhere in "
                "Gideon to the north."
            ),
        }
        enemies = []
        for enemy in battle_data['enemies']:
            stats = load_stats(enemy['name'])
            stats['soldiers'] = get_max_soldiers(enemy['name'], enemy['level'])
            stats['tactical_points'] = get_max_tactical_points(enemy['name'], enemy['level'])
            stats['attack_points'] = get_attack_points_by_level(enemy['level'])
            stats['armor_class'] = get_armor_class_by_level(enemy['level'])
            stats['tactics'] = get_tactics(enemy['name'], enemy['level'], pretty=False)
            enemies.append({
                'name': enemy['name'],
                'stats': stats,
            })
        self.current_map.start_battle_after_dialog(
            enemies, battle_data['battle_type'], exit=battle_data['exit'], battle_name="battle04",
        )

    def handle_talked_with_nehor(self):
        battle_data = {
            'enemies': [
                {'name': 'nehor', 'level': 7},
                {'name': 'gad', 'level': 11},
                {'name': 'emer', 'level': 7},
                {'name': 'jeneum', 'level': 9},
            ],
            'battle_type': 'story',
            'intro': (
                "You don't have to do this, Moroni. Join my religion and I will make you rich beyond your wildest "
                "dreams. ~~~~~~~~ ~~~~~~~~ ~~~~~~~~ ~~~~~~~~ ~~~~~~~~ ~~~~~~~~ ~~~~~~~~ No? Then we fight!"
            ),
            'exit': "Noooo!",
            'narration': (
                "You have succeeded in captured Nehor! Take him back to Alma in Zarahemla so that he can be judged for "
                "his crimes."
            ),
        }
        enemies = []
        for enemy in battle_data['enemies']:
            stats = load_stats(enemy['name'])
            stats['soldiers'] = get_max_soldiers(enemy['name'], enemy['level'])
            stats['tactical_points'] = get_max_tactical_points(enemy['name'], enemy['level'])
            stats['attack_points'] = get_attack_points_by_level(enemy['level'])
            stats['armor_class'] = get_armor_class_by_level(enemy['level'])
            stats['tactics'] = get_tactics(enemy['name'], enemy['level'], pretty=False)
            enemies.append({
                'name': enemy['name'],
                'stats': stats,
            })
        self.current_map.start_battle_after_dialog(
            enemies, battle_data['battle_type'], intro=battle_data['intro'], exit=battle_data['exit'],
            battle_name="battle05", narration=battle_data['narration'],
        )
