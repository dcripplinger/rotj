# -*- coding: UTF-8 -*-

import math

import pygame
from pygame.locals import *

from constants import EXP_REQUIRED_BY_LEVEL, GAME_HEIGHT, GAME_WIDTH, ITEMS, MAX_ITEMS_PER_PERSON, MAX_NUM
from helpers import get_max_soldiers
from report import Report
from text import create_prompt, MenuBox, ShopMenu, TextBox

WARLORDS_EXEMPT_FROM_FIRING = {
    'moroni',
    'amalickiah',
    'teancum',
    'lachoneus',
    'nephi',
    'samuel',
    'gidgiddoni',
    'lehi',
    'helaman',
    'moronihah',
    'pahoran',
    'corianton',
}


class Shop(object):
    def __init__(self, shop, game):
        self.company_menu_type = None
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
        self.report = None
        self.select_sound = pygame.mixer.Sound('data/audio/select.wav')
        self.heal = False

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
            self.game.start_sleep(self.sleep_music, self.sleep_dialog, self.heal)
        elif self.state == 'company_menu':
            self.create_company_menu()
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
        if self.misc_menu:
            if len(self.misc_menu.get_choices()) > 4:
                self.surface.blit(self.misc_menu.surface, (160, 128))
            else:
                self.surface.blit(self.misc_menu.surface, (160, 160))
        if self.confirm_menu:
            self.surface.blit(self.confirm_menu.surface, (160, 160))
        if self.spoils_box:
            self.surface.blit(self.spoils_box.surface, (160, 104))
        if self.company_menu:
            self.surface.blit(self.company_menu.surface, (128, 0))
        if self.report:
            self.surface.blit(self.report.surface, (0,0))

    def create_spoils_box(self):
        money = self.game.game_state['money']
        food = int(math.ceil(self.game.game_state['food']))
        text = u"MONEY\n{:~>9}\nFOOD\n{:~>9}".format(money, food)
        self.spoils_box = TextBox(text, border=True, indent=1)

    def handle_input(self, pressed):
        if self.report:
            if pressed[K_x] or pressed[K_z]:
                self.report = None
                self.company_menu.focus()
        elif self.state == 'dialog':
            self.dialog.handle_input(pressed)
        elif self.state == 'shop_menu':
            self.shop_menu.handle_input(pressed)
            if pressed[K_x]:
                self.select_sound.play()
                self.handle_shop_menu_selection()
            elif pressed[K_z]:
                self.handle_shop_menu_cancel()
        elif self.state == 'company_menu':
            self.company_menu.handle_input(pressed)
            if pressed[K_x]:
                self.select_sound.play()
                self.handle_company_menu_selection()
            elif pressed[K_z]:
                self.handle_company_menu_cancel()
        elif self.state == 'confirm':
            self.confirm_menu.handle_input(pressed)
            if pressed[K_x] and self.confirm_menu.get_choice() == 'YES':
                self.select_sound.play()
                self.handle_confirm_yes()
            elif pressed[K_z] or (pressed[K_x] and self.confirm_menu.get_choice() == 'NO'):
                self.handle_confirm_no()
        elif self.state == 'misc_menu':
            self.misc_menu.handle_input(pressed)
            if pressed[K_x]:
                self.select_sound.play()
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

    def create_company_menu(self):
        if self.company_menu_type == 'buying':
            self.company_menu = MenuBox(self.game.get_company_names(with_empty_item_slots=True))
        elif self.company_menu_type == 'selling':
            self.company_menu = MenuBox(self.game.get_company_names(with_items=True))
        else:
            self.company_menu = MenuBox(self.game.get_company_names())


class RecordOffice(Shop):
    def __init__(self, shop, game):
        super(RecordOffice, self).__init__(shop, game)
        leader = self.game.get_leader()['name'].title()
        self.dialog = create_prompt(u"Good morning, {} sir. What can I do for you today?".format(leader))
        self.next = 'misc_menu'

    def handle_misc_menu(self, choice):
        self.misc_menu.unfocus()
        self.state = 'dialog'
        if choice is None:
            self.dialog = create_prompt("Yes my lord.")
            self.next = 'exit'
        elif choice == 'RECORD':
            current_level = self.game.game_state['level']
            if current_level >= 90:
                prompt_text = (
                    "You have reached the highest level of experience. Shall I record the result of today's battles?"
                )
            else:
                total_exp_required = EXP_REQUIRED_BY_LEVEL.get(current_level + 1)
                net_exp_required = total_exp_required - self.game.game_state['experience']
                prompt_text = (
                    u'You need {} experience points to advance to the next level. '
                    u'Shall I record your current status?'
                ).format(net_exp_required)
            self.dialog = create_prompt(prompt_text)
            self.next = 'confirm'
        elif choice == 'SET~HQ':
            msg = self.game.try_set_hq()
            if not msg:
                self.dialog = create_prompt("OK.")
                self.next = 'sleep'
                self.sleep_dialog = "This city is now your base of operations."
            else:
                self.dialog = create_prompt(msg)
                self.next = 'exit'

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
            u"Welcome! You may stay here for {} senines per night. Shall I prepare your room?".format(self.cost)
        )
        self.next = 'confirm'
        self.sleep_music = 'data/audio/music/sleep.wav'
        self.sleep_dialog = "Good morning. I hope you rested well."
        self.heal = True

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
        money = self.game.game_state['money']
        sum_soldiers = sum(get_max_soldiers(warlord['name'], level, is_ally=True) for warlord in company)
        exponent = max(0, len(str(sum_soldiers)) - 3)
        affordable_exponent = max(0, len(str(money)) - 3)
        exponent = min(affordable_exponent, min(5, exponent))
        base = int(math.pow(10, exponent))
        self.shop_menu = ShopMenu([
            {'name': str(base), 'cost': base},
            {'name': str(10*base), 'cost': 10*base},
            {'name': str(100*base), 'cost': 100*base},
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

    def handle_shop_menu_selection(self):
        self.state = 'dialog'
        item = self.shop_menu.get_choice()
        if item['cost'] > self.game.game_state['money']:
            self.dialog = create_prompt("I'm sorry. You don't have enough money for that. Anything else?")
            self.next = 'shop_menu'
        elif len(self.game.get_company_names(with_empty_item_slots=True)) == 0:
            self.dialog = create_prompt("I'm sorry. You don't have any room to carry more items. Anything else?")
            self.next = 'shop_menu'
        else:
            self.dialog = create_prompt("And who will be carrying that?")
            self.company_menu_type = 'buying'
            self.next = 'company_menu'
            self.create_spoils_box()
        self.shop_menu.unfocus()

    def handle_shop_menu_cancel(self):
        self.state = 'dialog'
        self.dialog = create_prompt("Well, when I can help you, you know where I am.")
        self.next = 'exit'
        self.shop_menu = None

    def handle_company_menu_selection(self):
        self.company_menu.unfocus()
        self.state = 'dialog'
        warlord_name = self.company_menu.get_choice() # leave it capitalized
        warlord_name_lower = warlord_name.lower()
        for warlord_index, warlord in enumerate(self.game.game_state['company']):
            if warlord['name'] == warlord_name_lower:
                break
        current_items = warlord['items']
        if len(current_items) >= MAX_ITEMS_PER_PERSON:
            self.next = 'company_menu'
            self.dialog = create_prompt(u"{} can't carry any more. Who will be carrying that?".format(warlord_name))
            self.company_menu_type = 'buying'
        else:
            self.next = 'shop_menu'
            self.dialog = create_prompt("Thank you. Anything else?")
            self.company_menu = None
            item = self.shop_menu.get_choice()
            self.game.add_to_inventory(item['name'], warlord_index)
            self.game.update_game_state({'money': self.game.game_state['money'] - item['cost']})

    def handle_company_menu_cancel(self):
        self.state = 'dialog'
        self.next = 'shop_menu'
        self.dialog = create_prompt("What can I sell you?")
        self.company_menu = None


class MerchantShop(Shop):
    def __init__(self, shop, game):
        super(MerchantShop, self).__init__(shop, game)
        self.dialog = create_prompt("Come in, come in. I'm a merchant. Are you buying or selling?")
        self.next = 'misc_menu'

    def create_misc_menu(self):
        self.misc_menu = MenuBox(['BUY', 'SELL'])

    def handle_misc_menu(self, choice):
        self.misc_menu.unfocus()
        self.state = 'dialog'
        if choice is None:
            self.dialog = create_prompt("Well, when I can help you, you know where I am.")
            self.next = 'exit'
        elif choice == 'BUY':
            self.dialog = create_prompt("What can I get you?")
            self.next = 'shop_menu'
        elif choice == 'SELL':
            if len(self.game.get_company_names(with_items=True)) == 0:
                self.dialog = create_prompt("I'm sorry. You don't have anything to sell. Are you buying or selling?")
                self.next = 'misc_menu'
            else:
                self.dialog = create_prompt("Who is carrying the merchandise?")
                self.company_menu_type = 'selling'
                self.next = 'company_menu'

    def handle_shop_menu_selection(self):
        if self.misc_menu.get_choice() == 'BUY':
            self.handle_shop_menu_buy()
        else:
            self.handle_shop_menu_sell()

    def handle_shop_menu_buy(self):
        self.state = 'dialog'
        item = self.shop_menu.get_choice()
        if item['cost'] > self.game.game_state['money']:
            self.dialog = create_prompt("I'm sorry. You don't have enough money for that. Anything else?")
            self.next = 'shop_menu'
        elif len(self.game.get_company_names(with_empty_item_slots=True)) == 0:
            self.dialog = create_prompt("I'm sorry. You don't have any room to carry more items. Anything else?")
            self.next = 'shop_menu'
        else:
            self.dialog = create_prompt("And who will be carrying that?")
            self.company_menu_type = 'buying'
            self.next = 'company_menu'
            self.create_spoils_box()
        self.shop_menu.unfocus()

    def handle_shop_menu_sell(self):
        self.state = 'dialog'
        item = self.shop_menu.get_choice()
        if 'cost' in ITEMS[item['name']] and not ITEMS[item['name']].get('rare'):
            self.value = int(ITEMS[item['name']]['cost'] * 0.5)
            self.dialog = create_prompt(
                u"{}... I'll give you {} senines. Deal?".format(item['name'].title(), self.value),
            )
            self.next = 'confirm'
        else:
            self.next = 'shop_menu'
            self.dialog = create_prompt("I can't accept that. Anything else?")

    def handle_shop_menu_cancel(self):
        self.shop_menu = None
        self.state = 'dialog'
        if self.misc_menu.get_choice() == 'BUY':
            self.dialog = create_prompt("Are you buying or selling?")
            self.next = 'misc_menu'
        else:
            self.dialog = create_prompt("Who is carrying the merchandise?")
            self.company_menu_type = 'selling'
            self.next = 'company_menu'

    def handle_company_menu_selection(self):
        if self.misc_menu.get_choice() == 'BUY':
            self.handle_company_menu_buy()
        else:
            self.handle_company_menu_sell()

    def handle_company_menu_buy(self):
        self.company_menu.unfocus()
        self.state = 'dialog'
        warlord_name = self.company_menu.get_choice() # leave it capitalized
        warlord_name_lower = warlord_name.lower()
        for warlord_index, warlord in enumerate(self.game.game_state['company']):
            if warlord['name'] == warlord_name_lower:
                break
        current_items = warlord['items']
        if len(current_items) >= MAX_ITEMS_PER_PERSON:
            self.next = 'company_menu'
            self.dialog = create_prompt(u"{} can't carry any more. Who will be carrying that?".format(warlord_name))
            self.company_menu_type = 'buying'
        else:
            self.next = 'shop_menu'
            self.dialog = create_prompt("Thank you. Anything else?")
            self.company_menu = None
            item = self.shop_menu.get_choice()
            self.game.add_to_inventory(item['name'], warlord_index)
            self.game.update_game_state({'money': self.game.game_state['money'] - item['cost']})

    def handle_company_menu_sell(self):
        self.company_menu.unfocus()
        self.state = 'dialog'
        warlord_name = self.company_menu.get_choice() # leave it capitalized
        warlord_name_lower = warlord_name.lower()
        for warlord_index, warlord in enumerate(self.game.game_state['company']):
            if warlord['name'] == warlord_name_lower:
                break
        items = warlord['items']
        if len(items) == 0:
            self.dialog = create_prompt(u"{} has nothing to sell. Who is carrying the merchandise?".format(warlord_name))
            self.company_menu_type = 'selling'
            self.next = 'company_menu'
        else:
            self.dialog = create_prompt("Which item?")
            self.next = 'shop_menu'

    def handle_company_menu_cancel(self):
        self.state = 'dialog'
        self.company_menu = None
        if self.misc_menu.get_choice() == 'BUY':
            self.next = 'shop_menu'
            self.dialog = create_prompt("What can I sell you?")
        else:
            self.dialog = create_prompt("Are you buying or selling?")
            self.next = 'misc_menu'

    def create_shop_menu(self):
        if self.misc_menu.get_choice() == 'BUY':
            self.shop_menu = ShopMenu(self.shop['items'])
        else:
            warlord_name = self.company_menu.get_choice() # leave it capitalized
            warlord_name_lower = warlord_name.lower()
            for warlord_index, warlord in enumerate(self.game.game_state['company']):
                if warlord['name'] == warlord_name_lower:
                    break
            items = warlord['items']
            self.shop_menu = ShopMenu([
                {
                    'name': u"{}{}".format(
                        '*' if item.get('equipped') else '',
                        item['name'],
                    ),
                    'cost': '',
                }
                for item in items
            ])

    def handle_confirm_yes(self):
        warlord_name = self.company_menu.get_choice() # leave it capitalized
        warlord_name_lower = warlord_name.lower()
        for warlord_index, warlord in enumerate(self.game.game_state['company']):
            if warlord['name'] == warlord_name_lower:
                break
        item_index = self.shop_menu.current_choice
        self.game.sell_item(warlord_index, item_index)
        self.confirm_menu = None
        self.shop_menu = None
        self.create_spoils_box()
        self.state = 'dialog'
        if len(self.game.get_company_names(with_items=True)) == 0:
            self.dialog = create_prompt("Thank you. It looks like that was your last item. Is there anything else you would like to do?")
            self.next = 'misc_menu'
            self.company_menu = None
        else:
            self.next = 'company_menu'
            self.company_menu_type = 'selling'
            self.dialog = create_prompt("Thank you. Would you like to sell anything else?")

    def handle_confirm_no(self):
        self.state = 'dialog'
        self.dialog = create_prompt("Would you like to sell anything else?")
        self.company_menu_type = 'selling'
        self.next = 'company_menu'
        self.confirm_menu = None
        self.shop_menu = None


class Reserve(Shop):
    def __init__(self, shop, game):
        super(Reserve, self).__init__(shop, game)
        leader = self.game.get_leader()['name'].title()
        self.dialog = create_prompt(u"{}. What can I do for you?".format(leader))
        self.next = 'misc_menu'
        self.surplus_page = 0
        self.reserve_page = 0

    def create_misc_menu(self):
        self.misc_menu = MenuBox(['STATS', 'NEW~MEM', 'DEL~MEM', 'FIRE', 'SURPLUS'])

    def handle_shop_menu_selection(self):
        if self.shop_menu.get_choice() == 'ETC':
            self.surplus_page += 1
            if len(self.game.game_state['surplus'])/8 < self.surplus_page:
                self.surplus_page = 0
            self.create_shop_menu()
            self.shop_menu.focus()
        elif len(self.game.get_company_names(with_empty_item_slots=True)) == 0:
            self.state = 'dialog'
            self.dialog = create_prompt("You don't have enough room to carry it. Anything else?")
            self.next = 'shop_menu'
            self.shop_menu.unfocus()
        else:
            self.state = 'dialog'
            self.dialog = create_prompt("And who will be carrying that?")
            self.company_menu_type = 'buying'
            self.next = 'company_menu'
            self.shop_menu.unfocus()

    def handle_shop_menu_cancel(self):
        self.state = 'dialog'
        self.dialog = self.create_exit_dialog()
        self.next = 'exit'

    def handle_company_menu_selection(self):
        if self.company_menu.get_choice() == 'ETC':
            self.reserve_page += 1
            if len(self.game.game_state['reserve'])/8 < self.reserve_page:
                self.reserve_page = 0
            self.create_company_menu()
            self.company_menu.focus()
        else:
            self.state = 'dialog'
            mode = self.misc_menu.get_choice()
            if mode == 'STATS':
                self.handle_stats()
            elif mode == 'NEW~MEM':
                self.handle_recruit()
            elif mode == 'DEL~MEM':
                self.handle_delete()
            elif mode == 'FIRE':
                self.handle_fire()
            elif mode == 'SURPLUS':
                self.handle_get_surplus_item()

    def handle_get_surplus_item(self):
        warlord_name = self.company_menu.get_choice() # leave it capitalized
        warlord_name_lower = warlord_name.lower()
        for warlord_index, warlord in enumerate(self.game.game_state['company']):
            if warlord['name'] == warlord_name_lower:
                break
        surplus_index = self.shop_menu.current_choice + self.surplus_page * 8
        items = warlord['items']
        if len(items) >= MAX_ITEMS_PER_PERSON:
            self.next = 'company_menu'
            self.dialog = create_prompt(u"{} cannot carry any more. Who will be carrying that?".format(warlord_name))
            self.company_menu_type = 'buying'
        else:
            self.game.get_surplus_item(surplus_index, warlord_index)
            if len(self.game.game_state['surplus']) > 0:
                self.surplus_page = 0
                self.next = 'shop_menu'
                self.dialog = create_prompt("Here you go. Anything else?")
                self.company_menu = None
            else:
                self.next = 'exit'
                self.dialog = create_prompt("Here you go. Have a good day.")

    def handle_stats(self):
        warlord_name = self.company_menu.get_choice().lower()
        level = self.game.game_state['level']
        self.report = Report(warlord_name, level, [], headless=self.game.get_headless(warlord_name))
        self.company_menu.unfocus()
        self.state = 'company_menu'

    def handle_recruit(self):
        reserve_index = self.company_menu.current_choice + self.reserve_page * 8
        self.game.recruit(reserve_index)
        self.next = 'exit'
        warlord_name = self.company_menu.get_choice() # keep capitalization
        self.dialog = create_prompt(u"OK. {} has joined the traveling party.".format(warlord_name))

    def handle_delete(self):
        warlord_name = self.company_menu.get_choice() # leave it capitalized
        warlord_name_lower = warlord_name.lower()
        for warlord_index, warlord in enumerate(self.game.game_state['company']):
            if warlord['name'] == warlord_name_lower:
                break
        if len(warlord['items']) > 0:
            surplus_text = " His items are in surplus."
        else:
            surplus_text = ""
        self.game.delete_member(warlord_index)
        self.next = 'exit'
        self.dialog = create_prompt(u"OK. {} went to the reserve.{}".format(warlord_name, surplus_text))

    def handle_fire(self):
        warlord_name = self.company_menu.get_choice()
        if warlord_name.lower() not in WARLORDS_EXEMPT_FROM_FIRING:
            self.next = 'confirm'
            self.dialog = create_prompt(u"You want to fire {}?".format(warlord_name))
        else:
            self.dialog = create_prompt(
                u"{} shows great promise. You should not give up on him so easily.".format(warlord_name),
            )
            self.next = 'exit'

    def handle_company_menu_cancel(self):
        self.state = 'dialog'
        mode = self.misc_menu.get_choice()
        if mode == 'SURPLUS':
            self.dialog = create_prompt("Which item would you like to pick up?")
            self.next = 'shop_menu'
        else:
            self.dialog = self.create_exit_dialog()
            self.next = 'exit'

    def handle_confirm_yes(self):
        reserve_index = self.company_menu.current_choice + self.reserve_page * 8
        self.game.fire(reserve_index)
        self.next = 'exit'
        warlord_name = self.company_menu.get_choice() # keep capitalization
        self.dialog = create_prompt(u"OK. {} has left our side.".format(warlord_name))
        self.state = 'dialog'

    def handle_confirm_no(self):
        self.state = 'dialog'
        self.next = 'exit'
        self.dialog = self.create_exit_dialog()

    def handle_misc_menu(self, choice):
        self.state = 'dialog'
        if choice is None:
            self.dialog = self.create_exit_dialog()
            self.next = 'exit'
        elif choice == 'STATS':
            if len(self.game.game_state['reserve']) > 0:
                self.next = 'company_menu'
                self.dialog = create_prompt("Whose profile would you like to see?")
                self.company_menu_type = None
            else:
                self.next = 'exit'
                self.dialog = self.create_no_warlords_dialog()
        elif choice == 'NEW~MEM':
            if len(self.game.game_state['company']) >= 7:
                self.dialog = create_prompt("Your traveling party is too big to add any more people.")
                self.next = 'exit'
            elif len(self.game.game_state['reserve']) == 0:
                self.dialog = self.create_no_warlords_dialog()
                self.next = 'exit'
            else:
                self.dialog = create_prompt("Who would you like to add?")
                self.next = 'company_menu'
                self.company_menu_type = None
        elif choice == 'DEL~MEM':
            if len(self.game.game_state['company']) <= 1:
                self.dialog = create_prompt("You only have one member in your traveling party right now.")
                self.next = 'exit'
            else:
                self.dialog = create_prompt("Who would you like to leave behind?")
                self.next = 'company_menu'
                self.company_menu_type = None
        elif choice == 'FIRE':
            if len(self.game.game_state['reserve']) > 0:
                self.next = 'company_menu'
                self.dialog = create_prompt("Whom would you like to fire?")
                self.company_menu_type = None
            else:
                self.next = 'exit'
                self.dialog = self.create_no_warlords_dialog()
        elif choice == 'SURPLUS':
            if len(self.game.game_state['surplus']) > 0:
                self.next = 'shop_menu'
                self.dialog = create_prompt("Which item would you like to pick up from surplus?")
            else:
                self.next = 'exit'
                self.dialog = self.create_no_surplus_dialog()

    def create_shop_menu(self):
        surplus = self.game.game_state['surplus'][self.surplus_page*8:(self.surplus_page+1)*8]
        surplus = [name.title() for name in surplus]
        if len(self.game.game_state['surplus']) > MAX_ITEMS_PER_PERSON:
            surplus.append('ETC')
        self.shop_menu = MenuBox(surplus)

    def create_company_menu(self):
        mode = self.misc_menu.get_choice()
        if mode == 'DEL~MEM':
            self.company_menu = MenuBox(self.game.get_company_names())
        elif mode == 'SURPLUS':
            self.company_menu = MenuBox(self.game.get_company_names(with_empty_item_slots=True))
        elif mode in ('STATS', 'NEW~MEM', 'FIRE'):
            reserve = self.game.game_state['reserve'][self.reserve_page*8:(self.reserve_page+1)*8]
            reserve = [name.title() for name in reserve]
            if len(self.game.game_state['reserve']) > MAX_ITEMS_PER_PERSON:
                reserve.append('ETC')
            self.company_menu = MenuBox(reserve)

    def create_exit_dialog(self):
        return create_prompt("Come back anytime. Brethren, adieu.")

    def create_no_warlords_dialog(self):
        return create_prompt("I'm sorry, but you don't have any warlords in the reserve.")

    def create_no_surplus_dialog(self):
        return create_prompt("I'm sorry, but you don't have any surplus items.")


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
