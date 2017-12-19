# -*- coding: UTF-8 -*-

import math

import pygame
from pygame.locals import *

from constants import GAME_HEIGHT, GAME_WIDTH, MAX_NUM
from helpers import get_max_soldiers
from text import create_prompt, MenuBox, ShopMenu, TextBox


class Shop(object):
    def __init__(self, shop, game):
        self.shop = shop
        self.game = game
        self.surface = None
        self.state = 'dialog' # One of dialog, shop_menu, exit, sleep, company_menu, confirm
        self.company_menu = None # When not None, will be MenuBox(self.game.get_company_names())
        self.shop_menu = None # an instance of ShopMenu
        self.confirm_menu = None # an instance of MenuBox(['YES', 'NO'])
        self.spoils_box = None # This is sometimes instantiated via self.create_spoils_box()
        self.misc_menu = None # This is a MenuBox whenever it is needed
        self.sleep_music = None # Needs to be the path to the sleep sound byte, which could be None or a save sound byte or whatever

        # The following should be set by the inheriting class's init
        self.next = None # indicates the next state when a dialog finishes, use one of its valid values
        self.dialog = None # set using create_prompt()

    def update(self, dt):
        if self.state == 'dialog':
            self.dialog.update(dt)
            if not self.dialog.has_more_stuff_to_show():
                self.transition_state()
        elif self.state == 'shop_menu':
            self.shop_menu.update(dt)
        elif self.state == 'company_menu':
            self.company_menu.update(dt)
        elif self.state == 'confirm':
            self.confirm_menu.update(dt)
        elif self.state == 'misc_menu':
            self.misc_menu.update(dt)

    def transition_state(self):
        self.dialog.shutdown()
        self.state = self.next
        self.next = None
        if self.state == 'shop_menu':
            self.create_shop_menu()
            self.shop_menu.focus()
            self.create_spoils_box()
        elif self.state == 'sleep':
            self.game.start_sleep(self.sleep_music, self.sleep_dialog)
        elif self.state == 'company_menu':
            self.company_menu = MenuBox(self.game.get_company_names())
            self.company_menu.focus()
        elif self.state == 'confirm':
            self.confirm_menu = MenuBox(['YES', 'NO'])
            self.create_spoils_box()
            self.confirm_menu.focus()
        elif self.state == 'misc_menu':
            self.create_misc_menu()
            self.misc_menu.focus()

    def update_surface(self):
        self.surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT)).convert_alpha()
        self.surface.fill((0,0,0,0))
        if self.dialog:
            self.surface.blit(self.dialog.surface, (0, 160))
        if self.shop_menu:
            self.surface.blit(self.shop_menu.surface, (0, 0))
        if self.company_menu:
            self.surface.blit(self.company_menu.surface, (128, 0))
        if self.misc_menu:
            self.surface.blit(self.misc_menu.surface, (160, 160))
        if self.confirm_menu:
            self.surface.blit(self.confirm_menu.surface, (160, 160))
        if self.spoils_box:
            self.surface.blit(self.spoils_box.surface, (160, 104))

    def create_spoils_box(self):
        money = self.game.game_state['money']
        food = self.game.game_state['food']
        text = "MONEY\n{:~>9}\nFOOD\n{:~>9}".format(money, food)
        self.spoils_box = TextBox(text, border=True, indent=1)

    def handle_input(self, pressed):
        if self.state == 'dialog':
            self.dialog.handle_input(pressed)
        elif self.state == 'shop_menu':
            self.shop_menu.handle_input(pressed)
            if pressed[K_x]:
                self.handle_shop_menu_selection()
            elif pressed[K_z]:
                self.handle_shop_menu_cancel()
        elif self.state == 'company_menu':
            self.company_menu.handle_input(pressed)
            if pressed[K_x]:
                self.handle_company_menu_selection()
            elif pressed[K_z]:
                self.handle_company_menu_cancel()
        elif self.state == 'confirm':
            self.confirm_menu.handle_input(pressed)
            if pressed[K_x] and self.confirm_menu.get_choice() == 'YES':
                self.handle_confirm_yes()
            elif pressed[K_z] or (pressed[K_x] and self.confirm_menu.get_choice() == 'NO'):
                self.handle_confirm_no()
        elif self.state == 'misc_menu':
            self.misc_menu.handle_input(pressed)
            if pressed[K_x]:
                self.handle_misc_menu(self.misc_menu.get_choice())
            elif pressed[K_z]:
                self.handle_misc_menu(None)
        elif self.state == 'exit':
            if pressed[K_x] or pressed[K_z]:
                return 'exit'

    def handle_shop_menu_selection(self):
        raise NotImplementedError

    def handle_shop_menu_cancel(self):
        raise NotImplementedError

    def handle_company_menu_selection(self):
        raise NotImplementedError

    def handle_company_menu_cancel(self):
        raise NotImplementedError

    def handle_confirm_yes(self):
        raise NotImplementedError

    def handle_confirm_no(self):
        raise NotImplementedError

    def handle_misc_menu(self, choice):
        raise NotImplementedError

    def create_misc_menu(self):
        raise NotImplementedError

    def create_shop_menu(self):
        self.shop_menu = ShopMenu(self.shop['items'])


class RecordOffice(Shop):
    def __init__(self, shop, game):
        super(RecordOffice, self).__init__(shop, game)
        leader = self.game.get_leader()['name'].title()
        self.dialog = create_prompt("Good morning, {} sir. What can I do for you today?".format(leader))
        self.next = 'misc_menu'

    def handle_misc_menu(self, choice):
        self.misc_menu.unfocus()
        self.state = 'dialog'
        if choice is None:
            self.dialog = create_prompt("Yes my lord.")
            self.next = 'exit'
        elif choice == 'RECORD':
            self.dialog = create_prompt("Shall I record the result of today's battles?")
            self.next = 'confirm'
        elif choice == 'SET~HQ':
            msg = self.game.try_set_hq()
            if not msg:
                self.dialog = create_prompt("OK.")
                self.next = 'sleep'
                self.sleep_dialog = "This city is now your base of operations."

    def handle_confirm_yes(self):
        self.confirm_menu.unfocus()
        self.game.save()
        self.game.start_sleep('data/audio/save.wav', "I have recorded your status.")

    def handle_confirm_no(self):
        self.misc_menu.unfocus()
        self.state = 'dialog'
        self.dialog = create_prompt("Yes my lord.")
        self.next = 'exit'

    def create_misc_menu(self):
        self.misc_menu = MenuBox(['RECORD', 'SET~HQ'])


class Inn(Shop):
    def __init__(self, shop, game):
        super(Inn, self).__init__(shop, game)
        self.cost = sum(self.shop['cost'] for warlord in self.game.game_state['company'] if warlord['soldiers'] > 0)
        self.dialog = create_prompt(
            "Welcome! You may stay here for {} senines per night. Shall I prepare your room?".format(self.cost)
        )
        self.next = 'confirm'
        self.sleep_music = 'data/audio/music/sleep.wav'
        self.sleep_dialog = "Good morning. I hope you rested well."

    def handle_confirm_yes(self):
        self.confirm_menu = None
        self.state = 'dialog'
        new_balance = self.game.game_state['money'] - self.cost
        if new_balance < 0:
            self.dialog = create_prompt("I'm sorry. You don't have enough money.")
            self.next = 'exit'
        else:
            self.dialog = create_prompt("Good night.")
            self.next = 'sleep'
            self.game.update_game_state({'money': new_balance})
            self.create_spoils_box()

    def handle_confirm_no(self):
        self.confirm_menu = None
        self.state = 'dialog'
        self.next = 'exit'
        self.dialog = create_prompt("OK. But you won't find anything cheaper.")


class FoodShop(Shop):
    def __init__(self, shop, game):
        super(FoodShop, self).__init__(shop, game)
        self.dialog = create_prompt("Welcome. May I sell you some provisions?")
        self.next = 'shop_menu'

    def create_shop_menu(self):
        level = self.game.game_state['level']
        company = self.game.game_state['company']
        sum_soldiers = sum(get_max_soldiers(warlord['name'], level) for warlord in company)
        base = int(math.pow(10, len(str(sum_soldiers))-1))
        self.shop_menu = ShopMenu([
            {'name': str(3*base), 'cost': base},
            {'name': str(30*base), 'cost': 10*base},
            {'name': str(300*base), 'cost': 100*base},
        ])

    def handle_shop_menu_selection(self):
        self.state = 'dialog'
        item = self.shop_menu.get_choice()
        if item['cost'] > self.game.game_state['money']:
            self.dialog = create_prompt("Do you think I'm running a charity here? Come back when you have enough money.")
            self.next = 'exit'
        else:
            self.dialog = create_prompt("Thank you.")
            self.next = 'exit'
            self.game.update_game_state({
                'money': self.game.game_state['money'] - item['cost'],
                'food': min(MAX_NUM, self.game.game_state['food'] + int(item['name'])),
            })
            self.create_spoils_box()
        self.shop_menu.unfocus()

    def handle_shop_menu_cancel(self):
        self.state = 'dialog'
        self.dialog = create_prompt("OK, come back any time.")
        self.next = 'exit'
        self.shop_menu = None


class Armory(Shop):
    def __init__(self, shop, game):
        super(Armory, self).__init__(shop, game)
        self.dialog = create_prompt("Welcome. I have many fine weapons. What can I sell you?")
        self.next = 'shop_menu'


class MerchantShop(Shop):
    def __init__(self, shop, game):
        super(MerchantShop, self).__init__(shop, game)


class Reserve(Shop):
    def __init__(self, shop, game):
        super(Reserve, self).__init__(shop, game)


def create_shop(shop, game):
    t = shop['type']
    if t == 'record_office':
        return RecordOffice(shop, game)
    elif t == 'inn':
        return Inn(shop, game)
    elif t == 'food':
        return FoodShop(shop, game)
    elif t == 'armory':
        return Armory(shop, game)
    elif t == 'merchant':
        return MerchantShop(shop, game)
    elif t == 'reserve':
        return Reserve(shop, game)
