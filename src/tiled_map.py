# -*- coding: UTF-8 -*-

import json
import math
import os
import random

import pygame
from pygame.locals import *
import pyscroll
from pytmx.util_pygame import load_pygame

from constants import (
    DEFAULT_ENCOUNTER_CHANCE, FACELESS_ENEMIES, MAX_NUM, ITEMS, MAPS_WITH_RANDOM_ENCOUNTERS, NAMED_TELEPORTS,
    REUSABLE_MAP_NAMES, RED, GAME_WIDTH, GAME_HEIGHT, CHAPTER11_CITIES,
)
from helpers import (
    get_enemy_stats,
    get_map_filename,
    get_max_soldiers,
    get_max_tactical_points,
    get_attack_points_by_level,
    get_armor_class_by_level,
    get_tactics,
    load_json_file_if_exists,
    load_stats,
)
from hero import Hero
from map_menu import MapMenu
from report import CompanyReport, Report
from shop_mat import ShopMat
from sprite import AiSprite, Sprite
from text import create_prompt, MenuBox
from treasure import Treasure

MAX_NO_FOOD_DELTA = 0.06
MAX_EXPLODING_TIME = 1.5 # seconds
SHAKE = [
    [8, 0],
    [0, 0],
    [-8, 0],
    [0, 0],
    [0, 8],
    [0, 0],
    [0, -8],
    [0, 0],
    [8, 0],
    [0, 0],
    [-8, 0],
    [0, 0],
    [0, 8],
    [0, 0],
    [0, -8],
    [0, 0],
]


class Map(object):
    def __init__(self, screen, map_name, game, hero_position, direction='s', followers='under', opening_dialog=None):
        self.ready_explosion = False
        self.exploding = False
        self.exploding_time = 0
        self.shake = [0, 0]
        self.no_food_left = False
        self.no_food_delta = 0.0
        self.battle_after_dialog = None
        self.steps_for_tactical_points = 0
        self.company_report = None
        self.name = map_name
        self.game = game
        self.ai_sprites = {} # key is position tuple, value is ai_sprite at that position currently
        tmx_map_name = map_name
        for reusable_name in REUSABLE_MAP_NAMES:
            if map_name.endswith(reusable_name):
                tmx_map_name = reusable_name
                break
        map_filename = get_map_filename('{}.tmx'.format(tmx_map_name))
        self.json_filename = get_map_filename('{}.json'.format(map_name))
        self.encounter_filename = get_map_filename('{}_encounters.json'.format(map_name))
        self.screen = screen
        self.tmx_data = load_pygame(map_filename)
        self.load_cells_and_encounter_regions()
        map_data = pyscroll.data.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(map_data, self.screen.get_size())
        self.map_layer.zoom = 1
        self.group = pyscroll.group.PyscrollGroup(map_layer=self.map_layer)
        self.opening_dialog = create_prompt(opening_dialog) if opening_dialog is not None else None
        self.load_treasures()
        self.load_shop_mats()
        self.load_ai_sprites()
        self.hero = None
        self.follower_one = None
        self.follower_two = None
        self.peasants = []
        self.load_company_sprites(hero_position, direction, followers)
        self.map_menu = None
        self.random_encounter = False
        self.lava_sound = pygame.mixer.Sound(os.path.join('data', 'audio', 'lava.wav'))
        self.explosion_sound = pygame.mixer.Sound(os.path.join('data', 'audio', 'explosion.wav'))

    def set_game_state_condition(self, condition):
        return self.game.set_game_state_condition(condition)

    def load_cells_and_encounter_regions(self):
        with open(self.json_filename) as f:
            json_data = json.loads(f.read())
        try:
            with open(self.encounter_filename) as f:
                encounter_data = json.loads(f.read())
        except IOError:
            encounter_data = []
        self.cells = {(cell['x'], cell['y']): cell for cell in json_data}
        self.encounter_regions = {(region['x'], region['y']): region for region in encounter_data}

    def handle_game_state_condition(self, condition):
        if condition == 'ammah_and_manti_join':
            for sprite in self.group.sprites():
                if sprite.name in ['ammah', 'manti']:
                    self.group.remove(sprite)
            ai_sprites = {
                key: sprite for key, sprite in self.ai_sprites.items() if sprite.name not in ['ammah', 'manti']
            }
            self.ai_sprites = ai_sprites
        elif condition == 'battle04':
            for sprite in self.group.sprites():
                if sprite.name == 'jeneum_sleeping':
                    self.group.remove(sprite)
            ai_sprites = {
                key: sprite for key, sprite in self.ai_sprites.items() if sprite.name != 'jeneum_sleeping'
            }
            self.ai_sprites = ai_sprites
        elif condition == 'battle05':
            for sprite in self.group.sprites():
                if sprite.name == 'nehor':
                    self.group.remove(sprite)
            ai_sprites = {
                key: sprite for key, sprite in self.ai_sprites.items() if sprite.name != 'nehor'
            }
            self.ai_sprites = ai_sprites
        elif condition == 'talked_with_alma_after_nehor':
            for sprite in self.ai_sprites:
                self.group.remove(sprite)
            self.ai_sprites = {}
            self.load_ai_sprites()
        elif condition == 'battle06':
            for sprite in self.group.sprites():
                if sprite.name in ['antionum', 'alma']:
                    self.group.remove(sprite)
            ai_sprites = {
                key: sprite for key, sprite in self.ai_sprites.items() if sprite.name not in ['antionum', 'alma']
            }
            self.ai_sprites = ai_sprites
        elif condition == 'alma_joins':
            for sprite in self.group.sprites():
                if sprite.name == 'alma':
                    self.group.remove(sprite)
            ai_sprites = {
                key: sprite for key, sprite in self.ai_sprites.items() if sprite.name != 'alma'
            }
            self.ai_sprites = ai_sprites
        elif condition == 'ammon_joins':
            for sprite in self.group.sprites():
                if sprite.name == 'ammon':
                    self.group.remove(sprite)
            ai_sprites = {
                key: sprite for key, sprite in self.ai_sprites.items() if sprite.name != 'ammon'
            }
            self.ai_sprites = ai_sprites
        elif condition == 'anti_nephi_lehi_joins':
            for sprite in self.group.sprites():
                if sprite.name == 'anti-nephi-lehi':
                    self.group.remove(sprite)
            ai_sprites = {
                key: sprite for key, sprite in self.ai_sprites.items() if sprite.name != 'anti-nephi-lehi'
            }
            self.ai_sprites = ai_sprites
        elif condition == 'lamoni_joins':
            for sprite in self.group.sprites():
                if sprite.name == 'lamoni':
                    self.group.remove(sprite)
            ai_sprites = {
                key: sprite for key, sprite in self.ai_sprites.items() if sprite.name != 'lamoni'
            }
            self.ai_sprites = ai_sprites
        elif condition == 'muloki_joins':
            for sprite in self.group.sprites():
                if sprite.name == 'muloki':
                    self.group.remove(sprite)
            ai_sprites = {
                key: sprite for key, sprite in self.ai_sprites.items() if sprite.name != 'muloki'
            }
            self.ai_sprites = ai_sprites
        elif condition == 'lehi_and_aha_join':
            for sprite in self.group.sprites():
                if sprite.name in ['lehi', 'aha']:
                    self.group.remove(sprite)
            ai_sprites = {
                key: sprite for key, sprite in self.ai_sprites.items() if sprite.name not in ['lehi', 'aha']
            }
            self.ai_sprites = ai_sprites
        elif condition == 'battle20':
            for sprite in self.group.sprites():
                if getattr(sprite, 'name', '') == 'amalickiah':
                    self.group.remove(sprite)
            ai_sprites = {
                key: sprite for key, sprite in self.ai_sprites.items() if sprite.name != 'amalickiah'
            }
            self.ai_sprites = ai_sprites
        elif condition == 'battle21':
            for sprite in self.group.sprites():
                if getattr(sprite, 'name', '') == 'kingmen':
                    self.group.remove(sprite)
            ai_sprites = {
                key: sprite for key, sprite in self.ai_sprites.items() if sprite.name != 'kingmen'
            }
            self.ai_sprites = ai_sprites
        elif condition == 'battle34':
            for sprite in self.group.sprites():
                if getattr(sprite, 'name', '') == 'leantum':
                    self.group.remove(sprite)
            ai_sprites = {
                key: sprite for key, sprite in self.ai_sprites.items() if sprite.name != 'leantum'
            }
            self.ai_sprites = ai_sprites
        elif condition == 'helaman_joins':
            for sprite in self.group.sprites():
                if sprite.name == 'helaman':
                    self.group.remove(sprite)
            ai_sprites = {
                key: sprite for key, sprite in self.ai_sprites.items() if sprite.name != 'helaman'
            }
            self.ai_sprites = ai_sprites
        elif condition == 'battle56':
            for sprite in self.group.sprites():
                self.group.remove(sprite)
            self.ai_sprites = {}
            self.load_ai_sprites()
        elif condition == 'battle58':
            for sprite in self.group.sprites():
                self.group.remove(sprite)
            self.ai_sprites = {}
            self.load_ai_sprites()
        elif condition == 'battle59':
            for sprite in self.group.sprites():
                self.group.remove(sprite)
            self.ai_sprites = {}
            self.load_ai_sprites()
        elif condition == 'battle60':
            for sprite in self.group.sprites():
                self.group.remove(sprite)
            self.ai_sprites = {}
            self.load_ai_sprites()
        elif condition == 'battle61':
            for sprite in self.group.sprites():
                self.group.remove(sprite)
            self.ai_sprites = {}
            self.load_ai_sprites()
        elif condition == 'gidgiddoni_joins':
            for sprite in self.group.sprites():
                self.group.remove(sprite)
            self.ai_sprites = {}
            self.load_ai_sprites()
        elif condition == 'battle72':
            for sprite in self.group.sprites():
                self.group.remove(sprite)
            self.ai_sprites = {}
            self.load_ai_sprites()
        elif condition == 'moronihah_joins':
            for sprite in self.group.sprites():
                if sprite.name == 'moronihah':
                    self.group.remove(sprite)
            ai_sprites = {
                key: sprite for key, sprite in self.ai_sprites.items() if sprite.name != 'moronihah'
            }
            self.ai_sprites = ai_sprites
        elif condition == 'corianton_joins':
            for sprite in self.group.sprites():
                if sprite.name == 'corianton':
                    self.group.remove(sprite)
            ai_sprites = {
                key: sprite for key, sprite in self.ai_sprites.items() if sprite.name != 'corianton'
            }
            self.ai_sprites = ai_sprites
        elif condition == 'corianton_joins_again':
            for sprite in self.group.sprites():
                if sprite.name == 'corianton':
                    self.group.remove(sprite)
            ai_sprites = {
                key: sprite for key, sprite in self.ai_sprites.items() if sprite.name != 'corianton'
            }
            self.ai_sprites = ai_sprites
        elif condition == 'pahoran_joins':
            for sprite in self.group.sprites():
                if hasattr(sprite, 'name') and sprite.name == 'pahoran':
                    self.group.remove(sprite)
            ai_sprites = {
                key: sprite
                for key, sprite in self.ai_sprites.items()
                if not hasattr(sprite, 'name') or sprite.name != 'pahoran'
            }
            self.ai_sprites = ai_sprites
        elif condition == 'corianton_leaves':
            for sprite in self.group.sprites():
                self.group.remove(sprite)
            self.ai_sprites = {}
            self.load_ai_sprites()
        elif condition == 'wake_nephi':
            for sprite in self.group.sprites():
                self.group.remove(sprite)
            self.ai_sprites = {}
            self.load_ai_sprites()
        elif condition == 'pahoran_dead':
            for sprite in self.group.sprites():
                self.group.remove(sprite)
            self.ai_sprites = {}
            self.load_ai_sprites()
        elif condition == 'nephi_joins':
            for sprite in self.group.sprites():
                self.group.remove(sprite)
            self.ai_sprites = {}
            self.load_ai_sprites()
        self.load_company_sprites(self.hero.position, self.hero.direction, 'inplace')
        self.load_treasures()
        self.load_shop_mats()

    def try_toggle_equip_on_item(self, user, item_index):
        self.game.try_toggle_equip_on_item(user, item_index)

    def pass_item(self, user, recipient, item_index):
        self.game.pass_item(user, recipient, item_index)

    def heal(self, warlord, amount):
        self.game.heal(warlord, amount)
        # Reload sprites because sometimes heal() is called for resurrecting
        self.load_company_sprites(self.hero.position, self.hero.direction, 'inplace')

    def remove_item(self, warlord, index):
        self.game.remove_item(warlord, index)

    def add_to_lost_and_found(self, item):
        lost_and_found = self.game.game_state.get('lost_and_found', [])
        lost_and_found.append(item)
        self.game.update_game_state({'lost_and_found': lost_and_found})

    def teleport(self, place):
        self.game.set_current_map('overworld', NAMED_TELEPORTS[place], 's')

    def get_teleport_cities(self):
        return self.game.get_teleport_cities()

    def get_items(self, warlord):
        return self.game.get_items(warlord)

    def get_level(self):
        return self.game.get_level()

    def get_equips(self, warlord):
        return self.game.get_equips(warlord)

    def try_set_tactician(self, warlord):
        return self.game.try_set_tactician(warlord)

    def retire_tactician(self, warlord):
        self.game.retire_tactician(warlord)

    def get_company_names(self, **kwargs):
        return self.game.get_company_names(**kwargs)

    def update_company_order(self, new_order):
        self.game.update_company_order(new_order)
        self.load_company_sprites(self.hero.position, self.hero.direction, 'inplace')

    def check_for_item(self, unlocker=None):
        cell = self.cells.get(tuple(self.hero.position))
        treasure = cell.get('treasure') if cell else None
        if (
            not treasure
            or self.game.conditions_are_met(treasure['name'])
            or not self.game.conditions_are_met(treasure.get('conditions'))
        ):
            return "But nothing happened." if unlocker else "But found nothing."
        if 'locked' in treasure:
            if unlocker and treasure['locked'] != unlocker:
                return "But nothing happened."
            if not unlocker:
                return "The treasure is locked."
        if unlocker and 'locked' not in treasure:
            return "But nothing happened."
        self.treasures[tuple(self.hero.position)].open()
        self.game.set_game_state_condition(treasure['name'])
        if 'item' in treasure:
            self.game.add_to_inventory(treasure['item'])
            return "{} found.".format(treasure['item'].title())
        elif 'money' in treasure:
            money = self.game.game_state['money'] + treasure['money']
            self.game.update_game_state({'money': min(MAX_NUM, money)})
            return '{} senines found.'.format(treasure['money'])
        else:
            return "Something is wrong."

    def load_ai_sprites(self):
        for cell in self.cells.values():
            ai_sprite_data = cell.get('ai_sprite')
            if not ai_sprite_data:
                continue
            if isinstance(ai_sprite_data, dict):
                ai_sprite_data = [ai_sprite_data]
            for potential_sprite in ai_sprite_data:
                if self.game.conditions_are_met(potential_sprite.get('conditions')):
                    ai_sprite = AiSprite(
                        tmx_data=self.tmx_data, game=self.game, character=potential_sprite['name'],
                        position=[cell['x'], cell['y']], direction=potential_sprite['direction'],
                        wander=potential_sprite['wander'], tiled_map=self, dialog=potential_sprite['dialog'],
                        walk=potential_sprite.get('walk'),
                    )
                    self.group.add(ai_sprite)
                    break # Just load the first matching sprite in the list

    def load_treasures(self):
        self.treasures = {}
        for cell in self.cells.values():
            treasure_data = cell.get('treasure')
            if treasure_data:
                if not self.game.conditions_are_met(treasure_data.get('conditions')):
                    continue
                if self.game.conditions_are_met(treasure_data['name']):
                    opened = True
                else:
                    opened = False
                pos = [cell['x'], cell['y']]
                treasure = Treasure(opened=opened, invisible=treasure_data.get('invisible'), position=pos)
                self.group.add(treasure)
                self.treasures[tuple(pos)] = treasure

    def load_shop_mats(self):
        for cell in self.cells.values():
            if 'teleport' in cell and type(cell['teleport']) == dict and 'map' in cell['teleport']:
                current_shop = None
                for shop in ['inn', 'armory', 'merchant_shop', 'food_shop', 'record_office', 'reserve']:
                    if cell['teleport']['map'].endswith('_{}'.format(shop)):
                        current_shop = shop
                        break
                if current_shop:
                    self.group.add(ShopMat(typ=current_shop, position=(cell['x'], cell['y']+1)))

    def get_pos_behind(self, pos, direction):
        if direction == 'n':
            return [pos[0], pos[1]+1]
        elif direction == 's':
            return [pos[0], pos[1]-1]
        elif direction == 'e':
            return [pos[0]-1, pos[1]]
        elif direction == 'w':
            return [pos[0]+1, pos[1]]

    def get_pos_in_front(self, pos, direction):
        if direction == 'n':
            return [pos[0], pos[1]-1]
        elif direction == 's':
            return [pos[0], pos[1]+1]
        elif direction == 'e':
            return [pos[0]+1, pos[1]]
        elif direction == 'w':
            return [pos[0]-1, pos[1]]

    def load_company_sprites(self, hero_position, direction, followers):
        if self.follower_one:
            self.group.remove(self.follower_one)
        if self.follower_two:
            self.group.remove(self.follower_two)
        if self.hero:
            self.group.remove(self.hero)
        if self.peasants:
            for peasant in self.peasants:
                self.group.remove(peasant)
        peasants = 0
        if self.game.conditions_are_met('battle08') and not self.game.conditions_are_met('entered_jershon'):
            # tack on a lamanite follower peasant for each conquered place in chapter 3
            if self.game.conditions_are_met('talked_with_lamoni_after_sebus'):
                peasants += 1
            if self.game.conditions_are_met('battle10'):
                peasants += 1
            if self.game.conditions_are_met('battle13'):
                peasants += 1
            if self.game.conditions_are_met('battle14'):
                peasants += 1
            if self.game.conditions_are_met('battle17'):
                peasants += 1
        company_sprites = self.get_company_sprite_names()
        if followers == 'inplace':
            follower_one_pos = (
                self.follower_one.position if self.follower_one
                else self.get_pos_behind(hero_position, direction)
            )
            follower_one_dir = self.follower_one.direction if self.follower_one else direction
            follower_two_pos = (
                self.follower_two.position if self.follower_two
                else self.get_pos_behind(follower_one_pos, follower_one_dir)
            )
            follower_two_dir = self.follower_two.direction if self.follower_two else direction
        elif followers == 'under':
            follower_one_pos = list(hero_position)
            follower_two_pos = list(hero_position)
            follower_one_dir = direction
            follower_two_dir = direction
        else:
            follower_one_pos = self.get_pos_behind(hero_position, direction) if followers == 'trail' else hero_position[:]
            follower_two_pos = self.get_pos_behind(follower_one_pos, direction) if followers == 'trail' else hero_position[:]
            follower_one_dir = direction
            follower_two_dir = direction
        while peasants > 0:
            peasant_sprite = Sprite(
                self.tmx_data, self.game, 'villager3', hero_position[:], direction=direction,
                follower=self.peasants[0] if self.peasants else None, tiled_map=self,
            )
            self.peasants.insert(0, peasant_sprite)
            self.group.add(peasant_sprite)
            peasants -= 1
        if len(company_sprites) == 3:
            self.follower_two = Sprite(
                self.tmx_data, self.game, company_sprites[2], follower_two_pos, direction=follower_two_dir,
                tiled_map=self, follower=self.peasants[0] if self.peasants else None,
            )
            self.group.add(self.follower_two)
        else:
            self.follower_two = None
        if len(company_sprites) >= 2:
            self.follower_one = Sprite(
                self.tmx_data, self.game, company_sprites[1], follower_one_pos, direction=follower_one_dir,
                follower=self.follower_two or (self.peasants[0] if self.peasants else None), tiled_map=self,
            )
            self.group.add(self.follower_one)
        else:
            self.follower_one = None
        self.hero = Hero(
            self.tmx_data, self.game, company_sprites[0], hero_position[:], cells=self.cells, direction=direction,
            follower=self.follower_one or (self.peasants[0] if self.peasants else None), tiled_map=self,
        )
        self.group.add(self.hero)

    def get_company_sprite_names(self):
        '''
        Returns a list of names of warlords from the company that should appear on the screen as sprites.
        '''
        company = self.game.game_state['company']
        company_sprites = []
        for character in company:
            if len(company_sprites) == 3:
                break
            if character['soldiers'] == 0:
                continue
            company_sprites.append(character['name'])
        return company_sprites

    def draw(self):
        center = self.hero.rect.center
        if self.exploding:
            shake_idx = int(10 * self.exploding_time)
            shake = SHAKE[shake_idx]
            center = [center[0] + shake[0], center[1] + shake[1]]
        self.group.center(center)
        self.group.draw(self.screen)
        if self.no_food_left:
            red_box = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
            red_box.fill(RED)
            self.screen.blit(red_box, (0,0))
        if self.map_menu:
            self.map_menu.draw()
        if self.opening_dialog:
            self.screen.blit(self.opening_dialog.surface, (0, 160))
        if self.company_report:
            self.screen.blit(self.company_report.surface, (0, 0))

    def update(self, dt):
        if self.exploding:
            self.exploding_time += dt
            if self.exploding_time >= MAX_EXPLODING_TIME:
                dialog = "We are now able to pass by the wall."
                self.game.set_current_map(
                    self.name, self.hero.position, "s", dialog=dialog, continue_current_music=True, play_walk_sound=False,
                )
        self.group.update(dt)
        if self.map_menu:
            self.map_menu.update(dt)
        if self.opening_dialog:
            self.opening_dialog.update(dt)
        if self.random_encounter and self.hero.velocity == [0,0]:
            self.random_encounter = False
            enemies = self.get_random_encounter_enemies()
            if not enemies:
                return
            if enemies[0]['name'] not in FACELESS_ENEMIES:
                battle_type = 'warlord'
            else:
                battle_type = 'regular'
            self.game.start_battle(enemies, battle_type, self.is_near_water())
        if self.no_food_left:
            self.no_food_delta += dt
            if self.no_food_delta > MAX_NO_FOOD_DELTA:
                self.no_food_delta = 0.0
                self.no_food_left = False
        if not self.map_menu and self.ready_explosion:
            self.explosion_sound.play()
            self.exploding = True
            self.ready_explosion = False

    def is_near_water(self):
        x = int(self.hero.position[0])
        y = int(self.hero.position[1])
        for _x in [x-2, x-1, x, x+1, x+2]:
            for _y in [y-2, y-1, y, y+1, y+2]:
                props = self.tmx_data.get_tile_properties(_x, _y, 0) or {}
                if props.get('water') == 'true':
                    return True
        return False

    def move_hero(self, direction):
        next_pos = self.get_pos_in_front(self.hero.position, direction)
        battles = self.cells.get(tuple(next_pos), {}).get('battles') if next_pos else None
        if battles:
            chapter11_city = None
            if battles == 'chapter11_battles':
                chapter11_city = CHAPTER11_CITIES['{} {}'.format(*[int(x) for x in next_pos])]
                if self.game.conditions_are_met('battle_at_{}'.format(chapter11_city)):
                    battles = []
                else:
                    battles = load_json_file_if_exists(os.path.join('data', 'maps', 'chapter11_battles'))
            for battle_data in battles:
                if 'conditions' in battle_data and not self.game.conditions_are_met(battle_data['conditions']):
                    continue
                if self.game.conditions_are_met(battle_data['name']):
                    continue
                self.start_battle(battle_data, chapter11_city=chapter11_city)
                return
        moved = self.hero.move(direction)
        if moved and self.name in MAPS_WITH_RANDOM_ENCOUNTERS:
            if self.try_getting_random_encounter():
                self.random_encounter = True
            self.steps_for_tactical_points += 1
            if self.steps_for_tactical_points >= 5:
                self.steps_for_tactical_points -= 5
                self.game.increment_tactical_points()
            self.no_food_left = self.game.decrement_food()
            lava = self.cells.get(tuple(next_pos), {}).get('lava') == 'true'
            if lava:
                # piggy back on no_food_left for drawing red blinking screen
                self.no_food_left = True
                self.game.walk_in_lava()
                self.lava_sound.play()
            if self.no_food_left:
                self.no_food_delta = 0.0
            if self.game.cloak_steps_remaining:
                self.game.cloak_steps_remaining -= 1
                if not self.game.cloak_steps_remaining:
                    self.opening_dialog = create_prompt("The cloak has worn off. We are now visible to the enemy.")
            if self.name == 'overworld':
                self.game.mark_beaten_path(next_pos)

    def start_battle(self, battle_data, prev_experience=0, prev_money=0, prev_food=0, chapter11_city=None):
        battle_type = battle_data.get('battle_type', 'story')
        enemies = []
        for enemy in battle_data['enemies']:
            if 'stats' in enemy:
                stats = enemy['stats']
            else:
                stats = load_stats(enemy['name'])
                stats['soldiers'] = get_max_soldiers(enemy['name'], enemy['level'])
                stats['tactical_points'] = get_max_tactical_points(enemy['name'], enemy['level'])
                stats['attack_points'] = get_attack_points_by_level(enemy['level'])
                stats['armor_class'] = get_armor_class_by_level(enemy['level'])
                stats['tactics'] = get_tactics(enemy['name'], enemy['level'], pretty=False)
            enemies.append({
                'name': enemy['name'],
                'stats': stats,
                'reinforcements': enemy.get('reinforcements', False),
            })
        self.game.start_battle(
            enemies, battle_type, self.is_near_water(), intro=battle_data.get('intro'),
            exit=battle_data.get('exit'), battle_name=battle_data['name'],
            narration=battle_data.get('narration'), offguard=battle_data.get('offguard'),
            enemy_retreat=battle_data.get('enemy_retreat'), chapter11_city=chapter11_city,
            next_battle=battle_data.get('next_battle'), prev_experience=prev_experience,
            prev_money=prev_money, prev_food=prev_food,
        )

    def try_getting_random_encounter(self):
        # This function assumes that outside of it has already checked that self.name in MAPS_WITH_RANDOM_ENCOUNTERS.
        if self.game.devtools['No encounters'] or self.game.cloak_steps_remaining:
            return False
        (x,y) = self.get_pos_in_front(self.hero.position, self.hero.direction)
        props = self.tmx_data.get_tile_properties(x, y, 0) or {}
        encounter_chance = float(props.get('encounter', DEFAULT_ENCOUNTER_CHANCE))
        return random.random() < encounter_chance

    def filter_out_allies(self, encounters):
        '''
        Takes a list of possible encounters for a region and filters out any group of enemies (a.k.a. an encounter)
        that has an enemy who has joined your side.
        '''
        new_encounters = []
        for encounter in encounters:
            include = True
            for enemy_name in encounter:
                if self.game.is_in_company(enemy_name) or self.game.is_in_reserve(enemy_name):
                    include = False
                    break
            if include:
                new_encounters.append(encounter)
        return new_encounters

    def get_random_encounter_enemies(self):
        x = int(self.hero.position[0]) / 50
        y = int(self.hero.position[1]) / 50
        # The special (-1,-1) region means for the whole map, like in caves
        region = self.encounter_regions.get((x,y)) or self.encounter_regions.get((-1,-1))
        if not region:
            return None
        possible_encounters = self.filter_out_allies(region['encounters'])
        enemy_names = random.choice(possible_encounters)
        enemies = []
        for name in enemy_names:
            if 'level' in region['stats'][name]:
                stats = get_enemy_stats(name, region['stats'][name]['level'])
                stats['capture'] = region['stats'][name].get('capture')
            else:
                stats = region['stats'][name]
            enemies.append({'name': name, 'stats': stats})
        return enemies

    def handle_input(self, pressed):
        if self.exploding:
            return
        if self.opening_dialog:
            self.opening_dialog.handle_input(pressed)
            if pressed[K_x] and not self.opening_dialog.has_more_stuff_to_show():
                self.opening_dialog = None
        elif self.map_menu:
            action = self.map_menu.handle_input(pressed)
            if action == 'exit':
                self.map_menu = None
                pygame.key.set_repeat(50, 50)
                if self.battle_after_dialog:
                    self.game.start_battle(
                        self.battle_after_dialog['enemies'],
                        self.battle_after_dialog['battle_type'],
                        self.is_near_water(),
                        intro=self.battle_after_dialog['intro'],
                        exit=self.battle_after_dialog['exit'],
                        narration=self.battle_after_dialog['narration'],
                        battle_name=self.battle_after_dialog['battle_name'],
                        continue_music=self.battle_after_dialog['continue_music'],
                        offguard = self.battle_after_dialog['offguard'],
                        next_battle = self.battle_after_dialog['next_battle'],
                    )
                    self.battle_after_dialog = None
        elif self.company_report:
            if (
                pressed[K_UP] or pressed[K_UP] or pressed[K_DOWN] or pressed[K_LEFT] or pressed[K_x] or pressed[K_z]
                or pressed[K_RSHIFT] or pressed[K_RETURN]
            ):
                self.company_report = None
        else:
            if pressed[K_UP]:
                self.move_hero('n')
            elif pressed[K_DOWN]:
                self.move_hero('s')
            elif pressed[K_RIGHT]:
                self.move_hero('e')
            elif pressed[K_LEFT]:
                self.move_hero('w')
            elif pressed[K_x]:
                self.map_menu = MapMenu(self.screen, self)
                pygame.key.set_repeat(300, 300)
            elif pressed[K_RSHIFT] and self.hero.velocity == [0,0]:
                company = self.game.game_state['company']
                money = self.game.game_state['money']
                food = int(math.ceil(self.game.game_state['food']))
                experience = self.game.game_state['experience']
                level = self.game.game_state['level']
                self.company_report = CompanyReport(company, money, food, experience, level)
            elif pressed[K_RETURN] and self.hero.velocity == [0,0]:
                self.game.open_pause_menu()
            else:
                self.move_hero(None)

    def get_opposite_direction(self, direction):
        return {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}[direction]

    def get_shop(self):
        pos = self.get_pos_in_front(self.hero.position, self.hero.direction)
        cell = self.cells.get(tuple(pos), {})
        return cell.get('shop')

    def get_dialog(self):
        pos = self.get_pos_in_front(self.hero.position, self.hero.direction)
        ai_sprite = self.ai_sprites.get(tuple(pos))
        if ai_sprite:
            ai_sprite.direction = self.get_opposite_direction(self.hero.direction)
            return self.game.get_dialog_for_condition(ai_sprite.dialog)
        return "There's no one there."

    def start_battle_after_dialog(
        self, enemies, battle_type, intro=None, exit=None, battle_name=None, narration=None, continue_music=False, offguard=None,
        next_battle=None,
    ):
        self.battle_after_dialog = {
            'enemies': enemies,
            'battle_type': battle_type,
            'intro': intro,
            'exit': exit,
            'narration': narration,
            'battle_name': battle_name,
            'continue_music': continue_music,
            'offguard': offguard,
            'next_battle': next_battle,
        }

    def attempt_explosive(self):
        cell = self.cells.get(tuple(self.hero.position), {})
        explosive_status = cell.get('explosive')
        if explosive_status == 'success':
            self.ready_explosion = True
            self.game.set_game_state_condition('exploded_wall')
        return explosive_status
