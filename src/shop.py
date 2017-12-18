# -*- coding: UTF-8 -*-

import pygame
from pygame.locals import *

from constants import GAME_HEIGHT, GAME_WIDTH
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

    def transition_state(self):
        self.dialog.shutdown()
        self.state = self.next
        self.next = None
        if self.state == 'shop_menu':
            self.shop_menu = ShopMenu(self.shop['items'])
            self.shop_menu.focus()
        elif self.state == 'sleep':
            self.game.start_sleep()
        elif self.state == 'company_menu':
            self.company_menu = MenuBox(self.game.get_company_names())
            self.company_menu.focus()
        elif self.state == 'confirm':
            self.confirm_menu = MenuBox(['YES', 'NO'])
            self.create_spoils_box()
            self.confirm_menu.focus()

    def update_surface(self):
        self.surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT)).convert_alpha()
        self.surface.fill((0,0,0,0))
        if self.dialog:
            self.surface.blit(self.dialog.surface, (0, 160))
        if self.shop_menu:
            self.surface.blit(self.shop_menu.surface, (0, 0))
        if self.company_menu:
            self.surface.blit(self.company_menu.surface, (128, 0))
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


class RecordOffice(Shop):
    def __init__(self, shop, game):
        super(RecordOffice, self).__init__(shop, game)


class Inn(Shop):
    def __init__(self, shop, game):
        super(Inn, self).__init__(shop, game)
        self.cost = sum(self.shop['cost'] for warlord in self.game.game_state['company'] if warlord['soldiers'] > 0)
        self.dialog = create_prompt(
            "Welcome! You may stay here for {} senines per night. Shall I prepare your room?".format(self.cost)
        )
        self.next = 'confirm'

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
