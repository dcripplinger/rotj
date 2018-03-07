# -*- coding: UTF-8 -*-

import copy
import math
import random
import time

import pygame
from pygame.locals import *

from battle_warlord_rect import Ally, Enemy
from constants import BLACK, GAME_WIDTH, GAME_HEIGHT, ITEMS, TACTICS
from helpers import (
    can_level_up,
    get_equip_based_stat_value,
    get_intelligence,
    get_max_soldiers,
    get_max_tactical_points,
    get_tactic_for_level,
    get_tactics,
    is_quarter_second,
    load_image,
    load_stats,
    unpretty,
)
from report import Report
from text import create_prompt, MenuBox, MenuGrid

COLORS = [
    {
        'soldiers': 640,
        'color': (255,127,127), # pink
        'soldiers_per_pixel': 10,
    },
    {
        'soldiers': 2560,
        'color': (255,106,0), # orange
        'soldiers_per_pixel': 40,
    },
    {
        'soldiers': 10240,
        'color': (255,216,0), # yellow
        'soldiers_per_pixel': 160,
    },
    {
        'soldiers': 40960,
        'color': (0,148,255), # light blue
        'soldiers_per_pixel': 640,
    },
    {
        'soldiers': 163840,
        'color': (0,51,255), # dark blue
        'soldiers_per_pixel': 2560,
    },
    {
        'soldiers': 655360,
        'color': (0,228,0), # green
        'soldiers_per_pixel': 10240,
    },
    {
        'soldiers': 2621440,
        'color': (160,160,160), # gray
        'soldiers_per_pixel': 40960,
    },
    {
        'soldiers': 10485760,
        'color': (160,160,160), # gray
        'soldiers_per_pixel': 40960,
    },
    {
        'soldiers': 1000000000,
        'color': (210,64,64), # dark red
        'soldiers_per_pixel': 81920,
    },
]

RETREAT_TIME_PER_PERSON = 0.2
REMOVE_STATUS_PROB = 0.2 # Chance that a temporary status expires at the end of a volley


class Battle(object):
    def __init__(
        self, screen, game, allies, enemies, battle_type, ally_tactical_points, ally_tactics, near_water, exit=None,
        battle_name=None, narration=None,
    ):
        self.confirm_box = None
        self.battle_name = battle_name
        self.debug = False
        self.ally_tactics = [tactic.strip('~').lower() for tactic in ally_tactics] if ally_tactics else ['']*6
        self.time_elapsed = 0.0
        self.game = game
        self.battle_type = battle_type
        level = self.game.game_state['level']
        self.allies = []
        for i, ally in enumerate(allies):
            json_stats = load_stats(ally['name'])
            equips = self.game.get_equips(ally['name'])
            self.allies.append(Ally({
                'index': i,
                'name': ally['name'],
                'strength': json_stats['strength'],
                'intelligence': json_stats['intelligence'],
                'defense': json_stats['defense'],
                'agility': json_stats['agility'],
                'evasion': json_stats['evasion'],
                'attack_points': get_equip_based_stat_value('attack_points', equips),
                'armor_class': get_equip_based_stat_value('armor_class', equips),
                'tactical_points': ally['tactical_points'],
                'max_tactical_points': get_max_tactical_points(ally['name'], level),
                'soldiers': ally['soldiers'],
                'max_soldiers': get_max_soldiers(ally['name'], level),
                'tactics': get_tactics(json_stats, level, pretty=False),
                'items': ally['items'],
            }, self))
        self.enemies = []
        for i, enemy in enumerate(enemies):
            if isinstance(enemy['stats']['soldiers'], list):
                soldiers = random.choice(enemy['stats']['soldiers'])
            else:
                soldiers = enemy['stats']['soldiers']
            capture = self.game.conditions_are_met(enemy['stats']['capture']) if 'capture' in enemy['stats'] else False
            self.enemies.append(Enemy({
                'index': i,
                'name': enemy['name'],
                'strength': enemy['stats']['strength'],
                'intelligence': enemy['stats']['intelligence'],
                'defense': enemy['stats']['defense'],
                'agility': enemy['stats']['agility'],
                'evasion': enemy['stats']['evasion'],
                'attack_points': enemy['stats']['attack_points'],
                'armor_class': enemy['stats']['armor_class'],
                'tactical_points': enemy['stats']['tactical_points'],
                'max_tactical_points': enemy['stats']['tactical_points'],
                'soldiers': soldiers,
                'max_soldiers': soldiers,
                'tactics': unpretty(enemy['stats'].get('tactics', ['','','','','',''])),
                'items': [],
                'reinforcements': enemy['stats'].get('reinforcements', False),
                'capture': capture,
            }, self))
        self.state = 'start'
            # potential states: start, menu, action, report, report_selected, retreat, all_out, battle, tactic,
            # tactic_ally, tactic_enemy, item, item_ally, item_enemy, dialog, win, lose, execute, risk_it,
            # cancel_all_out, error
        self.warlord = None # the warlord whose turn it is (to make a choice or execute, depending on self.state)
        self.menu = None
        self.portraits = {
            warlord['name']: load_image('portraits/{}.png'.format(warlord['name']))
            for warlord in (allies + enemies)
        }
        self.portrait = None
        self.pointer_right = load_image('pointer.png')
        self.pointer_left = pygame.transform.flip(self.pointer_right, True, False)
        self.screen = screen
        self.right_dialog = None
        self.set_bar_color()
        self.set_start_dialog()
        self.select_sound = pygame.mixer.Sound('data/audio/select.wav')
        self.selected_enemy_index = None
        self.selected_ally_index = None
        self.switch_sound = pygame.mixer.Sound('data/audio/switch.wav')
        self.report = None
        self.submitted_moves = []
        self.enemy_moves = []
        self.ordered_moves = []
        self.good_enemy_statuses = {}
        self.good_ally_statuses = {}
        self.near_water = near_water
        self.excellent_sound = pygame.mixer.Sound('data/audio/excellent.wav')
        self.heavy_damage_sound = pygame.mixer.Sound('data/audio/heavy_damage.wav')
        self.hit_sound = pygame.mixer.Sound('data/audio/hit.wav')
        self.damage_sound = pygame.mixer.Sound('data/audio/damage.wav')
        self.fail_sound = pygame.mixer.Sound('data/audio/fail.wav')
        self.tactic_sound = pygame.mixer.Sound('data/audio/tactic.wav')
        self.ally_tactical_points = ally_tactical_points
        self.cancel_all_out = False
        self.exit_dialog = create_prompt(exit) if exit else None
        self.narration = create_prompt(narration) if narration else None
        self.captured_enemies = []

    def set_start_dialog(self):
        script = ''
        last_enemy_name = ''
        for enemy in self.enemies:
            if enemy.name != last_enemy_name:
                script += '{} approaching.\n'.format(enemy.name.title())
                last_enemy_name = enemy.name
        self.left_dialog = create_prompt(script, silent=True)

    def set_bar_color(self):
        max_max_soldiers = max([ally.max_soldiers for ally in self.allies])
        for color_info in COLORS:
            if max_max_soldiers < color_info['soldiers']:
                color = color_info['color']
                soldiers_per_pixel = color_info['soldiers_per_pixel']
                break
        for ally in self.allies:
            ally.color = color
            ally.soldiers_per_pixel = soldiers_per_pixel
            ally.build_soldiers_bar()
        for enemy in self.enemies:
            enemy.color = color
            enemy.soldiers_per_pixel = soldiers_per_pixel
            enemy.build_soldiers_bar()

    def update_retreat(self, dt):
        if not self.warlord:
            self.right_dialog.update(dt)
            if not self.right_dialog.has_more_stuff_to_show() and self.get_leader().state == 'wait':
                self.warlord = self.get_leader()
                self.time_elapsed = 0.0
                self.right_dialog.shutdown()
        else:
            if self.time_elapsed > RETREAT_TIME_PER_PERSON:
                self.time_elapsed -= RETREAT_TIME_PER_PERSON
                self.warlord.flip_sprite()
                self.warlord = self.get_next_live_ally_after(self.warlord, nowrap=True)
                if not self.warlord:
                    self.end_battle(self.get_company(), self.ally_tactical_points)

    def update_risk_it(self, dt):
        if self.get_leader().state == 'wait':
            self.simulate_battle()
            if self.state == 'win':
                self.excellent_sound.play()
            else:
                self.heavy_damage_sound.play()
            time.sleep(1)

    def get_captured_enemies(self):
        story_battle = self.battle_type in ['story', 'giddianhi', 'zemnarihah']
        if story_battle:
            return list(self.captured_enemies)
        captured_enemies = []
        for enemy in self.enemies:
            if enemy.capture and random.random() < 0.5:
                captured_enemies.append(enemy)
        return captured_enemies

    def update_win(self, dt):
        if self.win_state == 'start':
            if self.exit_dialog:
                self.exit_dialog.update(dt)
                return
            if self.narration:
                self.narration.update(dt)
                return
            if self.food > 0:
                victory_script = "{}'s army has conquered {}. We got {} exp. points, {} senines, and {} rations."
                victory_script = victory_script.format(
                    self.get_leader().name.title(), self.enemies[0].name.title(), self.experience, self.money,
                    self.food,
                )
            else:
                victory_script = "{}'s army has conquered {}. We got {} exp. points and {} senines."
                victory_script = victory_script.format(
                    self.get_leader().name.title(), self.enemies[0].name.title(), self.experience, self.money,
                )
            self.right_dialog = create_prompt(victory_script)
            self.captured_enemies = self.get_captured_enemies()
            pygame.mixer.music.load('data/audio/music/victory.wav')
            pygame.mixer.music.play()
            self.win_state = 'main'
        elif self.win_state == 'main':
            self.right_dialog.update(dt)
            if is_quarter_second():
                for ally in self.get_live_allies():
                    ally.sprite = ally.stand_s
            else:
                for ally in self.get_live_allies():
                    ally.sprite = ally.walk_s
        elif self.win_state == 'level_up':
            self.right_dialog.update(dt)
        elif self.win_state == 'capture':
            if self.confirm_box:
                self.confirm_box.update(dt)
            else:
                self.right_dialog.update(dt)
                if not self.right_dialog.has_more_stuff_to_show():
                    self.confirm_box = MenuBox(['YES', 'NO'])
                    self.confirm_box.focus()
                    self.right_dialog.shutdown()
        elif self.win_state == 'bargain':
            if self.confirm_box:
                self.confirm_box.update(dt)
            else:
                self.right_dialog.update(dt)
                if self.bargain and not self.right_dialog.has_more_stuff_to_show():
                    self.confirm_box = MenuBox(['YES', 'NO'])
                    self.confirm_box.focus()
                    self.right_dialog.shutdown()

    def update_lose(self, dt):
        if self.lose_state == 'start':
            self.right_dialog = create_prompt('Your army has been overcome by the enemy. Game over.')
            pygame.mixer.music.load('data/audio/music/game_over.wav')
            pygame.mixer.music.play()
            self.lose_state = 'main'
        elif self.lose_state == 'main':
            self.right_dialog.update(dt)
            if is_quarter_second():
                for enemy in self.get_live_enemies():
                    enemy.sprite = enemy.stand_s
            else:
                for enemy in self.get_live_enemies():
                    enemy.sprite = enemy.walk_s

    def update(self, dt):
        self.time_elapsed += dt
        for ally in self.allies:
            ally.update(dt)
        for enemy in self.enemies:
            enemy.update(dt)
        if self.state == 'start':
            self.left_dialog.update(dt)
        elif self.state == 'menu':
            self.menu.update(dt)
        elif self.state == 'retreat':
            self.update_retreat(dt)
        elif self.state == 'risk_it':
            self.update_risk_it(dt)
        elif self.state == 'win':
            self.update_win(dt)
        elif self.state == 'lose':
            self.update_lose(dt)
        elif self.state == 'all_out':
            self.update_all_out(dt)
        elif self.state == 'cancel_all_out':
            if self.get_leader().state == 'wait':
                self.init_menu_state()
        elif self.state == 'execute':
            self.update_execute(dt)
        elif self.state == 'defend':
            if self.warlord.state == 'wait':
                self.warlord = self.get_next_live_ally_after(self.warlord, nowrap=True)
                if self.warlord:
                    self.init_menu_state()
                else:
                    self.init_execute_state()
        elif self.state == 'item':
            self.menu.update(dt)
        elif self.state == 'error':
            self.right_dialog.update(dt)
        elif self.state == 'tactic':
            self.menu.update(dt)

    def update_execute(self, dt):
        if self.execute_state == 'move_back':
            if self.warlord is None or self.warlord.state == 'wait':
                if len(self.ordered_moves) > 0:
                    self.move = self.ordered_moves.pop(0)
                    self.warlord = self.move['agent']
                    self.warlord.move_forward()
                    self.execute_state = 'move_forward'
                else:
                    self.move = None
                    self.warlord = None
                    self.submitted_moves = []
                    self.enemy_moves = []
                    ally_status_updates = []
                    enemy_status_updates = []
                    for (status, duration) in list(self.good_ally_statuses.items()):
                        if duration == 'temporary' and random.random() < REMOVE_STATUS_PROB:
                            del self.good_ally_statuses[status]
                            ally_status_updates.append(status)
                    for (status, duration) in list(self.good_enemy_statuses.items()):
                        if duration == 'temporary' and random.random() < REMOVE_STATUS_PROB:
                            del self.good_enemy_statuses[status]
                            enemy_status_updates.append(status)
                    got_reinforcements = False
                    for enemy in self.enemies:
                        if enemy.reinforcements and enemy.soldiers == 0:
                            enemy.get_healed(enemy.max_soldiers)
                            enemy.state = 'wait'
                            enemy.rel_pos = 0
                            enemy.rel_target_pos = None
                            got_reinforcements = True
                    self.execute_state = 'dialog'
                    self.right_dialog = self.finish_volley_dialog(
                        ally_status_updates, enemy_status_updates, got_reinforcements,
                    )
        elif self.execute_state == 'move_forward':
            if self.warlord.state == 'wait':
                if self.warlord.soldiers == 0:
                    self.execute_state = 'move_back'
                else:
                    self.execute_move(self.move)
                    self.mini_moves, self.mini_results = self.get_mini_moves(self.move, self.results)
                    self.execute_state = 'mini_move'
        elif self.execute_state == 'mini_move':
            self.pop_and_handle_mini_move()
            if self.mini_move:
                self.execute_state = 'dialog'
                self.portrait = self.portraits[self.move['agent'].name]
                dialog = self.get_move_dialog(self.mini_move, self.mini_result)
                if self.move['agent'] in self.allies:
                    self.right_dialog = dialog
                else:
                    self.left_dialog = dialog
            else:
                self.execute_state = 'move_back'
                self.warlord.move_back()
                self.portrait = None
        elif self.execute_state == 'dialog':
            dialog = self.right_dialog or self.left_dialog
            if dialog:
                dialog.update(dt)
            else:
                if len(self.ordered_moves) == 0:
                    self.init_menu_state()
                else:
                    self.execute_state = 'mini_move'

    def finish_volley_dialog(self, ally_status_updates, enemy_status_updates, got_reinforcements):
        prompt_text = ""
        for status in ally_status_updates:
            prompt_text += "Your army's {} status has worn off. ".format(status.title())
        for status in enemy_status_updates:
            prompt_text += "The enemy's {} status has worn off. ".format(status.title())
        if got_reinforcements:
            prompt_text += "Enemy reinforcements have arrived."
        if not prompt_text:
            return None
        else:
            return create_prompt(prompt_text)

    def get_mini_moves(self, move, results):
        mini_moves = []
        mini_results = []
        if move['action'] in [self.execute_move_battle, self.execute_move_confuse, self.execute_move_provoke]:
            mini_moves.append(move)
            mini_result = copy.copy(results)
            if 'double_tap' in mini_result:
                del mini_result['double_tap']
                if 'killed' in mini_result:
                    del mini_result['killed']
                mini_results.append(mini_result)
                mini_moves.append(move)
                mini_result = copy.copy(results)
                mini_result['damage'] = mini_result['double_tap']
                del mini_result['double_tap']
                mini_results.append(mini_result)
            else:
                mini_results.append(results)
        elif move['action'] in [self.execute_move_defend, self.execute_move_item]:
            mini_moves.append(move)
            mini_results.append(results)
        elif move['action'] == self.execute_move_tactic:
            results.update({'first': True})
            mini_moves.append(move)
            mini_results.append(results)
        return mini_moves, mini_results

    def get_damage_dialog(self, mini_move, mini_result, is_ally_move):
        if is_ally_move:
            dialog = "We defeated {} of {}'s soldiers. ".format(
                mini_result['damage'], mini_move['target'].name.title(),
            )
        else:
            dialog = "{} of {}'s soldiers were defeated. ".format(
                mini_result['damage'], mini_move['target'].name.title(),
            )
        if mini_result.get('killed'):
            if is_ally_move:
                dialog += "{} vanquished {}.".format(
                    mini_move['agent'].name.title(), mini_move['target'].name.title(),
                )
            else:
                dialog += "{} has been routed by {}.".format(
                    mini_move['target'].name.title(), mini_move['agent'].name.title(),
                )
        return dialog

    def get_healing_dialog(self, mini_move, mini_result):
        return "Some of {}'s soldiers have recovered their strength.".format(mini_move['target'].name.title())

    def get_move_dialog(self, mini_move, mini_result):
        is_ally_move = mini_move['agent'] in self.allies
        if mini_move['action'] in [self.execute_move_battle, self.execute_move_confuse, self.execute_move_provoke]:
            dialog = "{}'s attack. ".format(mini_move['agent'].name.title())
            if mini_result.get('evade'):
                dialog += "{} evaded the attack.".format(mini_move['target'].name.title())
                return create_prompt(dialog)
            if mini_result.get('repel'):
                if is_ally_move:
                    dialog += "The enemy is repelling all attacks."
                else:
                    dialog += "{}'s army is repelling all attacks.".format(self.get_leader().name.title())
                return create_prompt(dialog)
            if mini_result.get('excellent'):
                if is_ally_move:
                    dialog += "{} did heavy damage. ".format(mini_move['agent'].name.title())
                else:
                    dialog += "{} took heavy damage. ".format(mini_move['target'].name.title())
            dialog += self.get_damage_dialog(mini_move, mini_result, is_ally_move)
            return create_prompt(dialog)
        elif mini_move['action'] == self.execute_move_defend:
            return create_prompt("{} is defending.".format(mini_move['agent'].name.title()))
        elif mini_move['action'] == self.execute_move_tactic:
            if mini_result.get('first'):
                dialog = "{} uses {}. ".format(mini_move['agent'].name.title(), mini_move['tactic'].title())
            else:
                dialog = ""
            if mini_result.get('deflect'):
                if is_ally_move:
                    dialog += "The enemy is deflecting all tactics."
                else:
                    dialog += "{}'s army is deflecting all tactics.".format(self.get_leader().name.title())
                return create_prompt(dialog)
            elif mini_result.get('wasted'):
                dialog += "They feel so dumb for wasting their move on a dead guy."
                return create_prompt(dialog)
            elif mini_result.get('fail'):
                dialog += "Failed."
                return create_prompt(dialog)
            elif 'damage' in mini_result:
                dialog += self.get_damage_dialog(mini_move, mini_result, is_ally_move)
                return create_prompt(dialog)
            elif 'healing' in mini_result:
                dialog += self.get_healing_dialog(mini_move, mini_result)
                return create_prompt(dialog)
            elif mini_move['tactic'] == 'firewall':
                dialog += "Fire damage is reduced by half."
                return create_prompt(dialog)
            elif mini_move['tactic'] == 'extinguish':
                dialog += 'Fire damage is reduced to one.'
                return create_prompt(dialog)
            elif mini_move['tactic'] == 'provoke':
                dialog += "{} is mindlessly targeting {}.".format(
                    mini_move['target'].name.title(), mini_move['agent'].name.title(),
                )
                return create_prompt(dialog)
            elif mini_move['tactic'] == 'ninja':
                dialog += "{}'s agility is increased to 255.".format(mini_move['target'].name.title())
                return create_prompt(dialog)
        elif mini_move['action'] == self.execute_move_item:
            dialog = "{} uses {}. ".format(mini_move['agent'].name.title(), mini_move['item'].title())
            if mini_result.get('wasted'):
                dialog += "They feel so dumb for wasting their move on a dead guy."
                return create_prompt(dialog)
            elif 'healing' in mini_result:
                dialog += self.get_healing_dialog(mini_move, mini_result)
                return create_prompt(dialog)

    def pop_and_handle_mini_move(self):
        if len(self.mini_moves) > 0:
            self.mini_move = self.mini_moves.pop(0)
            self.mini_result = self.mini_results.pop(0)
            sound = self.get_move_sound(self.mini_move, self.mini_result)
            if sound:
                sound.play()
            self.animate_move_hit(self.mini_move, self.mini_result)
        else:
            self.mini_move = None
            self.mini_result = None

    def update_all_out(self, dt):
        if self.all_out_state == 'move_back_leader':
            if self.warlord.state == 'wait':
                self.all_out_state = 'charge'
                for warlord in self.get_live_allies() + self.get_live_enemies():
                    warlord.move_to_front()
                self.warlord = None
        elif self.all_out_state == 'charge':
            if self.get_leader().state == 'wait':
                self.all_out_state = 'main'
        elif self.all_out_state == 'main' and self.get_leader().state == 'wait':
            time.sleep(.1) # pause between each all-out animation
            if len(self.submitted_moves) == 0:
                if self.cancel_all_out == True:
                    for warlord in self.get_live_allies() + self.get_live_enemies():
                        warlord.move_back()
                    self.state = 'cancel_all_out'
                    self.cancel_all_out = False
                    return
                else:
                    self.submit_ai_moves()
            next_move = self.ordered_moves.pop(0)
            self.execute_move(next_move)
            for warlord in self.get_live_allies() + self.get_live_enemies():
                warlord.animate_all_out()
            move_sound = self.get_move_sound(self.move, self.results)
            if move_sound:
                move_sound.play()
            self.animate_move_hit(self.move, self.results)
            if len(self.ordered_moves) == 0:
                self.submitted_moves = []
                self.enemy_moves = []
                for (status, duration) in list(self.good_ally_statuses.items()):
                    if duration == 'temporary' and random.random() < REMOVE_STATUS_PROB:
                        del self.good_ally_statuses[status]
                for (status, duration) in list(self.good_enemy_statuses.items()):
                    if duration == 'temporary' and random.random() < REMOVE_STATUS_PROB:
                        del self.good_enemy_statuses[status]
                for enemy in self.enemies:
                    if enemy.reinforcements and enemy.soldiers == 0:
                        enemy.get_healed(enemy.max_soldiers)
                        enemy.state = 'wait'
                        enemy.rel_pos = 0
                        enemy.rel_target_pos = None

    def animate_move_hit(self, move, results):
        if (
            results.get('repel') or results.get('evade') or results.get('fail') or results.get('deflect')
            or results.get('wasted')
        ):
            return
        elif move['action'] == self.execute_move_battle:
            move['target'].animate_hit('attack')
        elif move['action'] == self.execute_move_tactic:
            slot = TACTICS[move['tactic']]['slot']
            if slot == 1:
                move['target'].animate_hit('fire')
            elif slot == 2:
                move['target'].animate_hit('water')

    def get_company(self):
        return {
            ally.name: {
                'name': ally.name,
                'tactical_points': ally.get_tactical_points(),
                'soldiers': ally.soldiers,
                'items': ally.items,
            }
            for ally in self.allies
        }

    def simulate_battle(self):
        while self.state == 'risk_it':
            self.simulate_volley()
            self.submitted_moves = []
            self.enemy_moves = []
            self.ordered_moves = []

    def submit_ai_moves(self, include_allies=True):
        if include_allies:
            enemies = self.get_live_enemies()
            for ally in self.get_live_allies():
                move = {'agent': ally, 'action': self.execute_move_battle, 'target': random.choice(enemies)}
                self.submit_move(move)
        self.generate_enemy_moves()
        self.ordered_moves = self.get_moves_in_order_of_agility()

    def simulate_volley(self):
        self.submit_ai_moves()
        self.execute_moves()
        for (status, duration) in list(self.good_ally_statuses.items()):
            if duration == 'temporary' and random.random() < REMOVE_STATUS_PROB:
                del self.good_ally_statuses[status]
        for (status, duration) in list(self.good_enemy_statuses.items()):
            if duration == 'temporary' and random.random() < REMOVE_STATUS_PROB:
                del self.good_enemy_statuses[status]
        for enemy in self.enemies:
            if enemy.reinforcements and enemy.soldiers == 0:
                enemy.get_healed(enemy.max_soldiers)
                enemy.state = 'wait'
                enemy.rel_pos = 0
                enemy.rel_target_pos = None

    def execute_moves(self):
        for move in self.ordered_moves:
            result = self.execute_move(move)
            if result != 'continue':
                break

    def execute_move(self, move):
        move = self.change_move_if_dead_or_cursed(move)
        if move is not None:
            action_handler = move['action']
            move, results = action_handler(move)
            self.results = results
            self.move = move
            if results.get('killed'):
                if move['target'] in self.enemies and all(enemy.soldiers == 0 for enemy in self.enemies):
                    self.handle_win()
                    return 'win'
                elif move['target'] in self.allies and all(ally.soldiers == 0 for ally in self.allies):
                    self.handle_lose()
                    return 'lose'
        return 'continue'

    def handle_win(self):
        self.state = 'win'
        self.menu = None
        self.portrait = None
        self.collect_spoils()
        self.win_state = 'start'

    def collect_spoils(self):
        story_battle = self.battle_type in ['story', 'giddianhi', 'zemnarihah']
        story_battle_gain = 3 if story_battle else 1
        base_num = 1.0 * sum([e.max_soldiers * e.attack_points for e in self.enemies])
        self.experience = int(0.001 * base_num) * story_battle_gain
        self.money = int(0.004 * base_num) * story_battle_gain
        self.food = int(0.009 * base_num) if story_battle else 0
        self.levels = self.game.collect_spoils(self.experience, self.money, self.food)

    def handle_lose(self):
        self.state = 'lose'
        self.menu = None
        self.portrait = None
        self.lose_state = 'start'

    def get_moves_in_order_of_agility(self):
        the_moves = self.submitted_moves + self.enemy_moves
        the_moves.sort(key=lambda move: move['agent'].get_effective_agility(), reverse=True)
        return the_moves

    def get_move_sound(self, move, results):
        if (
            results.get('repel') or results.get('evade') or results.get('fail') or results.get('deflect')
            or results.get('wasted')
        ):
            return self.fail_sound
        elif move['action'] in [self.execute_move_battle, self.execute_move_confuse, self.execute_move_provoke]:
            if move['agent'] in self.allies:
                return self.excellent_sound if results.get('excellent') else self.hit_sound
            else:
                return self.heavy_damage_sound if results.get('excellent') else self.damage_sound
        elif move['action'] == self.execute_move_defend:
            return None
        elif move['action'] == self.execute_move_tactic:
            return self.tactic_sound if TACTICS[move['tactic']]['type'] in ['enemy', 'enemies'] else None
        elif move['action'] == self.execute_move_item:
            return None

    def execute_move_battle(self, move):
        is_ally_move = move['agent'] in self.allies
        if move['target'].soldiers == 0:
            targets = self.get_live_enemies() if is_ally_move else self.get_live_allies()
            return self.execute_move_battle({
                'agent': move['agent'],
                'target': random.choice(targets),
                'action': self.execute_move_battle,
            })
        if 'defend' in move['agent'].boosts:
            del move['agent'].boosts['defend']
        good_target_team_statuses = self.good_enemy_statuses if is_ally_move else self.good_ally_statuses
        if 'repel' in good_target_team_statuses:
            return move, {'repel': True}
        evade_prob = ((move['target'].evasion - move['agent'].agility) / 255.0 + 1) / 2.0
        if random.random() < evade_prob / 4.0: # divide by 4 so that evades aren't too common
            return move, {'evade': True}
        excellent = random.random() < 1.0/16
        inflicted_damage = int( move['target'].attack_exposure * move['agent'].get_damage(excellent=excellent) + 1 )
        if move['agent'].boosts.get('double_tap'):
            double_tap = int( move['target'].attack_exposure * move['agent'].get_damage() + 1 )
        else:
            double_tap = None
        if 'shield' in good_target_team_statuses:
            inflicted_damage = max(inflicted_damage/2, 1)
            if double_tap:
                double_tap = max(double_tap/2, 1)
        if 'defend' in move['target'].boosts:
            inflicted_damage = max(inflicted_damage/2, 1)
            if double_tap:
                double_tap = max(double_tap/2, 1)
        if move['target'].soldiers <= inflicted_damage:
            inflicted_damage = move['target'].soldiers
            move['target'].get_damaged(inflicted_damage)
            return move, {'damage': inflicted_damage, 'killed': True, 'excellent': excellent}
        move['target'].get_damaged(inflicted_damage)
        if double_tap:
            if move['target'].soldiers <= double_tap:
                double_tap = move['target'].soldiers
                move['target'].get_damaged(double_tap)
                return move, {'damage': inflicted_damage, 'double_tap': double_tap, 'killed': True, 'excellent': excellent}
            move['target'].get_damaged(double_tap)
            return move, {'damage': inflicted_damage, 'double_tap': double_tap, 'excellent': excellent}
        return move, {'damage': inflicted_damage, 'excellent': excellent}

    def execute_move_confuse(self, move):
        move, result = self.execute_move_battle(move)
        result.update({'status': 'confuse'})
        return move, result

    def execute_move_disable(self, move):
        return move, {'status': 'disable'}

    def execute_move_provoke(self, move):
        move, result = self.execute_move_battle(move)
        result.update({'status': 'provoke'})
        return move, result

    def execute_move_item(self, move):
        if 'target' in move and move['target'].soldiers == 0:
            return move, {'wasted': True}
        move_type = ITEMS[move['item']]['battle_usage']
        # go through items by type
        if move_type == 'ally':
            return self.execute_item_type_ally(move)
        else:
            return move, {}

    def execute_item_type_ally(self, move):
        info = ITEMS[move['item']]
        if 'healing_points' in info:
            healing = info['healing_points']
            if healing + move['target'].soldiers > move['target'].max_soldiers:
                healing = move['target'].max_soldiers - move['target'].soldiers
            move['target'].get_healed(healing)
            return move, {'healing': healing}

    def execute_move_tactic(self, move):
        if 'target' in move and move['target'].soldiers == 0:
            return move, {'wasted': True}
        is_ally_move = move['agent'] in self.allies
        good_target_team_statuses = self.good_enemy_statuses if is_ally_move else self.good_ally_statuses
        good_acting_team_statuses = self.good_ally_statuses if is_ally_move else self.good_enemy_statuses
        tactic_type = TACTICS[move['tactic']]['type']
        if 'deflect' in good_target_team_statuses:
            return move, {'deflect': True}
        # go through tactics by type
        if tactic_type == 'enemy':
            return self.execute_tactic_type_enemy(move, good_target_team_statuses)
        elif tactic_type == 'ally':
            return self.execute_tactic_type_ally(move)
        elif tactic_type == 'defense':
            return self.execute_tactic_type_defense(move, good_acting_team_statuses)
        else:
            return move, {}

    def execute_tactic_type_defense(self, move, good_acting_team_statuses):
        info = TACTICS[move['tactic']]
        success = self.get_tactic_success(move)
        if not success:
            return move, {'fail': True}
        good_acting_team_statuses[move['tactic']] = info['duration']
        return move, {}

    def execute_tactic_type_ally(self, move):
        info = TACTICS[move['tactic']]
        success = self.get_tactic_success(move)
        if not success:
            return move, {'fail': True}
        if 'min_damage' in info:
            norm_intel = move['agent'].intelligence / 255.0
            norm_cutoff = random.uniform(0.0, norm_intel)
            prelim_healing_range = info['max_damage'] - info['min_damage']
            cutoff = int(norm_cutoff * prelim_healing_range)
            mod_min_healing = info['min_damage'] + cutoff
            healing = random.randrange(mod_min_healing, info['max_damage'])
            if move['target'].soldiers + healing > move['target'].max_soldiers:
                healing = move['target'].max_soldiers - move['target'].soldiers
            move['target'].get_healed(healing)
            return move, {'healing': healing}
        elif move['tactic'] == 'ninja':
            move['target'].good_statuses['ninja'] = True
            return move, {}

    def execute_tactic_type_enemy(self, move, good_target_team_statuses):
        info = TACTICS[move['tactic']]
        success = self.get_tactic_success(move)
        if not success:
            return move, {'fail': True}
        if 'min_damage' in info:
            norm_intel = move['agent'].intelligence / 255.0
            norm_cutoff = random.uniform(0.0, norm_intel)
            prelim_damage_range = info['max_damage'] - info['min_damage']
            cutoff = int(norm_cutoff * prelim_damage_range)
            mod_min_damage = info['min_damage'] + cutoff
            damage = random.randrange(mod_min_damage, info['max_damage'])
            if info['slot'] == 1:
                if 'firewall' in good_target_team_statuses:
                    damage = int(damage/2)
                elif 'extinguish' in good_target_team_statuses:
                    damage = 1
            if move['target'].soldiers <= damage:
                damage = move['target'].soldiers
                move['target'].get_damaged(damage)
                return move, {'damage': damage, 'killed': True}
            move['target'].get_damaged(damage)
            return move, {'damage': damage}
        elif info.get('duration') == 'permanent':
            move['target'].bad_status = {'name': move['tactic'], 'agent': move['agent']}
            return move, {}

    def get_tactic_success(self, move):
        prob_type = TACTICS[move['tactic']]['success_probability_type']
        if prob_type == 'enemy_prob':
            intel = move['agent'].intelligence
            enemy_intel = move['target'].intelligence
            enemy_prob = ((intel-enemy_intel)/255.0+1.0)/2.0
            return random.random() < enemy_prob
        elif prob_type == 'enemy_prob2':
            intel = move['agent'].intelligence
            enemy_intel = move['target'].intelligence
            enemy_prob = ((intel-enemy_intel)/255.0+1.0)/2.0
            enemy_prob2 = min(1.0, enemy_prob*2)
            return random.random() < enemy_prob2
        elif prob_type == 'one':
            return True
        elif prob_type == 'intel_prob':
            intel = move['agent'].intelligence
            intel_prob = intel/255.0
            return random.random() < intel_prob
        elif prob_type == 'assassin':
            intel = move['agent'].intelligence
            enemy_intel = move['target'].intelligence
            enemy_prob = ((intel-enemy_intel)/255.0+1.0)/2.0
            assassin = enemy_prob / 3.0
            return random.random() < assassin

    def execute_move_defend(self, move):
        move['agent'].boosts['defend'] = True
        return move, {'defend': True}

    def change_move_if_dead_or_cursed(self, move):
        if move['agent'].soldiers == 0:
            move = None
        elif move['agent'].bad_status:
            if move['agent'].bad_status['agent'].soldiers == 0:
                move['agent'].bad_status = None
            elif move['agent'].bad_status['name'] == 'disable':
                move = {'agent': move['agent'], 'action': self.execute_move_disable}
            elif move['agent'].bad_status['name'] == 'confuse':
                if move['agent'] in self.allies:
                    random_target = random.choice(self.get_live_allies())
                else:
                    random_target = random.choice(self.get_live_enemies())
                move = {'agent': move['agent'], 'action': self.execute_move_confuse, 'target': random_target}
            else: # provoke
                move = {
                    'agent': move['agent'],
                    'action': self.execute_move_provoke,
                    'target': move['agent'].bad_status['agent'],
                }
        return move

    def generate_enemy_moves(self):
        ally_dangers = {ally.index: ally.get_danger() for ally in self.allies if ally.soldiers > 0}
        sum_dangers = sum(ally_dangers.values())
        ally_target_probabilities = {index: danger*1.0 / sum_dangers for index, danger in ally_dangers.items()}
        for enemy in self.get_live_enemies():
            ally_target_index = self.choose_random_target(ally_target_probabilities)
            self.enemy_moves.append(self.generate_enemy_move(enemy, ally_target_index, sum_dangers))

    def choose_random_target(self, target_probabilities):
        sample = random.random()
        for target in sorted(target_probabilities, key=target_probabilities.get):
            prob = target_probabilities[target]
            if sample < prob:
                return target
            sample -= prob

    def generate_enemy_move(self, enemy, ally_target_index, sum_dangers):
        ally_target = self.allies[ally_target_index]
        random_enemy = random.choice(self.get_live_enemies())

        # heal
        heal_tactic = enemy.tactics[2] if enemy.tactics else None
        tactical_points = enemy.tactical_points
        heal_cost = TACTICS.get(heal_tactic, {}).get('tactical_points', 0)
        if (
            heal_tactic and heal_cost < tactical_points and enemy.soldiers*1.0/enemy.max_soldiers < .5
            and sum_dangers > enemy.soldiers and random.random() < .7
        ):
            action = {'agent': enemy, 'action': self.execute_move_tactic, 'tactic': heal_tactic}
            enemy.consume_tactical_points(heal_cost)
            if TACTICS[heal_tactic]['type'] == 'ally':
                action.update({'target': enemy})
            return action

        # dispel
        if (
            enemy.tactics[4] == 'dispel' if enemy.tactics else None
            and (
                len(self.good_ally_statuses) > 0
                or any([enemy.bad_status for enemy in self.enemies if enemy.soldiers > 0])
            )
            and TACTICS['dispel']['tactical_points'] + heal_cost < tactical_points
            and random.random() < .3
        ):
            enemy.consume_tactical_points(TACTICS['dispel']['tactical_points'])
            return {'agent': enemy, 'action': self.execute_move_tactic, 'tactic': 'dispel'}

        # defense
        defense_tactic = enemy.tactics[3] if enemy.tactics else None
        defense_cost = TACTICS.get(defense_tactic, {}).get('tactical_points', 0)
        if (
            defense_tactic and heal_cost + defense_cost < tactical_points
            and defense_tactic not in self.good_enemy_statuses and random.random() < .2
        ):
            enemy.consume_tactical_points(defense_cost)
            return {'agent': enemy, 'action': self.execute_move_tactic, 'tactic': defense_tactic}

        # provoke, disable
        enemy_prob = self.get_enemy_prob(enemy, ally_target)
        if (
            (enemy.tactics[4] if enemy.tactics else None) in ['provoke', 'disable']
            and heal_cost + TACTICS[enemy.tactics[4]]['tactical_points'] < tactical_points
            and (ally_target.bad_status is None or enemy.tactics[4] != ally_target.bad_status['name'])
            and random.random() < enemy_prob
            and random.random() < .5 # we don't want to be using these all the time
        ):
            enemy.consume_tactical_points(TACTICS[enemy.tactics[4]]['tactical_points'])
            return {
                'agent': enemy, 'action': self.execute_move_tactic, 'tactic': enemy.tactics[4], 'target': ally_target,
            }

        # confuse, assassin
        if (
            (enemy.tactics[5] if enemy.tactics else None) in ['confuse', 'assassin']
            and heal_cost + TACTICS[enemy.tactics[5]]['tactical_points'] < tactical_points
            and (ally_target.bad_status is None or enemy.tactics[5] != ally_target.bad_status['name'])
            and random.random() < enemy_prob
            and random.random() < .5 # we don't want to be using these all the time
        ):
            enemy.consume_tactical_points(TACTICS[enemy.tactics[5]]['tactical_points'])
            return {
                'agent': enemy, 'action': self.execute_move_tactic, 'tactic': enemy.tactics[5], 'target': ally_target,
            }

        # boost_tactic: ninja, double tap, hulk out
        boost_tactic = enemy.tactics[5] if enemy.tactics else None
        if boost_tactic in ['ninja', 'double~tap', 'hulk~out']:
            if (
                (boost_tactic == 'hulk~out' or boost_tactic not in random_enemy.good_statuses)
                and heal_cost + TACTICS[boost_tactic]['tactical_points'] < tactical_points
                and random.random() < .6
            ):
                enemy.consume_tactical_points(TACTICS[enemy.tactics[5]]['tactical_points'])
                return {
                    'agent': enemy, 'action': self.execute_move_tactic, 'tactic': boost_tactic, 'target': random_enemy,
                }

        # water
        maybe_do_tactic_damage = enemy.tactic_danger > enemy.get_preliminary_damage()
        enemy_prob2 = min(1.0, enemy_prob*2)
        if (
            maybe_do_tactic_damage
            and enemy.tactics
            and enemy.tactics[1]
            and self.near_water
            and heal_cost + TACTICS[enemy.tactics[1]]['tactical_points'] < tactical_points
            and random.random() < enemy_prob2
        ):
            enemy.consume_tactical_points(TACTICS[enemy.tactics[1]]['tactical_points'])
            action = {'agent': enemy, 'action': self.execute_move_tactic, 'tactic': enemy.tactics[1]}
            if TACTICS[enemy.tactics[1]]['type'] == 'enemy':
                action.update({'target': ally_target})
            return action

        # fire
        if (
            maybe_do_tactic_damage
            and enemy.tactics
            and enemy.tactics[0]
            and heal_cost + TACTICS[enemy.tactics[0]]['tactical_points'] < tactical_points
            and random.random() < enemy_prob2
        ):
            enemy.consume_tactical_points(TACTICS[enemy.tactics[0]]['tactical_points'])
            action = {'agent': enemy, 'action': self.execute_move_tactic, 'tactic': enemy.tactics[0]}
            if TACTICS[enemy.tactics[0]]['type'] == 'enemy':
                action.update({'target': ally_target})
            return action

        # battle
        return {'agent': enemy, 'action': self.execute_move_battle, 'target': ally_target}

    def get_enemy_prob(self, attacker, target):
        return ((attacker.intelligence - target.intelligence)/255.0+1)/2

    def get_live_allies(self):
        return [ally for ally in self.allies if ally.soldiers > 0]

    def submit_move(self, move):
        self.submitted_moves.append(move)

    def get_live_enemies(self):
        return [enemy for enemy in self.enemies if enemy.soldiers > 0]

    def handle_input_start(self, pressed):
        self.left_dialog.handle_input(pressed)
        if (pressed[K_x] or pressed[K_z]) and not self.left_dialog.has_more_stuff_to_show():
            self.init_menu_state()

    def init_menu_state(self):
        self.state = 'menu'
        self.left_dialog = None
        self.right_dialog = None
        self.warlord = self.warlord or self.get_leader()
        self.portrait = self.portraits[self.warlord.name]
        self.create_menu()
        self.warlord.move_forward()

    def start_next_capture(self):
        self.win_state = 'capture'
        enemy = self.captured_enemies[0]
        self.right_dialog = create_prompt(
            'We captured a general named {}. Should we try to recruit him to our side?'.format(enemy.name.title()),
        )

    def handle_input_win(self, pressed):
        if self.win_state == 'start' and self.exit_dialog:
            self.exit_dialog.handle_input(pressed)
            if pressed[K_x] and not self.exit_dialog.has_more_stuff_to_show():
                self.exit_dialog = None
        elif self.win_state == 'start' and self.narration:
            self.narration.handle_input(pressed)
            if pressed[K_x] and not self.narration.has_more_stuff_to_show():
                self.narration = None
        elif self.win_state == 'main':
            self.right_dialog.handle_input(pressed)
            if (pressed[K_x] or pressed[K_z]) and not self.right_dialog.has_more_stuff_to_show():
                leveled_up = self.level_up()
                if leveled_up:
                    self.win_state = 'level_up'
                elif len(self.captured_enemies) > 0:
                    self.start_next_capture()
                else:
                    self.right_dialog.shutdown()
                    self.end_battle(self.get_company(), self.ally_tactical_points, battle_name=self.battle_name)
        elif self.win_state == 'level_up':
            self.right_dialog.handle_input(pressed)
            if (pressed[K_x] or pressed[K_z]) and not self.right_dialog.has_more_stuff_to_show():
                leveled_up = self.level_up()
                if leveled_up:
                    return
                elif len(self.captured_enemies) > 0:
                    self.start_next_capture()
                else:
                    self.right_dialog.shutdown()
                    self.end_battle(self.get_company(), self.ally_tactical_points, battle_name=self.battle_name)
        elif self.win_state == 'capture':
            if self.confirm_box:
                self.confirm_box.handle_input(pressed)
                if pressed[K_x] and self.confirm_box.get_choice() == 'YES':
                    self.confirm_box = None
                    self.bargain = self.get_bargain()
                    if not self.bargain:
                        self.convert_captured_enemy()
                    elif self.bargain == 'horse':
                        self.right_dialog = create_prompt(
                            'I might be convinced to offer my services for an especially good horse.',
                        )
                        self.win_state = 'bargain'
                    elif self.bargain == 'refuse':
                        self.right_dialog = create_prompt("I'm no traitor! I serve only my master!")
                        self.win_state = 'bargain'
                        self.captured_enemies.pop(0)
                    else:
                        self.right_dialog = create_prompt(
                            'I might be convinced to offer my services for {} senines.'.format(self.bargain),
                        )
                        self.win_state = 'bargain'
                elif (pressed[K_x] and self.confirm_box.get_choice() == 'NO') or pressed[K_z]:
                    enemy = self.captured_enemies.pop(0)
                    self.right_dialog = create_prompt('OK. {} was let go.'.format(enemy.name.title()))
                    self.confirm_box = None
                    self.bargain = None
                    self.win_state = 'bargain'
            else:
                self.right_dialog.handle_input(pressed)
        elif self.win_state == 'bargain':
            if self.confirm_box:
                self.confirm_box.handle_input(pressed)
                if pressed[K_x] and self.confirm_box.get_choice() == 'YES':
                    self.try_bargain()
                elif (pressed[K_x] and self.confirm_box.get_choice() == 'NO') or pressed[K_z]:
                    self.captured_enemies.pop(0)
                    self.right_dialog = create_prompt("Your loss! I'll see you again on the battle field!")
                    self.confirm_box = None
                    self.bargain = None
            else:
                self.right_dialog.handle_input(pressed)
                if (pressed[K_x] or pressed[K_z]) and not self.right_dialog.has_more_stuff_to_show():
                    if len(self.captured_enemies) > 0:
                        self.start_next_capture()
                    else:
                        self.right_dialog.shutdown()
                        self.end_battle(
                            self.get_company(), self.ally_tactical_points, battle_name=self.battle_name,
                        )

    def end_battle(self, *args, **kwargs):
        if kwargs.get('battle_name') == 'battle08':
            kwargs.update({
                'opening_dialog': create_prompt(
                    "Now that Amlici is defeated, I must return to the judgment seat in Zarahemla. Please see me there "
                    "when you get a chance."
                ),
            })
            self.game.remove_from_company_and_reserve('alma')
        self.game.end_battle(*args, **kwargs)

    def try_bargain(self):
        enemy = self.captured_enemies.pop(0)
        self.confirm_box = None
        if self.bargain == 'horse':
            found = False
            for warlord in self.allies:
                if found:
                    break
                for i, item in enumerate(warlord.items):
                    if item['name'] == 'horse':
                        found = True
                        warlord.items.pop(i)
                        break
            if found:
                self.game.add_to_company(enemy.name)
                self.right_dialog = create_prompt('OK. {} has joined your army.'.format(enemy.name.title()))
            else:
                self.right_dialog = create_prompt('Do you take me for a fool? You do not have any horses!')
            self.bargain = None
        else: # money bargain
            current_money = self.game.game_state['money']
            required_money = self.bargain
            if current_money >= required_money:
                self.game.update_game_state({'money': current_money - required_money})
                self.game.add_to_company(enemy.name)
                self.right_dialog = create_prompt('OK. {} has joined your army.'.format(enemy.name.title()))
            else:
                self.right_dialog = create_prompt("You can't even afford me!")
            self.bargain = None

    def get_bargain(self):
        random_number = random.random()
        if random_number < 0.25:
            return None
        elif random_number < 0.5:
            return self.get_required_money_for_recruiting(self.captured_enemies[0].max_soldiers)
        elif random_number < 0.75:
            return 'refuse'
        else:
            return 'horse'

    def get_required_money_for_recruiting(self, soldiers):
        base = .25*soldiers
        extra = random.random()*.25*soldiers
        return int(base+extra)

    def convert_captured_enemy(self):
        enemy = self.captured_enemies.pop(0)
        self.right_dialog = create_prompt('OK. {} has joined your army.'.format(enemy.name.title()))
        self.win_state = 'bargain'
        self.game.add_to_company(enemy.name)

    def level_up(self):
        if len(self.levels) == 0:
            return False
        level = self.levels.pop(0)
        pygame.mixer.music.load('data/audio/music/level.wav')
        pygame.mixer.music.play()
        self.right_dialog.shutdown()
        dialog = "{}'s army has advanced one skill level. ".format(self.get_leader().name.title())
        tactic_guys = []
        tactic = get_tactic_for_level(level)
        for warlord in self.game.game_state['company']:
            if can_level_up(warlord['name']):
                dialog += "{} now has {} soldiers. ".format(
                    warlord['name'].title(), get_max_soldiers(warlord['name'], level),
                )
                if tactic and get_intelligence(warlord['name']) >= TACTICS[tactic]['min_intelligence']:
                    tactic_guys.append(warlord)
        if len(tactic_guys) > 1:
            for warlord in tactic_guys[0:-1]:
                dialog += "{}, ".format(warlord['name'].title())
        if len(tactic_guys) > 0:
            dialog += "{} learned the {} tactic. ".format(tactic_guys[-1]['name'].title(), tactic.title())
        tactician = self.game.get_tactician()
        if tactician:
            dialog += "{}'s tactical ability increased to {}.".format(
                tactician['name'].title(), get_max_tactical_points(tactician['name'], level),
            )
        self.right_dialog = create_prompt(dialog)
        return True

    def handle_input_lose(self, pressed):
        if self.right_dialog:
            self.right_dialog.handle_input(pressed)
            if (pressed[K_x] or pressed[K_z]) and not self.right_dialog.has_more_stuff_to_show():
                self.right_dialog.shutdown()
                self.game.set_screen_state('title')

    def handle_input_menu(self, pressed):
        self.menu.handle_input(pressed)
        if pressed[K_x]:
            self.select_sound.play()
            choice = self.menu.get_choice()
            if choice == 'RETREAT':
                self.handle_retreat()
            elif choice == 'REPORT':
                self.handle_report()
            elif choice == 'RISK-IT':
                self.handle_risk_it()
            elif choice == 'ALL-OUT':
                self.handle_all_out()
            elif choice == 'BATTLE':
                self.handle_battle()
            elif choice == 'DEFEND':
                self.handle_defend()
            elif choice == 'ITEM':
                self.handle_item()
            elif choice == 'TACTIC':
                self.handle_tactic()
        elif pressed[K_z]:
            warlord = self.get_previous_live_ally_before(self.warlord, nowrap=True)
            self.warlord.move_back()
            self.menu = None
            self.portrait = None
            if warlord:
                move = self.submitted_moves.pop()
                if 'tactic' in move:
                    move['agent'].restore_tactical_points(TACTICS[move['tactic']]['tactical_points'])
                self.warlord = warlord
            self.init_menu_state()

    def handle_tactic(self):
        tactic_menu = self.warlord.get_tactic_menu()
        if tactic_menu:
            self.state = 'tactic'
            self.menu = tactic_menu
            self.menu.focus()
        else:
            self.menu.unfocus()
            self.right_dialog = create_prompt(
                "You do not have an assigned tactician who knows any tactics."
            )
            self.state = 'error'

    def handle_item(self):
        self.state = 'item'
        self.menu = self.warlord.get_item_menu()
        self.menu.focus()

    def handle_defend(self):
        self.state = 'defend'
        self.menu = None
        self.warlord.move_back()
        self.portrait = None
        self.submit_move({'agent': self.warlord, 'action': self.execute_move_defend})

    def handle_battle(self):
        self.state = 'battle'
        self.selected_enemy_index = self.get_first_live_enemy_index()
        self.menu.unfocus()

    def handle_all_out(self):
        self.warlord.move_back()
        self.state = 'all_out'
        self.menu.unfocus()
        self.portrait = None
        self.all_out_state = 'move_back_leader'

    def handle_risk_it(self):
        self.warlord.move_back()
        self.state = 'risk_it'
        self.menu.unfocus()
        time.sleep(1)

    def handle_input_report(self, pressed):
        if pressed[K_UP]:
            self.switch_sound.play()
            self.selected_enemy_index = self.get_previous_live_enemy_index()
        elif pressed[K_DOWN]:
            self.switch_sound.play()
            self.selected_enemy_index = self.get_next_live_enemy_index()
        elif pressed[K_z]:
            self.state = 'menu'
            self.menu.focus()
            self.selected_enemy_index = None
        elif pressed[K_x]:
            self.state = 'report_selected'
            self.report = Report(stats=self.enemies[self.selected_enemy_index].stats)
            self.selected_enemy_index = None

    def handle_input(self, pressed):
        if pressed[K_d]:
            self.debug = not self.debug
        if self.state == 'start':
            self.handle_input_start(pressed)
        elif self.state == 'menu':
            self.handle_input_menu(pressed)
        elif self.state == 'report':
            self.handle_input_report(pressed)
        elif self.state == 'report_selected':
            self.handle_input_report_selected(pressed)
        elif self.state == 'win':
            self.handle_input_win(pressed)
        elif self.state == 'lose':
            self.handle_input_lose(pressed)
        elif self.state == 'all_out':
            self.handle_input_all_out(pressed)
        elif self.state == 'battle':
            self.handle_input_battle(pressed)
        elif self.state == 'execute':
            self.handle_input_execute(pressed)
        elif self.state == 'item':
            self.handle_input_item(pressed)
        elif self.state == 'error':
            self.handle_input_error(pressed)
        elif self.state == 'tactic':
            self.handle_input_tactic(pressed)
        elif self.state == 'tactic_enemy':
            self.handle_input_tactic_enemy(pressed)
        elif self.state == 'tactic_ally':
            self.handle_input_tactic_ally(pressed)
        elif self.state == 'item_ally':
            self.handle_input_item_ally(pressed)

    def handle_input_tactic(self, pressed):
        self.menu.handle_input(pressed)
        if pressed[K_z]:
            self.init_menu_state()
        elif pressed[K_x]:
            self.select_sound.play()
            tactic = self.menu.get_choice().lower().strip('~')
            cost = TACTICS[tactic]['tactical_points']
            if cost > self.warlord.get_tactical_points():
                self.state = 'error'
                self.right_dialog = create_prompt("Insufficient tactical points.")
            elif TACTICS[tactic]['slot'] == 2 and not self.near_water:
                self.state = 'error'
                self.right_dialog = create_prompt("Sorry, there must be a body of water nearby to do that.")
            else:
                if TACTICS[tactic]['type'] == 'ally':
                    self.state = 'tactic_ally'
                    self.selected_ally_index = self.get_leader().index
                elif TACTICS[tactic]['type'] == 'enemy':
                    self.state = 'tactic_enemy'
                    self.selected_enemy_index = self.get_enemy_leader().index
                else:
                    self.submit_move({'agent': self.warlord, 'action': self.execute_move_tactic, 'tactic': tactic})
                    self.warlord.consume_tactical_points(cost)
                    self.do_next_menu()

    def get_enemy_leader(self):
        for enemy in self.enemies:
            if enemy.soldiers > 0:
                return enemy

    def handle_input_error(self, pressed):
        self.right_dialog.handle_input(pressed)
        if pressed[K_x] and not self.right_dialog.has_more_stuff_to_show():
            self.init_menu_state()

    def handle_input_item(self, pressed):
        self.menu.handle_input(pressed)
        if pressed[K_z]:
            self.init_menu_state()
        elif pressed[K_x]:
            self.select_sound.play()
            item = self.menu.get_choice().lower().strip('~')
            if ITEMS[item].get('battle_usage') == 'ally':
                self.state = 'item_ally'
                self.selected_ally_index = self.get_leader().index
            else:
                self.right_dialog = create_prompt("That item cannot be used in battle.")
                self.menu.unfocus()
                self.state = 'error'

    def handle_input_execute(self, pressed):
        dialog = self.left_dialog or self.right_dialog
        if dialog:
            dialog.handle_input(pressed)
            if pressed[K_x] and not dialog.has_more_stuff_to_show():
                if self.warlord is None:
                    self.init_menu_state()
                else:
                    self.execute_state = 'mini_move'
                dialog.shutdown()
                self.left_dialog = None
                self.right_dialog = None

    def handle_input_battle(self, pressed):
        if pressed[K_UP]:
            self.switch_sound.play()
            self.selected_enemy_index = self.get_previous_live_enemy_index()
        elif pressed[K_DOWN]:
            self.switch_sound.play()
            self.selected_enemy_index = self.get_next_live_enemy_index()
        elif pressed[K_z]:
            self.state = 'menu'
            self.menu.focus()
            self.selected_enemy_index = None
        elif pressed[K_x]:
            self.submit_move({
                'agent': self.warlord,
                'target': self.enemies[self.selected_enemy_index],
                'action': self.execute_move_battle,
            })
            self.select_sound.play()
            self.do_next_menu()

    def handle_input_item_ally(self, pressed):
        if pressed[K_UP]:
            self.switch_sound.play()
            self.selected_ally_index = self.get_previous_live_ally_index()
        elif pressed[K_DOWN]:
            self.switch_sound.play()
            self.selected_ally_index = self.get_next_live_ally_index()
        elif pressed[K_z]:
            self.state = 'item'
            self.menu.focus()
            self.selected_ally_index = None
        elif pressed[K_x]:
            item = self.menu.get_choice().lower().strip('~')
            self.submit_move({
                'agent': self.warlord,
                'target': self.allies[self.selected_ally_index],
                'action': self.execute_move_item,
                'item': item,
            })
            self.select_sound.play()
            self.do_next_menu()

    def handle_input_tactic_ally(self, pressed):
        if pressed[K_UP]:
            self.switch_sound.play()
            self.selected_ally_index = self.get_previous_live_ally_index()
        elif pressed[K_DOWN]:
            self.switch_sound.play()
            self.selected_ally_index = self.get_next_live_ally_index()
        elif pressed[K_z]:
            self.state = 'tactic'
            self.menu.focus()
            self.selected_ally_index = None
        elif pressed[K_x]:
            tactic = self.menu.get_choice().lower().strip('~')
            self.submit_move({
                'agent': self.warlord,
                'target': self.allies[self.selected_ally_index],
                'action': self.execute_move_tactic,
                'tactic': tactic,
            })
            self.warlord.consume_tactical_points(TACTICS[tactic]['tactical_points'])
            self.select_sound.play()
            self.do_next_menu()

    def handle_input_tactic_enemy(self, pressed):
        if pressed[K_UP]:
            self.switch_sound.play()
            self.selected_enemy_index = self.get_previous_live_enemy_index()
        elif pressed[K_DOWN]:
            self.switch_sound.play()
            self.selected_enemy_index = self.get_next_live_enemy_index()
        elif pressed[K_z]:
            self.state = 'tactic'
            self.menu.focus()
            self.selected_enemy_index = None
        elif pressed[K_x]:
            tactic = self.menu.get_choice().lower()
            self.submit_move({
                'agent': self.warlord,
                'target': self.enemies[self.selected_enemy_index],
                'action': self.execute_move_tactic,
                'tactic': tactic,
            })
            self.warlord.consume_tactical_points(TACTICS[tactic]['tactical_points'])
            self.select_sound.play()
            self.do_next_menu()

    def do_next_menu(self):
        self.warlord.move_back()
        current_warlord = self.warlord
        self.warlord = self.get_next_live_ally_after(self.warlord, nowrap=True)
        self.selected_enemy_index = None
        self.selected_ally_index = None
        if self.warlord:
            self.init_menu_state()
        else:
            self.warlord = current_warlord
            self.init_execute_state()

    def init_execute_state(self):
        self.state = 'execute'
        self.execute_state = 'move_back'
        self.menu = None
        self.portrait = None
        self.submit_ai_moves(include_allies=False)

    def handle_input_all_out(self, pressed):
        if pressed[K_z]:
            self.cancel_all_out = True

    def handle_input_report_selected(self, pressed):
        if pressed[K_x] or pressed[K_z]:
            self.state = 'menu'
            self.menu.focus()
            self.report = None

    def get_next_live_ally_after(self, warlord, nowrap=False):
        if warlord is None:
            return self.get_leader()
        found = False
        index = warlord.index
        while not found:
            index += 1
            if index >= len(self.allies):
                if nowrap:
                    return None
                else:
                    index = 0
            ally = self.allies[index]
            if ally.soldiers == 0:
                continue
            found = True
        return ally

    def get_previous_live_ally_before(self, warlord, nowrap=False):
        if warlord is None:
            return self.get_leader()
        found = False
        index = warlord.index
        while not found:
            index -= 1
            if index < 0:
                if nowrap:
                    return None
                else:
                    index = len(self.allies)-1
            ally = self.allies[index]
            if ally.soldiers == 0:
                continue
            found = True
        return ally

    def get_next_live_enemy_index(self):
        if self.selected_enemy_index is None:
            return self.get_first_live_enemy_index()
        found = False
        index = self.selected_enemy_index
        while not found:
            index += 1
            if index >= len(self.enemies):
                index = 0
            enemy = self.enemies[index]
            if enemy.soldiers == 0:
                continue
            found = True
        return index

    def get_previous_live_enemy_index(self):
        if self.selected_enemy_index is None:
            return self.get_first_live_enemy_index()
        found = False
        index = self.selected_enemy_index
        while not found:
            index -= 1
            if index < 0:
                index = len(self.enemies)-1
            enemy = self.enemies[index]
            if enemy.soldiers == 0:
                continue
            found = True
        return index

    def get_next_live_ally_index(self):
        if self.selected_ally_index is None:
            return self.get_first_live_ally_index()
        found = False
        index = self.selected_ally_index
        while not found:
            index += 1
            if index >= len(self.allies):
                index = 0
            ally = self.allies[index]
            if ally.soldiers == 0:
                continue
            found = True
        return index

    def get_previous_live_ally_index(self):
        if self.selected_ally_index is None:
            return self.get_first_live_ally_index()
        found = False
        index = self.selected_ally_index
        while not found:
            index -= 1
            if index < 0:
                index = len(self.allies)-1
            ally = self.allies[index]
            if ally.soldiers == 0:
                continue
            found = True
        return index

    def handle_report(self):
        self.state = 'report'
        self.menu.unfocus()
        self.selected_enemy_index = self.get_first_live_enemy_index()

    def get_first_live_enemy_index(self):
        for i, enemy in enumerate(self.enemies):
            if enemy.soldiers > 0:
                return i
        return None

    def get_first_live_ally_index(self):
        for i, ally in enumerate(self.allies):
            if ally.soldiers > 0:
                return i
        return None

    def handle_retreat(self):
        self.state = 'retreat'
        self.warlord.move_back()
        self.right_dialog = create_prompt("{}'s army retreated.".format(self.get_leader().name.title()))
        self.warlord = None

    def create_menu(self):
        first_column = ['BATTLE', 'TACTIC', 'DEFEND', 'ITEM']
        if self.warlord == self.get_leader():
            choices = [first_column, ['ALL-OUT', 'RETREAT', 'REPORT', 'RISK-IT']]
        else:
            choices = [first_column]
        self.menu = MenuGrid(choices, border=True)
        self.menu.focus()

    def get_leader(self):
        for ally in self.allies:
            if ally.soldiers > 0:
                return ally
        assert False, 'should not call this function if everyone is dead'

    def draw(self):
        self.screen.fill(BLACK)
        
        # If showing a report, we don't need to show anything else.
        if self.report:
            self.screen.blit(self.report.surface, (0,0))
            return

        top_margin = 16
        for i, ally in enumerate(self.allies):
            ally.draw()
            self.screen.blit(ally.surface, (0, i*24+top_margin))
        for i, enemy in enumerate(self.enemies):
            enemy.draw()
            self.screen.blit(enemy.surface, (GAME_WIDTH/2, i*24+top_margin))
        if self.portrait:
            self.screen.blit(self.portrait, self.get_portrait_position())
        if self.left_dialog:
            self.screen.blit(self.left_dialog.surface, (0, 128+top_margin))
        if self.menu:
            self.screen.blit(self.menu.surface, (64, 128 + top_margin))
        if self.right_dialog:
            self.screen.blit(self.right_dialog.surface, (GAME_WIDTH-self.right_dialog.width, 128+top_margin))
        if self.selected_enemy_index is not None:
            self.screen.blit(self.pointer_right, (GAME_WIDTH-96, self.selected_enemy_index*24+top_margin))
        if self.selected_ally_index is not None:
            self.screen.blit(self.pointer_left, (96, self.selected_ally_index*24+top_margin))
        if self.state == 'win' and self.exit_dialog:
            self.screen.blit(self.exit_dialog.surface, (0, 128 + top_margin))
            self.screen.blit(self.portraits[self.enemies[0].name], (GAME_WIDTH-64, 160))
        if self.state == 'win' and not self.exit_dialog and self.narration:
            self.screen.blit(self.narration.surface, (0, 128 + top_margin))
        if self.confirm_box:
            self.screen.blit(self.confirm_box.surface, (GAME_WIDTH-self.right_dialog.width, 80+top_margin))

    def get_portrait_position(self):
        return ((16 if self.is_ally_turn() else GAME_WIDTH-64), 160)

    def is_ally_turn(self):
        if not self.warlord:
            return True
        return self.warlord in self.allies
