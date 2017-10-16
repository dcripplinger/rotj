# -*- coding: UTF-8 -*-

import json

from pygame.locals import *
import pyscroll
from pytmx.util_pygame import load_pygame

from helpers import get_map_filename
from hero import Hero
from sprite import AiSprite, Sprite


class Map(object):
    def __init__(self, screen, map_name, game, hero_position, direction='s'):
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
        self.load_ai_sprites()
        self.load_company_sprites(hero_position, direction)

    def load_ai_sprites(self):
        for cell in self.cells.values():
            ai_sprite_data = cell.get('ai_sprite')
            if ai_sprite_data:
                ai_sprite = AiSprite(
                    tmx_data=self.tmx_data, game=self.game, character=ai_sprite_data['name'], position=[cell['x'], cell['y']],
                    direction=ai_sprite_data['direction'], wander=ai_sprite_data['wander'], tiled_map=self,
                )
                self.group.add(ai_sprite)

    def load_company_sprites(self, hero_position, direction):
        company_sprites = self.get_company_sprite_names()
        if len(company_sprites) == 3:
            self.follower_two = Sprite(
                self.tmx_data, self.game, company_sprites[2], hero_position[:], direction=direction, tiled_map=self,
            )
            self.group.add(self.follower_two)
        else:
            self.follower_two = None
        if len(company_sprites) >= 2:
            self.follower_one = Sprite(
                self.tmx_data, self.game, company_sprites[1], hero_position[:], direction=direction, follower=self.follower_two,
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

    def update(self, dt):
        self.group.update(dt)

    def move_hero(self, direction):
        self.hero.move(direction)
        # followers get moved automatically through moving the leaders

    def handle_input(self, pressed):
        if pressed[K_UP]:
            self.move_hero('n')
        elif pressed[K_DOWN]:
            self.move_hero('s')
        elif pressed[K_RIGHT]:
            self.move_hero('e')
        elif pressed[K_LEFT]:
            self.move_hero('w')
        else:
            self.move_hero(None)
