# -*- coding: UTF-8 -*-

import random

import pygame
from pygame.locals import *

from battle_warlord_rect import Ally, Enemy
from constants import BLACK, GAME_WIDTH, GAME_HEIGHT, TACTICS
from helpers import (
    get_equip_based_stat_value, get_max_soldiers, get_max_tactical_points, get_tactics, load_image, load_stats,
)
from report import Report
from text import create_prompt, MenuGrid

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


class Battle(object):
    def __init__(self, screen, game, allies, enemies, battle_type):
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
            }))
        self.enemies = []
        for i, enemy in enumerate(enemies):
            soldiers = random.choice(enemy['stats']['soldiers'])
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
                'tactics': enemy['stats'].get('tactics', ['','','','','','']),
            }))
        self.state = 'start'
            # potential states: start, menu, action, report, report_selected, retreat, all_out, battle, tactic,
            # tactic_ally, tactic_enemy, item, item_ally, item_enemy, dialog, win, lose, execute, risk_it
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
        self.switch_sound = pygame.mixer.Sound('data/audio/switch.wav')
        self.report = None
        self.submitted_moves = []
        self.enemy_moves = []
        self.good_enemy_statuses = {}
        self.good_ally_statuses = {}
        self.near_water = False

    def set_start_dialog(self):
        script = ''
        for enemy in self.enemies:
            script += '{} approaching.\n'.format(enemy.name.title())
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
                    self.warlord = self.get_next_live_ally_after(self.warlord)
                    if not self.warlord:
                        self.game.end_battle()
        elif self.state == 'risk_it':
            if self.get_leader().state == 'wait':
                self.simulate_battle()
        elif self.state == 'win':
            self.right_dialog.update(dt)
        elif self.state == 'lose':
            self.right_dialog.update(dt)

    def simulate_battle(self):
        while self.state == 'risk_it':
            enemies = self.get_live_enemies()
            for ally in self.get_live_allies():
                move = {'agent': ally, 'action': self.execute_move_battle, 'target': random.choice(enemies)}
                self.submit_move(move)
            self.generate_enemy_moves()
            for move in self.get_moves_in_order_of_agility():
                move = self.change_move_if_dead_or_cursed(move)
                if move is not None:
                    action_handler = move['action']
                    results = action_handler(move)
                    if results.get('killed'):
                        if move['target'] in self.enemies and all(enemy.soldiers == 0 for enemy in self.enemies):
                            self.handle_win()
                            break
                        elif move['target'] in self.allies and all(ally.soldiers == 0 for ally in self.allies):
                            self.handle_lose()
                            break
            self.submitted_moves = []
            self.enemy_moves = []

    def handle_win(self):
        self.state = 'win'
        self.right_dialog = create_prompt('You won the fight!')
        self.menu = None
        self.portrait = None

    def handle_lose(self):
        self.state = 'lose'
        self.right_dialog = create_prompt('Oh no, you lost!')
        self.menu = None
        self.portrait = None

    def get_moves_in_order_of_agility(self):
        the_moves = self.submitted_moves + self.enemy_moves
        the_moves.sort(key=lambda move: move['agent'].agility, reverse=True)
        return the_moves

    def execute_move_battle(self, move):
        is_ally_move = move['agent'] in self.allies
        if move['target'].soldiers == 0:
            targets = self.get_live_enemies() if is_ally_move else self.get_live_allies()
            return self.execute_move_battle({'agent': move['agent'], 'target': random.choice(targets)})
        if 'defend' in move['agent'].boosts:
            del move['agent'].boosts['defend']
        good_target_team_statuses = self.good_enemy_statuses if is_ally_move else self.good_ally_statuses
        if 'repel' in good_target_team_statuses:
            return {'repel': True}
        evade_prob = ((move['target'].evasion - move['agent'].agility) / 255.0 + 1) / 2.0
        if random.random() < evade_prob / 2.0: # divide by 2 so that evades aren't too common
            return {'evade': True}
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
            return {'damage': inflicted_damage, 'killed': True}
        move['target'].get_damaged(inflicted_damage)
        if double_tap:
            if move['target'].soldiers <= double_tap:
                double_tap = move['target'].soldiers
                move['target'].get_damaged(double_tap)
                return {'damage': inflicted_damage, 'double_tap': double_tap, 'killed': True}
            move['target'].get_damaged(double_tap)
            return {'damage': inflicted_damage, 'double_tap': double_tap}
        return {'damage': inflicted_damage}

    def execute_move_confuse(self, move):
        result = execute_move_battle(move)
        result.update({'status': 'confuse'})
        return result

    def execute_move_disable(self, move):
        return {'status': 'disable'}

    def execute_move_provoke(self, move):
        result = execute_move_battle(move)
        result.update({'status': 'provoke'})
        return result

    def execute_move_tactic(self, move):
        return {}

    def execute_move_defend(self, move):
        move['agent'].boosts['defend'] = True
        return {'defend': True}

    def execute_move_item(self, move):
        return {}

    def change_move_if_dead_or_cursed(self, move):
        if move['agent'].soldiers == 0:
            move = None
        elif move['agent'].bad_statuses:
            if 'disable' in move['agent'].bad_statuses:
                move = {'agent': move['agent'], 'action': self.execute_move_disable}
            elif 'confuse' in move['agent'].bad_statuses:
                if move['agent'] in self.allies:
                    random_target = random.choice(self.get_live_allies())
                else:
                    random_target = random.choice(self.get_live_enemies())
                move = {'agent': move['agent'], 'action': self.execute_move_confuse, 'target': random_target}
            else: # provoke
                move = {'agent': move['agent'], 'action': self.execute_move_provoke, 'target': move['agent'].provoker}
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
        heal_tactic = enemy.tactics[2]
        tactical_points = enemy.tactical_points
        heal_cost = TACTICS.get(heal_tactic, {}).get('tactical_points', 0)
        if (
            heal_tactic and heal_cost < tactical_points and enemy.soldiers*1.0/enemy.max_soldiers < .5
            and sum_dangers > enemy.soldiers and random.random() < .8
        ):
            action = {'agent': enemy, 'action': self.execute_move_tactic, 'tactic': heal_tactic}
            if TACTICS[heal_tactic]['type'] == 'ally':
                action.update({'target': enemy})
            return action

        # dispel
        if (
            enemy.tactics[4] == 'dispel'
            and (
                len(self.good_ally_statuses) > 0
                or any([len(enemy.bad_statuses) > 0 for enemy in self.enemies if enemy.soldiers > 0])
            )
            and TACTICS['dispel']['tactical_points'] + heal_cost < tactical_points
            and random.random() < .5
        ):
            return {'agent': enemy, 'action': self.execute_move_tactic, 'tactic': 'dispel'}

        # defense
        defense_tactic = enemy.tactics[3]
        defense_cost = TACTICS.get(defense_tactic, {}).get('tactical_points', 0)
        if (
            defense_tactic and heal_cost + defense_cost < tactical_points
            and defense_tactic not in self.good_enemy_statuses and random.random() < .3
        ):
            return {'agent': enemy, 'action': self.execute_move_tactic, 'tactic': defense_tactic}

        # provoke, disable
        enemy_prob = self.get_enemy_prob(enemy, ally_target)
        if (
            enemy.tactics[4] in ['provoke', 'disable']
            and heal_cost + TACTICS[enemy.tactics[4]]['tactical_points'] < tactical_points
            and enemy.tactics[4] not in ally_target.bad_statuses
            and random.random() < enemy_prob
        ):
            return {
                'agent': enemy, 'action': self.execute_move_tactic, 'tactic': enemy.tactics[4], 'target': ally_target,
            }

        # confuse, assassin
        if (
            enemy.tactics[5] in ['confuse', 'assassin']
            and heal_cost + TACTICS[enemy.tactics[5]]['tactical_points'] < tactical_points
            and enemy.tactics[5] not in ally_target.bad_statuses
            and random.random() < enemy_prob
        ):
            return {
                'agent': enemy, 'action': self.execute_move_tactic, 'tactic': enemy.tactics[5], 'target': ally_target,
            }

        # boost_tactic: ninja, double tap, hulk out
        boost_tactic = enemy.tactics[5]
        if boost_tactic in ['ninja', 'double~tap', 'hulk~out']:
            if (
                (boost_tactic == 'hulk~out' or boost_tactic not in random_enemy.good_statuses)
                and heal_cost + TACTICS[boost_tactic]['tactical_points'] < tactical_points
                and random.random() < .6
            ):
                return {
                    'agent': enemy, 'action': self.execute_move_tactic, 'tactic': boost_tactic, 'target': random_enemy,
                }

        # water
        maybe_do_tactic_damage = enemy.tactic_danger > enemy.get_preliminary_damage()
        if (
            maybe_do_tactic_damage
            and enemy.tactics[1]
            and self.near_water
            and heal_cost + TACTICS[enemy.tactics[1]]['tactical_points'] < tactical_points
            and random.random() < enemy_prob
        ):
            action = {'agent': enemy, 'action': self.execute_move_tactic, 'tactic': enemy.tactics[1]}
            if TACTICS[enemy.tactics[1]]['type'] == 'enemy':
                action.update({'target': ally_target})
            return action

        # fire
        if (
            maybe_do_tactic_damage
            and enemy.tactics[0]
            and heal_cost + TACTICS[enemy.tactics[0]]['tactical_points'] < tactical_points
            and random.random() < enemy_prob
        ):
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
            self.state = 'menu'
            self.left_dialog = None
            self.warlord = self.allies[0]
            self.portrait = self.portraits[self.warlord.name]
            self.create_menu()
            self.warlord.move_forward()

    def handle_input_menu(self, pressed):
        self.menu.handle_input(pressed)
        if pressed[K_x]:
            self.select_sound.play()
            if self.menu.get_choice() == 'RETREAT':
                self.handle_retreat()
            elif self.menu.get_choice() == 'REPORT':
                self.handle_report()
            elif self.menu.get_choice() == 'RISK-IT':
                self.handle_risk_it()

    def handle_risk_it(self):
        self.warlord.move_back()
        self.state = 'risk_it'
        self.menu.unfocus()

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
        if self.state == 'start':
            self.handle_input_start(pressed)
        elif self.state == 'menu':
            self.handle_input_menu(pressed)
        elif self.state == 'report':
            self.handle_input_report(pressed)
        elif self.state == 'report_selected':
            self.handle_input_report_selected(pressed)

    def handle_input_report_selected(self, pressed):
        if pressed[K_x] or pressed[K_z]:
            self.state = 'menu'
            self.menu.focus()
            self.report = None

    def get_next_live_ally_after(self, warlord):
        if warlord is None:
            return self.get_leader()
        found = False
        index = warlord.index
        while not found:
            index += 1
            if index >= len(self.allies):
                index = 0
            ally = self.allies[index]
            if ally.soldiers == 0:
                continue
            found = True
        return ally

    def get_previous_live_ally_before(self, warlord):
        if warlord is None:
            return self.get_leader()
        found = False
        index = warlord.index
        while not found:
            index -= 1
            if index < 0:
                index = len(self.allies)-1
            ally = self.ally[index]
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

    def handle_report(self):
        self.state = 'report'
        self.menu.unfocus()
        self.selected_enemy_index = self.get_first_live_enemy_index()

    def get_first_live_enemy_index(self):
        for i, enemy in enumerate(self.enemies):
            if enemy.soldiers > 0:
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
            choices = first_column
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
            self.screen.blit(self.menu.surface, ((GAME_WIDTH - self.menu.get_width())/2, 128 + top_margin))
        if self.right_dialog:
            self.screen.blit(self.right_dialog.surface, (GAME_WIDTH-self.right_dialog.width, 128+top_margin))
        if self.selected_enemy_index is not None:
            self.screen.blit(self.pointer_right, (GAME_WIDTH-96, self.selected_enemy_index*24+top_margin))

    def get_portrait_position(self):
        return ((16 if self.is_ally_turn() else GAME_WIDTH-64), 160)

    def is_ally_turn(self):
        if not self.warlord:
            return True
        return self.warlord in self.allies
