# -*- coding: UTF-8 -*-

import json

import pygame
from pygame.locals import *
import pyscroll
from pytmx.util_pygame import load_pygame

from helpers import get_map_filename
from hero import Hero
from sprite import AiSprite, Sprite
from text import create_prompt, MenuBox


class MapMenu(object):
    def __init__(self, screen, tiled_map):
        self.screen = screen
        self.main_menu = MenuBox(['TALK', 'CHECK', 'FORMATION', 'GENERAL', 'ITEM'], title='Command')
        self.main_menu.focus()
        self.select_sound = pygame.mixer.Sound('data/audio/select.wav')
        self.select_sound.play()
        self.state = 'main'
        self.prompt = None
        self.map = tiled_map
        self.formation_menu = None

    def update(self, dt):
        self.main_menu.update(dt)
        if self.state in ['talk', 'check']:
            self.prompt.update(dt)
        if self.state == 'formation':
            self.formation_menu.update(dt)

    def draw(self):
        self.screen.blit(self.main_menu.surface, (160, 0))
        if self.prompt:
            self.screen.blit(self.prompt.surface, (0, 160))
        if self.formation_menu:
            self.screen.blit(self.formation_menu.surface, (160, 128))

    def handle_input(self, pressed):
        if self.state == 'main':
            self.main_menu.handle_input(pressed)
            if pressed[K_z]:
                return 'exit'
            elif pressed[K_x]:
                choice = self.main_menu.get_choice()
                if choice == 'TALK':
                    self.handle_talk()
                elif choice == 'CHECK':
                    self.handle_check()
                elif choice == 'FORMATION':
                    self.handle_formation()
        elif self.state in ['talk', 'check']:
            self.prompt.handle_input(pressed)
            if (pressed[K_x] or pressed[K_z]) and not self.prompt.has_more_stuff_to_show():
                return 'exit'
        elif self.state == 'formation':
            self.formation_menu.handle_input(pressed)
            if pressed[K_z]:
                self.formation_menu = None
                self.state = 'main'
                self.main_menu.focus()

    def handle_talk(self):
        self.prompt = create_prompt(self.map.get_dialog())
        self.state = 'talk'
        self.main_menu.unfocus()

    def handle_check(self):
        item = self.map.check_for_item()
        text = "{} searched. ".format(self.map.hero.name.title()) + ("{} found.".format(item) if item else "But found nothing.")
        self.prompt = create_prompt(text)
        self.state = 'check'
        self.main_menu.unfocus()

    def handle_formation(self):
        self.formation_menu = MenuBox(['ORDER', 'STRAT.'])
        self.formation_menu.focus()
        self.main_menu.unfocus()
        self.state = 'formation'


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
        self.load_company_sprites(hero_position, direction, followers)
        self.map_menu = None

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
            if ai_sprite_data:
                ai_sprite = AiSprite(
                    tmx_data=self.tmx_data, game=self.game, character=ai_sprite_data['name'], position=[cell['x'], cell['y']],
                    direction=ai_sprite_data['direction'], wander=ai_sprite_data['wander'], tiled_map=self,
                    dialog=ai_sprite_data['dialog'],
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
            return ai_sprite.dialog
        cell = self.cells.get(tuple(pos))
        if cell:
            # this is for having to talk to a tile instead of a sprite, giving the appearance of talking over a counter.
            dialog = cell.get('dialog')
            if dialog:
                return dialog
        return "There's no one there."
