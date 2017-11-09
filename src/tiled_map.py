# -*- coding: UTF-8 -*-

import json

import pygame
from pygame.locals import *
import pyscroll
from pytmx.util_pygame import load_pygame

from constants import ITEMS, NAMED_TELEPORTS
from helpers import get_map_filename
from hero import Hero
from report import Report
from sprite import AiSprite, Sprite
from text import create_prompt, MenuBox
from map_menu import MapMenu


class Map(object):
    def __init__(self, screen, map_name, game, hero_position, direction='s', followers='under', opening_dialog=None):
        self.name = map_name
        self.game = game
        self.ai_sprites = {} # key is position tuple, value is ai_sprite at that position currently
        map_filename = get_map_filename('{}.tmx'.format(map_name))
        json_filename = get_map_filename('{}.json'.format(map_name))
        self.screen = screen
        self.tmx_data = load_pygame(map_filename)
        with open(json_filename) as f:
            json_data = json.loads(f.read())
        self.cells = {(cell['x'], cell['y']): cell for cell in json_data}
        map_data = pyscroll.data.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(map_data, self.screen.get_size())
        self.map_layer.zoom = 1
        self.group = pyscroll.group.PyscrollGroup(map_layer=self.map_layer)
        self.opening_dialog = opening_dialog
        self.load_ai_sprites()
        self.hero = None
        self.follower_one = None
        self.follower_two = None
        self.load_company_sprites(hero_position, direction, followers)
        self.map_menu = None

    def set_game_state_condition(self, condition):
        self.game.set_game_state_condition(condition)
        if condition == 'ammah_and_manti_join':
            for sprite in self.group.sprites():
                if sprite.name in ['ammah', 'manti']:
                    self.group.remove(sprite)
            ai_sprites = {
                key: sprite for key, sprite in self.ai_sprites.items() if sprite.name not in ['ammah', 'manti']
            }
            self.ai_sprites = ai_sprites

    def try_toggle_equip_on_item(self, user, item_index):
        self.game.try_toggle_equip_on_item(user, item_index)

    def pass_item(self, user, recipient, item_index):
        self.game.pass_item(user, recipient, item_index)

    def heal(self, warlord, amount):
        self.game.heal(warlord, amount)

    def remove_item(self, warlord, index):
        self.game.remove_item(warlord, index)

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

    def check_for_item(self):
        cell = self.cells.get(tuple(self.hero.position))
        item = cell.get('item') if cell else None
        if not item or item['id'] in self.game.game_state['acquired_items']:
            return None
        self.game.add_to_inventory(item)
        return item['name']

    def load_ai_sprites(self):
        for cell in self.cells.values():
            ai_sprite_data = cell.get('ai_sprite')
            if ai_sprite_data and self.game.conditions_are_met(ai_sprite_data.get('conditions')):
                ai_sprite = AiSprite(
                    tmx_data=self.tmx_data, game=self.game, character=ai_sprite_data['name'],
                    position=[cell['x'], cell['y']], direction=ai_sprite_data['direction'],
                    wander=ai_sprite_data['wander'], tiled_map=self, dialog=ai_sprite_data['dialog'],
                )
                self.group.add(ai_sprite)

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
        company_sprites = self.get_company_sprite_names()
        if followers == 'inplace':
            follower_one_pos = self.follower_one.position if self.follower_one else None
            follower_two_pos = self.follower_two.position if self.follower_two else None
            follower_one_dir = self.follower_one.direction if self.follower_one else None
            follower_two_dir = self.follower_two.direction if self.follower_two else None
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
        if len(company_sprites) == 3:
            self.follower_two = Sprite(
                self.tmx_data, self.game, company_sprites[2], follower_two_pos, direction=follower_two_dir, tiled_map=self,
            )
            self.group.add(self.follower_two)
        else:
            self.follower_two = None
        if len(company_sprites) >= 2:
            self.follower_one = Sprite(
                self.tmx_data, self.game, company_sprites[1], follower_one_pos, direction=follower_one_dir,
                follower=self.follower_two, tiled_map=self,
            )
            self.group.add(self.follower_one)
        else:
            self.follower_one = None
        self.hero = Hero(
            self.tmx_data, self.game, company_sprites[0], hero_position[:], cells=self.cells, direction=direction,
            follower=self.follower_one, tiled_map=self,
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
        self.group.center(self.hero.rect.center)
        self.group.draw(self.screen)
        if self.map_menu:
            self.map_menu.draw()
        if self.opening_dialog:
            self.screen.blit(self.opening_dialog.surface, (0, 160))

    def update(self, dt):
        self.group.update(dt)
        if self.map_menu:
            self.map_menu.update(dt)
        if self.opening_dialog:
            self.opening_dialog.update(dt)

    def move_hero(self, direction):
        self.hero.move(direction)
        # followers get moved automatically through moving the leaders

    def handle_input(self, pressed):
        if self.opening_dialog:
            self.opening_dialog.handle_input(pressed)
            if pressed[K_x] and not self.opening_dialog.has_more_stuff_to_show():
                self.opening_dialog = None
        elif self.map_menu:
            action = self.map_menu.handle_input(pressed)
            if action == 'exit':
                self.map_menu = None
                pygame.key.set_repeat(50, 50)
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
            else:
                self.move_hero(None)

    def get_opposite_direction(self, direction):
        return {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}[direction]

    def get_dialog(self):
        pos = self.get_pos_in_front(self.hero.position, self.hero.direction)
        ai_sprite = self.ai_sprites.get(tuple(pos))
        if ai_sprite:
            ai_sprite.direction = self.get_opposite_direction(self.hero.direction)
            return self.game.get_dialog_for_condition(ai_sprite.dialog)
        cell = self.cells.get(tuple(pos))
        if cell:
            # this is for having to talk to a tile instead of a sprite, giving the appearance of talking over a counter.
            dialog = cell.get('dialog')
            if dialog:
                return self.game.get_dialog_for_condition(dialog)
        return "There's no one there."
