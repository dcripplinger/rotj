# -*- coding: UTF-8 -*-

import json

import pygame
from pygame.locals import *
import pyscroll
from pytmx.util_pygame import load_pygame

from helpers import get_map_filename
from hero import Hero
from sprite import AiSprite, Sprite
from text import MenuBox


class MapMenu(object):
    def __init__(self, screen):
        self.screen = screen
        self.current_text_box = MenuBox(['TALK', 'CHECK', 'FORMATION', 'GENERAL', 'ITEM'], title='Command')
        self.current_text_box.focus()

    def update(self, dt):
        self.current_text_box.update(dt)

    def draw(self):
        self.screen.blit(self.current_text_box.surface, (160, 0))

    def handle_input(self, pressed):
        self.current_text_box.handle_input(pressed)
        if pressed[K_z]:
            return 'exit'


class Map(object):
    def __init__(self, screen, map_name, game, hero_position, direction='s', followers='under', dialog=None):
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
        self.dialog = dialog
        self.load_ai_sprites()
        self.load_company_sprites(hero_position, direction, followers)
        self.map_menu = None

    def load_ai_sprites(self):
        for cell in self.cells.values():
            ai_sprite_data = cell.get('ai_sprite')
            if ai_sprite_data:
                ai_sprite = AiSprite(
                    tmx_data=self.tmx_data, game=self.game, character=ai_sprite_data['name'], position=[cell['x'], cell['y']],
                    direction=ai_sprite_data['direction'], wander=ai_sprite_data['wander'], tiled_map=self,
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

    def load_company_sprites(self, hero_position, direction, followers):
        company_sprites = self.get_company_sprite_names()
        follower_one_pos = self.get_pos_behind(hero_position, direction) if followers == 'trail' else hero_position[:]
        follower_two_pos = self.get_pos_behind(follower_one_pos, direction) if followers == 'trail' else hero_position[:]
        if len(company_sprites) == 3:
            self.follower_two = Sprite(
                self.tmx_data, self.game, company_sprites[2], follower_two_pos, direction=direction, tiled_map=self,
            )
            self.group.add(self.follower_two)
        else:
            self.follower_two = None
        if len(company_sprites) >= 2:
            self.follower_one = Sprite(
                self.tmx_data, self.game, company_sprites[1], follower_one_pos, direction=direction, follower=self.follower_two,
                tiled_map=self,
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
        if self.dialog:
            self.screen.blit(self.dialog.surface, (0, 160))

    def update(self, dt):
        self.group.update(dt)
        if self.map_menu:
            self.map_menu.update(dt)
        if self.dialog:
            self.dialog.update(dt)

    def move_hero(self, direction):
        self.hero.move(direction)
        # followers get moved automatically through moving the leaders

    def handle_input(self, pressed):
        if self.dialog:
            self.dialog.handle_input(pressed)
            if pressed[K_x] and not self.dialog.has_more_stuff_to_show():
                self.dialog = None
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
                self.map_menu = MapMenu(self.screen)
                pygame.key.set_repeat(300, 300)
            else:
                self.move_hero(None)
