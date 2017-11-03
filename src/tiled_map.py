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
        self.order_menu = None
        self.new_order = None
        self.order_indices = []
        self.strat_menu = None
        self.general_menu = None
        self.report = None
        self.items_menu = None
        self.item_selected_menu = None
        self.recipient_menu = None
        self.city_menu = None

    def update(self, dt):
        if self.state == 'main':
            self.main_menu.update(dt)
        if self.state in ['talk', 'check', 'confirm_strat', 'empty', 'item_prompt']:
            self.prompt.update(dt)
        if self.state == 'formation':
            self.formation_menu.update(dt)
        if self.state == 'order':
            self.order_menu.update(dt)
            self.new_order.update(dt)
        if self.state in ['strat', 'confirm_strat', 'item']:
            self.strat_menu.update(dt)
        if self.state == 'general':
            self.general_menu.update(dt)
        if self.state == 'items':
            self.items_menu.update(dt)
        if self.state == 'item_selected':
            self.item_selected_menu.update(dt)
        if self.state == 'recipient':
            self.recipient_menu.update(dt)
        if self.state == 'city':
            self.city_menu.update(dt)

    def draw(self):
        if self.main_menu:
            self.screen.blit(self.main_menu.surface, (160, 0))
        if self.prompt:
            self.screen.blit(self.prompt.surface, (0, 160))
        if self.formation_menu:
            self.screen.blit(self.formation_menu.surface, (160, 128))
        if self.new_order:
            self.screen.blit(self.new_order.surface, (128, 0))
        if self.order_menu:
            self.screen.blit(self.order_menu.surface, (0, 0))
        if self.strat_menu:
            self.screen.blit(self.strat_menu.surface, (0, 0))
        if self.general_menu:
            self.screen.blit(self.general_menu.surface, (0, 0))
        if self.report:
            self.screen.blit(self.report.surface, (0, 0))
        if self.items_menu:
            self.screen.blit(self.items_menu.surface, (64, 0))
        if self.item_selected_menu:
            self.screen.blit(self.item_selected_menu.surface, (176, 128))
        if self.recipient_menu:
            self.screen.blit(self.recipient_menu.surface, (144, 0))
        if self.city_menu:
            self.screen.blit(self.city_menu.surface, (160, 0))

    def handle_input_main(self, pressed):
        self.main_menu.handle_input(pressed)
        if pressed[K_z]:
            return 'exit'
        elif pressed[K_x]:
            self.select_sound.play()
            choice = self.main_menu.get_choice()
            if choice == 'TALK':
                self.handle_talk()
            elif choice == 'CHECK':
                self.handle_check()
            elif choice == 'FORMATION':
                self.handle_formation()
            elif choice == 'GENERAL':
                self.handle_general()
            elif choice == 'ITEM':
                self.handle_item()

    def handle_item(self):
        self.state = 'item'
        self.main_menu.unfocus()
        self.strat_menu = MenuBox(self.map.get_company_names())
        self.strat_menu.focus()    

    def handle_general(self):
        self.general_menu = MenuBox(self.map.get_company_names())
        self.main_menu.unfocus()
        self.general_menu.focus()
        self.state = 'general'

    def handle_input(self, pressed):
        if self.state == 'main':
            return self.handle_input_main(pressed)
        elif self.state in ['talk', 'check', 'confirm_strat', 'item_prompt']:
            self.prompt.handle_input(pressed)
            if (pressed[K_x] or pressed[K_z]) and not self.prompt.has_more_stuff_to_show():
                return 'exit'
        elif self.state == 'formation':
            return self.handle_input_formation(pressed)
        elif self.state == 'order':
            return self.handle_input_order(pressed)
        elif self.state == 'strat':
            return self.handle_input_strat(pressed)
        elif self.state == 'general':
            return self.handle_input_general(pressed)
        elif self.state == 'report':
            if pressed[K_x] or pressed[K_z]:
                return 'exit'
        elif self.state == 'item':
            return self.handle_input_item(pressed)
        elif self.state == 'empty':
            return self.handle_input_empty(pressed)
        elif self.state == 'items':
            return self.handle_input_items(pressed)
        elif self.state == 'item_selected':
            return self.handle_input_item_selected(pressed)
        elif self.state == 'recipient':
            return self.handle_input_recipient(pressed)
        elif self.state == 'city':
            return self.handle_input_city(pressed)

    def handle_input_city(self, pressed):
        self.city_menu.handle_input(pressed)
        if pressed[K_z]:
            self.city_menu = None
            self.state = 'item_selected'
            self.item_selected_menu.focus()
        elif pressed[K_x]:
            self.select_sound.play()
            self.map.teleport(self.city_menu.get_choice().lower())
            return 'exit'

    def handle_input_recipient(self, pressed):
        self.recipient_menu.handle_input(pressed)
        if pressed[K_z]:
            self.recipient_menu = None
            self.state = 'item_selected'
            self.item_selected_menu.focus()
        elif pressed[K_x]:
            self.select_sound.play()

    def handle_input_item_selected(self, pressed):
        self.item_selected_menu.handle_input(pressed)
        if pressed[K_z]:
            self.item_selected_menu = None
            self.items_menu.focus()
            self.state = 'items'
        elif pressed[K_x]:
            self.select_sound.play()
            choice = self.item_selected_menu.get_choice()
            if choice == 'USE':
                self.handle_use()

    def handle_use(self):
        self.item_selected_menu.unfocus()
        item_name = self.items_menu.get_choice().lower()
        map_usage = ITEMS[item_name].get('map_usage')
        if map_usage == 'company':
            self.state = 'recipient'
            self.recipient_menu = MenuBox(self.map.get_company_names())
            self.recipient_menu.focus()
        elif map_usage == 'city':
            self.state = 'city'
            self.city_menu = MenuBox(self.map.get_teleport_cities())
            self.city_menu.focus()
        elif map_usage == 'map':
            self.state = 'item_prompt'
            warlord = self.strat_menu.get_choice().title()
            self.prompt = create_prompt("{} used {}. But nothing happened.".format(warlord, item_name.title()))
        else:
            self.state = 'item_prompt'
            self.prompt = create_prompt("That can't be used here.")

    def handle_input_empty(self, pressed):
        if pressed[K_x]:
            return 'exit'
        elif pressed[K_z]:
            self.prompt = None
            self.strat_menu.focus()
            self.state = 'item'

    def handle_input_item(self, pressed):
        self.strat_menu.handle_input(pressed)
        if pressed[K_z]:
            self.strat_menu = None
            self.main_menu.focus()
            self.state = 'main'
        elif pressed[K_x]:
            self.select_sound.play()
            warlord = self.strat_menu.get_choice()
            items = self.map.get_items(warlord)
            if not items:
                self.state = 'empty'
                self.strat_menu.unfocus()
                self.prompt = create_prompt(u"{} doesn't have anything.".format(warlord))
            else:
                self.state = 'items'
                self.strat_menu.unfocus()
                self.items_menu = MenuBox(
                    [u"{}{}".format(('*' if item.get('equipped') else ''), item['name'].title()) for item in items]
                )
                self.items_menu.focus()

    def handle_input_items(self, pressed):
        self.items_menu.handle_input(pressed)
        if pressed[K_z]:
            self.items_menu = None
            self.strat_menu.focus()
            self.state = 'item'
        elif pressed[K_x]:
            self.select_sound.play()
            self.item_selected_menu = MenuBox(['USE', 'PASS', 'EQUIP', 'DROP'])
            self.state = 'item_selected'
            self.items_menu.unfocus()
            self.item_selected_menu.focus()

    def handle_input_general(self, pressed):
        self.general_menu.handle_input(pressed)
        if pressed[K_z]:
            self.general_menu = None
            self.main_menu.focus()
            self.state = 'main'
        elif pressed[K_x]:
            self.select_sound.play()
            choice = self.general_menu.get_choice().lower()
            self.state = 'report'
            self.report = Report(choice, self.map.get_level(), self.map.get_equips(choice))
            self.general_menu = None
            self.main_menu = None

    def handle_input_strat(self, pressed):
        self.strat_menu.handle_input(pressed)
        if pressed[K_z]:
            self.strat_menu = None
            self.formation_menu.focus()
            self.state = 'formation'
        elif pressed[K_x]:
            self.select_sound.play()
            choice = self.strat_menu.get_choice(strip_star=False)
            if choice.startswith(u'★'):
                choice = choice[1:]
                already_tactician = True
            else:
                already_tactician = False
            if already_tactician:
                self.map.retire_tactician(choice)
                self.strat_menu.remove_stars()
                text = "{} resigned as tactician.".format(choice.title())
            else:
                success = self.map.try_set_tactician(choice)
                if success:
                    self.strat_menu.remove_stars()
                    self.strat_menu.choices[self.strat_menu.current_choice] = u"★" + self.strat_menu.get_choice()
                    text = "{} is the acting tactician.".format(choice.title())
                else:
                    text = "{} can't be a tactician.".format(choice.title())
            self.prompt = create_prompt(text)
            self.state = 'confirm_strat'
            self.strat_menu.create_text_box(None, None, None)
            self.strat_menu.unfocus()

    def handle_input_formation(self, pressed):
        self.formation_menu.handle_input(pressed)
        if pressed[K_z]:
            self.formation_menu = None
            self.state = 'main'
            self.main_menu.focus()
        elif pressed[K_x]:
            self.select_sound.play()
            choice = self.formation_menu.get_choice()
            if choice == 'ORDER':
                self.handle_order()
            elif choice == 'STRAT.':
                self.handle_strat()

    def handle_input_order(self, pressed):
        self.order_menu.handle_input(pressed)
        if pressed[K_z]:
            if len(self.new_order.choices) == 0:
                self.state = 'formation'
                self.formation_menu.focus()
                self.order_menu = None
                self.new_order = None
            else:
                warlord = self.new_order.choices.pop()
                self.order_menu.choices.insert(self.order_indices.pop(), warlord)
        elif pressed[K_x]:
            self.select_sound.play()
            choice_with_star = self.order_menu.get_choice(strip_star=False)
            index = self.order_menu.current_choice
            if choice_with_star:
                self.order_menu.choices.remove(choice_with_star)
                if self.order_menu.current_choice == len(self.order_menu.choices):
                    self.order_menu.current_choice = max(0, self.order_menu.current_choice-1)
                self.new_order.choices.append(choice_with_star)
                self.order_indices.append(index)
            else:
                self.map.update_company_order([choice.lower() for choice in self.new_order.get_choices()])
                return 'exit'

    def handle_order(self):
        self.state = 'order'
        self.formation_menu.unfocus()
        self.order_menu = MenuBox(self.map.get_company_names())
        self.order_menu.focus()
        self.new_order = MenuBox([], width=self.order_menu.get_width(), height=self.order_menu.get_height())

    def handle_strat(self):
        self.state = 'strat'
        self.formation_menu.unfocus()
        self.strat_menu = MenuBox(self.map.get_company_names())
        self.strat_menu.focus()

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
        self.hero = None
        self.follower_one = None
        self.follower_two = None
        self.load_company_sprites(hero_position, direction, followers)
        self.map_menu = None

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

    def get_company_names(self):
        return self.game.get_company_names()

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
            return ai_sprite.dialog
        cell = self.cells.get(tuple(pos))
        if cell:
            # this is for having to talk to a tile instead of a sprite, giving the appearance of talking over a counter.
            dialog = cell.get('dialog')
            if dialog:
                return dialog
        return "There's no one there."
