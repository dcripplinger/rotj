# -*- coding: UTF-8 -*-

import os

from pygame.locals import *

# colors
WHITE = (255,255,255)
BLACK = (0,0,0)
COPPER = (164, 82, 41)
RED = (128, 0, 0)
ORANGE = (255, 106, 0)
BLUE = (15, 125, 255)

# sizes
TILE_SIZE = 16 # pixels
GAME_WIDTH = 256 # pixels (before scaling)
GAME_HEIGHT = 240 # pixels (before scaling)
MAP_WIDTH = 300 # overworld map width in tiles
MAP_HEIGHT = 400 # overworld map height in tiles

DEFAULT_ENCOUNTER_CHANCE = 0.03

_EXP_DIFF_PER_LEVEL = [
    12,
    13,
    15,
    17,
    20,
    23,
    26,
    30,
    35,
    40,
    47,
    54,
    62,
    71,
    83,
    96,
    111,
    128,
    148,
    172,
    200,
    232,
    270,
    314,
    366,
    427,
    498,
    582,
    681,
    797,
    933,
    1094,
    1283,
    1506,
    1770,
    2081,
    2449,
    2883,
    3397,
    4004,
    4722,
    5573,
    6580,
    7772,
    9184,
    10857,
    12840,
    15190,
    17975,
    21276,
    25190,
    29831,
    35333,
    41856,
    49590,
    58761,
    69633,
    82524,
    97805,
    115920,
    137392,
    162842,
    193003,
    228742,
    271087,
    321253,
    380676,
    451054,
    534395,
    633073,
    749890,
    888160,
    1051795,
    1245417,
    1474481,
    1745428,
    2065861,
    2444750,
    2892679,
    3422133,
    4047837,
    4787153,
    5660550,
    6692156,
    7910404,
    9348797,
    11046807,
    13050919,
    15415883,
]

EXP_REQUIRED_BY_LEVEL = {
    1: 0,
}

for (i, exp) in enumerate(_EXP_DIFF_PER_LEVEL):
    level = i + 2
    EXP_REQUIRED_BY_LEVEL[level] = EXP_REQUIRED_BY_LEVEL[level-1] + exp

ATTACK_POINTS = {
    1: 10,
    2: 10,
    3: 15,
    4: 15,
    5: 20,
    6: 20,
    7: 25,
    8: 25,
    9: 30,
    10: 30,
    11: 35,
    12: 35,
    13: 40,
    14: 40,
    15: 45,
    16: 45,
    17: 50,
    18: 50,
    19: 55,
    20: 55,
    21: 60,
    22: 60,
    23: 65,
    24: 65,
    25: 70,
    26: 70,
    27: 75,
    28: 75,
    29: 80,
    30: 80,
    31: 85,
    32: 85,
    33: 90,
    34: 90,
    35: 95,
    36: 95,
    37: 100,
    38: 100,
    39: 105,
    40: 105,
    41: 110,
    42: 110,
    43: 115,
    44: 115,
    45: 120,
    46: 120,
    47: 125,
    48: 125,
    49: 130,
    50: 130,
    51: 135,
    52: 135,
    53: 140,
    54: 140,
    55: 145,
    56: 145,
    57: 150,
    58: 150,
    59: 155,
    60: 155,
    61: 160,
    62: 160,
    63: 165,
    64: 165,
    65: 170,
    66: 170,
    67: 175,
    68: 175,
    69: 180,
    70: 180,
    71: 185,
    72: 185,
    73: 190,
    74: 190,
    75: 195,
    76: 195,
    77: 200,
    78: 200,
    79: 205,
    80: 205,
    81: 210,
    82: 210,
    83: 215,
    84: 215,
    85: 220,
    86: 220,
    87: 225,
    88: 225,
    89: 230,
    90: 230,
    91: 235,
    92: 235,
}

ARMOR_CLASS = {level: min(255, int(value*1.5)) for level, value in ATTACK_POINTS.items()}

MAX_NUM = 99999999 # 99,999,999. Theoretical max num of soldiers, food, money, and exp.

TACTICS = {
    'fire': {
        'min_damage': 40,
        'max_damage': 60,
        'type': 'enemy', # type can be enemy, ally, enemies, allies, defense, single
        'min_intelligence': 100,
        'min_level': 2,
        'success_probability_type': 'enemy_prob2',
            # enemy_prob = ((intel-enemy_intel)/255+1) / 2
            # enemy_prob2 = min( 1, (intel-enemy_intel)/255+1 )
            # one = 1
            # intel_prob = intel/255
            # assassin = enemy_prob/3
        'slot': 1,
        'tactical_points': 2,
        'description': "Fire: Inflicts 40 to 60 fire damage on a single enemy. High success probability, based on INT of user and target. INT required to learn: 100. Level required to learn: 2. T.P cost: 2.",
    },
    'bomb': {
        'min_damage': 70,
        'max_damage': 150,
        'type': 'enemy',
        'min_intelligence': 110,
        'min_level': 9,
        'success_probability_type': 'enemy_prob2',
        'slot': 1,
        'tactical_points': 4,
        'description': "Bomb: Inflicts 70 to 150 fire damage on a single enemy. High success probability, based on INT of user and target. INT required to learn: 110. Level required to learn: 9. T.P cost: 4.",
    },
    'lava': {
        'min_damage': 100,
        'max_damage': 200,
        'type': 'enemies',
        'min_intelligence': 130,
        'min_level': 16,
        'success_probability_type': 'enemy_prob',
        'slot': 1,
        'tactical_points': 6,
        'description': "Lava: Inflicts 100 to 200 fire damage on all enemies. Medium success probability per target, based on INT of user and target. INT required to learn: 130. Level required to learn: 16. T.P cost: 6.",
    },
    'brimstone': {
        'min_damage': 700,
        'max_damage': 1100,
        'type': 'enemy',
        'min_intelligence': 140,
        'min_level': 23,
        'success_probability_type': 'enemy_prob2',
        'slot': 1,
        'tactical_points': 8,
        'description': "Brimstone: Inflicts 700 to 1100 fire damage on a single enemy. High success probability, based on INT of user and target. INT required to learn: 140. Level required to learn: 23. T.P cost: 8.",
    },
    'backdraft': {
        'min_damage': 1500,
        'max_damage': 2500,
        'type': 'enemies',
        'min_intelligence': 150,
        'min_level': 30,
        'success_probability_type': 'enemy_prob',
        'slot': 1,
        'tactical_points': 12,
        'description': "Backdraft: Inflicts 1500 to 2500 fire damage on all enemies. Medium success probability per target, based on INT of user and target. INT required to learn: 150. Level required to learn: 30. T.P cost: 12.",
    },
    'blue~flame': {
        'min_damage': 4000,
        'max_damage': 6000,
        'type': 'enemy',
        'min_intelligence': 160,
        'min_level': 35,
        'success_probability_type': 'enemy_prob2',
        'slot': 1,
        'tactical_points': 16,
        'description': "Blue Flame: Inflicts 4000 to 6000 fire damage on a single enemy. High success probability, based on INT of user and target. INT required to learn: 160. Level required to learn: 35. T.P cost: 16.",
    },
    'volcano': {
        'min_damage': 10000,
        'max_damage': 20000,
        'type': 'enemies',
        'min_intelligence': 170,
        'min_level': 41,
        'success_probability_type': 'enemy_prob',
        'slot': 1,
        'tactical_points': 20,
        'description': "Volcano: Inflicts 10000 to 20000 fire damage on all enemies. Medium success probability per target, based on INT of user and target. INT required to learn: 170. Level required to learn: 41. T.P cost: 20.",
    },
    'napalm': {
        'min_damage': 50000,
        'max_damage': 100000,
        'type': 'enemy',
        'min_intelligence': 180,
        'min_level': 52,
        'success_probability_type': 'enemy_prob2',
        'slot': 1,
        'tactical_points': 24,
        'description': "Napalm: Inflicts 50000 to 100000 fire damage on a single enemy. High success probability, based on INT of user and target. INT required to learn: 180. Level required to learn: 52. T.P cost: 24.",
    },
    'baby~nuke': {
        'min_damage': 1000000,
        'max_damage': 2000000,
        'type': 'enemies',
        'min_intelligence': 190,
        'min_level': 76,
        'success_probability_type': 'enemy_prob',
        'slot': 1,
        'tactical_points': 32,
        'description': "Baby Nuke: Inflicts 1000000 to 2000000 fire damage on all enemies. Medium success probability per target, based on INT of user and target. INT required to learn: 190. Level required to learn: 76. T.P cost: 32.",
    },
    'flood': {
        'min_damage': 60,
        'max_damage': 80,
        'type': 'enemy',
        'min_intelligence': 100,
        'min_level': 3,
        'success_probability_type': 'enemy_prob2',
        'slot': 2,
        'tactical_points': 3,
        'description': "Flood: Inflicts 60 to 80 water damage on a single enemy. High success probability, based on INT of user and target. INT required to learn: 100. Level required to learn: 3. T.P cost: 3.",
    },
    'geyser': {
        'min_damage': 90,
        'max_damage': 200,
        'type': 'enemy',
        'min_intelligence': 115,
        'min_level': 10,
        'success_probability_type': 'enemy_prob2',
        'slot': 2,
        'tactical_points': 6,
        'description': "Geyser: Inflicts 90 to 200 water damage on a single enemy. High success probability, based on INT of user and target. INT required to learn: 115. Level required to learn: 10. T.P cost: 6.",
    },
    'hailstorm': {
        'min_damage': 130,
        'max_damage': 250,
        'type': 'enemies',
        'min_intelligence': 130,
        'min_level': 17,
        'success_probability_type': 'enemy_prob',
        'slot': 2,
        'tactical_points': 9,
        'description': "Hailstorm: Inflicts 130 to 250 water damage on all enemies. Medium success probability per target, based on INT of user and target. INT required to learn: 130. Level required to learn: 17. T.P cost: 9.",
    },
    'monsoon': {
        'min_damage': 600,
        'max_damage': 1000,
        'type': 'enemies',
        'min_intelligence': 145,
        'min_level': 22,
        'success_probability_type': 'enemy_prob',
        'slot': 2,
        'tactical_points': 12,
        'description': "Monsoon: Inflicts 600 to 1000 water damage on all enemies. Medium success probability per target, based on INT of user and target. INT required to learn: 145. Level required to learn: 22. T.P cost: 12.",
    },
    'tsunami': {
        'min_damage': 1800,
        'max_damage': 3000,
        'type': 'enemies',
        'min_intelligence': 160,
        'min_level': 29,
        'success_probability_type': 'enemy_prob',
        'slot': 2,
        'tactical_points': 15,
        'description': "Monsoon: Inflicts 1800 to 3000 water damage on all enemies. Medium success probability per target, based on INT of user and target. INT required to learn: 160. Level required to learn: 29. T.P cost: 15.",
    },
    'blizzard': {
        'min_damage': 8000,
        'max_damage': 15000,
        'type': 'enemies',
        'min_intelligence': 175,
        'min_level': 40,
        'success_probability_type': 'enemy_prob',
        'slot': 2,
        'tactical_points': 21,
        'description': "Monsoon: Inflicts 8000 to 15000 water damage on all enemies. Medium success probability per target, based on INT of user and target. INT required to learn: 175. Level required to learn: 40. T.P cost: 21.",
    },
    'sharknado': {
        'min_damage': 100000,
        'max_damage': 300000,
        'type': 'enemies',
        'min_intelligence': 190,
        'min_level': 59,
        'success_probability_type': 'enemy_prob',
        'slot': 2,
        'tactical_points': 27,
        'description': "Sharknado: Inflicts 100000 to 300000 water damage on all enemies. Medium success probability per target, based on INT of user and target. INT required to learn: 190. Level required to learn: 59. T.P cost: 27.",
    },
    'hurricane': {
        'min_damage': 1000000,
        'max_damage': 4000000,
        'type': 'enemies',
        'min_intelligence': 220,
        'min_level': 78,
        'success_probability_type': 'enemy_prob',
        'slot': 2,
        'tactical_points': 36,
        'description': "Hurricane: Inflicts 1000000 to 4000000 water damage on all enemies. Medium success probability per target, based on INT of user and target. INT required to learn: 220. Level required to learn: 78. T.P cost: 36.",
    },
    'salve': {
        'min_damage': 100,
        'max_damage': 150,
        'type': 'ally',
        'min_intelligence': 100,
        'min_level': 4,
        'success_probability_type': 'one',
        'slot': 3,
        'tactical_points': 3,
        'description': "Salve: Heals 100 to 150 soldiers of one ally. Always successful. INT required to learn: 100. Level required to learn: 4. T.P cost: 3.",
    },
    'cure': {
        'min_damage': 400,
        'max_damage': 700,
        'type': 'ally',
        'min_intelligence': 110,
        'min_level': 11,
        'success_probability_type': 'one',
        'slot': 3,
        'tactical_points': 6,
        'description': "Cure: Heals 400 to 700 soldiers of one ally. Always successful. INT required to learn: 110. Level required to learn: 11. T.P cost: 6.",
    },
    'rejuvenate': {
        'min_damage': 900,
        'max_damage': 1500,
        'type': 'allies',
        'min_intelligence': 120,
        'min_level': 18,
        'success_probability_type': 'one',
        'slot': 3,
        'tactical_points': 9,
        'description': "Rejuvenate: Heals 900 to 1500 soldiers of all allies. Always successful. INT required to learn: 120. Level required to learn: 18. T.P cost: 9.",
    },
    'restore': {
        'min_damage': 1000000000,
        'max_damage': 1000000001,
        'type': 'ally',
        'min_intelligence': 180,
        'min_level': 24,
        'success_probability_type': 'one',
        'slot': 3,
        'tactical_points': 12,
        'description': "Restore: Heals one ally completely. Always successful. INT required to learn: 180. Level required to learn: 24. T.P cost: 12.",
    },
    'heal': {
        'min_damage': 4000,
        'max_damage': 6000,
        'type': 'allies',
        'min_intelligence': 140,
        'min_level': 28,
        'success_probability_type': 'one',
        'slot': 3,
        'tactical_points': 4,
        'description': "Heal: Heals 4000 to 6000 soldiers of all allies. Always successful. INT required to learn: 140. Level required to learn: 28. T.P cost: 4.",
    },
    'healmore': {
        'min_damage': 40000,
        'max_damage': 60000,
        'type': 'allies',
        'min_intelligence': 150,
        'min_level': 45,
        'success_probability_type': 'one',
        'slot': 3,
        'tactical_points': 8,
        'description': "Healmore: Heals 40000 to 60000 soldiers of all allies. Always successful. INT required to learn: 150. Level required to learn: 45. T.P cost: 8.",
    },
    'arise': {
        'min_damage': 400000,
        'max_damage': 600000,
        'type': 'allies',
        'min_intelligence': 170,
        'min_level': 61,
        'success_probability_type': 'one',
        'slot': 3,
        'tactical_points': 12,
        'description': "Arise: Heals 400000 to 600000 soldiers of all allies. Always successful. INT required to learn: 170. Level required to learn: 61. T.P cost: 12.",
    },
    'revive': {
        'min_damage': 1000000000,
        'max_damage': 1000000001,
        'type': 'allies',
        'min_intelligence': 190,
        'min_level': 80,
        'success_probability_type': 'one',
        'slot': 3,
        'tactical_points': 24,
        'description': "Revive: Heals all allies completely. Always successful. INT required to learn: 190. Level required to learn: 80. T.P cost: 24.",
    },
    'firewall': {
        'type': 'defense',
        'min_intelligence': 100,
        'min_level': 5,
        'success_probability_type': 'one',
        'slot': 4,
        'tactical_points': 4,
        'duration': 'temporary', # can be temporary or permanent. This is for status effects.
        'description': "Firewall: Reduces fire damage inflicted on all allies down to half. Always successful. Duration is temporary, with some chance of it expiring at the end of each volley. INT required to learn: 100. Level required to learn: 5. T.P cost: 4.",
    },
    'extinguish': {
        'type': 'defense',
        'min_intelligence': 120,
        'min_level': 15,
        'success_probability_type': 'one',
        'slot': 4,
        'tactical_points': 8,
        'duration': 'temporary',
        'description': "Extinguish: Reduces fire damage inflicted on all allies down to one. Always successful. Duration is temporary, with some chance of it expiring at the end of each volley. INT required to learn: 120. Level required to learn: 15. T.P cost: 8.",
    },
    'shield': {
        'type': 'defense',
        'min_intelligence': 170,
        'min_level': 26,
        'success_probability_type': 'one',
        'slot': 4,
        'tactical_points': 12,
        'duration': 'temporary',
        'description': "Shield: Reduces physical damage inflicted on all allies down to half. Always successful. Duration is temporary, with some chance of it expiring at the end of each volley. INT required to learn: 170. Level required to learn: 26. T.P cost: 12.",
    },
    'repel': {
        'type': 'defense',
        'min_intelligence': 200,
        'min_level': 37,
        'success_probability_type': 'intel_prob',
        'slot': 4,
        'tactical_points': 16,
        'duration': 'temporary',
        'description': "Repel: Repels all physical attacks from the enemy. Medium success probability, based on INT of user. Duration is temporary, with some chance of it expiring at the end of each volley. INT required to learn: 200. Level required to learn: 37. T.P cost: 16.",
    },
    'deflect': {
        'type': 'defense',
        'min_intelligence': 240,
        'min_level': 50,
        'success_probability_type': 'intel_prob',
        'slot': 4,
        'tactical_points': 20,
        'duration': 'temporary',
        'description': "Deflect: Deflects all tactics from the enemy that target any allies. Medium success probability, based on INT of user. Duration is temporary, with some chance of it expiring at the end of each volley. INT required to learn: 240. Level required to learn: 50. T.P cost: 20.",
    },
    'provoke': {
        'type': 'enemy',
        'min_intelligence': 130,
        'min_level': 6,
        'success_probability_type': 'enemy_prob2',
        'slot': 5,
        'tactical_points': 5,
        'duration': 'permanent',
        'description': "Provoke: Force the target enemy to only do physical attacks on the user. High success probability, based on INT of user and target. If used by you, duration is five turns. If used by an enemy, duration is permanent until the user is defeated. INT required to learn: 130. Level required to learn: 6. T.P cost: 5.",
    },
    'disable': {
        'type': 'enemy',
        'min_intelligence': 160,
        'min_level': 20,
        'success_probability_type': 'enemy_prob',
        'slot': 5,
        'tactical_points': 10,
        'duration': 'permanent',
        'description': "Disable: Force the target enemy to do nothing. Medium success probability, based on INT of user and target. If used by you, duration is five turns. If used by an enemy, duration is permanent until the user is defeated. INT required to learn: 160. Level required to learn: 20. T.P cost: 10.",
    },
    'dispel': {
        'type': 'single',
        'min_intelligence': 160,
        'min_level': 33,
        'success_probability_type': 'intel_prob',
        'slot': 5,
        'tactical_points': 15,
        'description': "Dispel: Remove all bad status effects on allies and all good status effects on enemies. Medium success probability, based on INT of user. INT required to learn: 160. Level required to learn: 33. T.P cost: 15.",
    },
    'plunder': {
        'type': 'single',
        'min_intelligence': 200,
        'min_level': 43,
        'success_probability_type': 'one',
        'slot': 5,
        'tactical_points': 20,
        'description': "Plunder: Steal money from the enemy. You can plunder a net number of one time. So, if the enemy plunders first, you can plunder twice. If you have already plundered more than the enemy, each time the enemy plunders, you can plunder back. Whatever you gain or lose is still in effect if you retreat early. Always successful. INT required to learn: 200. Level required to learn: 43. T.P cost: 20.",
    },
    'train': {
        'type': 'defense',
        'min_intelligence': 245,
        'min_level': 55,
        'success_probability_type': 'one',
        'slot': 5,
        'tactical_points': 25,
        'duration': 'permanent',
        'description': "Train: Earn three times the experience points if you complete the battle. Always successful. INT required to learn: 245. Level required to learn: 55. T.P cost: 25.",
    },
    'surrender': {
        'type': 'single',
        'min_intelligence': 255,
        'min_level': 69,
        'success_probability_type': 'one',
        'slot': 5,
        'tactical_points': 30,
        'description': "Surrender: Immediately retreat from battle. Always successful and you never get overtaken by the enemy, but you lose half your soldiers. INT required to learn: 255. Level required to learn: 69. T.P cost: 30.",
    },
    'ninja': {
        'type': 'ally',
        'min_intelligence': 140,
        'min_level': 7,
        'success_probability_type': 'one',
        'slot': 6,
        'tactical_points': 4,
        'duration': 'permanent',
        'description': "Ninja: Increase AGI of target ally to 255 for duration of battle. Always successful. The effect lasts for the whole battle. INT required to learn: 140. Level required to learn: 7. T.P cost: 4.",
    },
    'double~tap': {
        'type': 'ally',
        'min_intelligence': 220,
        'min_level': 13,
        'success_probability_type': 'one',
        'slot': 6,
        'tactical_points': 6,
        'duration': 'permanent',
        'description': "Double Tap: Target ally has a 75 percent chance of hitting a second time when doing a physical attack. Always successful. The effect lasts for the whole battle. INT required to learn: 220. Level required to learn: 13. T.P cost: 6.",
    },
    'confuse': {
        'type': 'enemy',
        'min_intelligence': 150,
        'min_level': 32,
        'success_probability_type': 'enemy_prob',
        'slot': 6,
        'tactical_points': 6,
        'duration': 'permanent',
        'description': "Confuse: Cause an enemy to only do physical attacks on his own allies. Medium success probability, based on INT of user and target. If used by you, duration is five turns. If used by an enemy, duration is permanent until the user is defeated. INT required to learn: 150. Level required to learn: 32. T.P cost: 6.",
    },
    'assassin': {
        'type': 'enemy',
        'min_damage': 1000000000,
        'max_damage': 1000000001,
        'min_intelligence': 180,
        'min_level': 48,
        'success_probability_type': 'assassin',
        'slot': 6,
        'tactical_points': 10,
        'description': "Assassin: Instantly defeat a single enemy. Low success probability, based on INT of user and target. INT required to learn: 180. Level required to learn: 48. T.P cost: 10.",
    },
    'hulk~out': {
        'type': 'ally',
        'min_intelligence': 240,
        'min_level': 73,
        'success_probability_type': 'one',
        'slot': 6,
        'tactical_points': 6,
        'duration': 'permanent',
        'description': "Hulk Out: Target ally's physical attack damage increases by 50 percent. It can be used twice on an ally to increase the damage by a maximum of 100 percent. Always successful. The effect lasts for the whole battle. INT required to learn: 240. Level required to learn: 73. T.P cost: 6.",
    },
}

REUSABLE_MAP_NAMES = [
    '_inn',
    '_home',
    '_home2',
    '_reserve',
    '_food_shop',
    '_armory',
    '_merchant_shop',
    '_palace',
    '_record_office',
]

MAPS_WITH_RANDOM_ENCOUNTERS = [
    'overworld',
    'tunnels_of_the_north',
    'cave_of_gadianton',
    'sierra_pass',
    'cavity_of_a_rock',
    'passage_to_gid',
    'antum',
    'east_desert_cave',
    'moroni_cave',
    'north_grotto',
    'onidah',
    'south_desert_cave',
    'west_desert_cave',
    'west_grotto',
]

CAVE_MUSIC = {
    'intro': 'data/audio/music/cave_intro.wav',
    'repeat': 'data/audio/music/cave.wav',
}

SHOP_MUSIC = {
    'intro': None,
    'repeat': 'data/audio/music/shop.wav',
}

CITY_MUSIC = {
    'intro': None,
    'repeat': 'data/audio/music/city.wav',
}

CAMP_MUSIC = {
    'intro': None,
    'repeat': 'data/audio/music/camp.wav',
}

JUDGE_MUSIC = {
    'intro': None,
    'repeat': 'data/audio/music/palace.wav',
}

VILLAGE_MUSIC = {
    'intro': None,
    'repeat': 'data/audio/music/menu.wav',
}

MARCH_MUSIC = {
    'intro': None,
    'repeat': 'data/audio/music/march.wav',
}

CREDITS_MUSIC = {
    'intro': os.path.join('data', 'audio', 'music', 'credits_intro.wav'),
    'repeat': os.path.join('data', 'audio', 'music', 'credits_repeat.wav'),
}

PEACE_MUSIC = {
    'intro': None,
    'repeat': os.path.join('data', 'audio', 'music', 'peace.wav'),
    'conditions': {
        'battle90': True, # zemnarihah
        'battle80': True, # giddianhi
        'battle69': True, # tubaloth
    },
}

TRIUMPH_MUSIC = {
    'intro': None,
    'repeat': os.path.join('data', 'audio', 'music', 'triumph.wav'),
    'conditions': {
        'battle90': True, # zemnarihah
        'battle80': True, # giddianhi
        'battle69': True, # tubaloth
    },
}

WANDER_MUSIC = {
    'intro': os.path.join('data', 'audio', 'music', 'wander_intro.wav'),
    'repeat': os.path.join('data', 'audio', 'music', 'wander_repeat.wav'),
    'conditions': {
        "battle55": True, # ammoron
    },
}

RESOLVE_MUSIC = {
    'intro': None,
    'repeat': os.path.join('data', 'audio', 'music', 'resolve.wav'),
    'conditions': {
        'battle71': True, # battle at kishkumen
    },
}

OVERWORLD_MUSIC = [
    PEACE_MUSIC,
    RESOLVE_MUSIC,
    WANDER_MUSIC,
    MARCH_MUSIC,
]

PALACE_MUSIC = [
    TRIUMPH_MUSIC,
    JUDGE_MUSIC,
]

# If a map name is omitted here, the default music should be SHOP_MUSIC.
# The class Game in game.py has a method get_music() that follows this guideline.
MAP_MUSIC = {
    'lehi': CITY_MUSIC,
    'morianton': CITY_MUSIC,
    'manti': CITY_MUSIC,
    'manti_palace': PALACE_MUSIC,
    'antionum': CITY_MUSIC,
    'antionum_palace': PALACE_MUSIC,
    'nephi': CITY_MUSIC,
    'nephi_palace': PALACE_MUSIC,
    'shimnilon': CITY_MUSIC,
    'lemuel': CITY_MUSIC,
    'bountiful': CITY_MUSIC,
    'bountiful_palace': PALACE_MUSIC,
    'noah': CITY_MUSIC,
    'ishmael': CITY_MUSIC,
    'ishmael_palace': PALACE_MUSIC,
    'gideon': CITY_MUSIC,
    'gideon_palace': PALACE_MUSIC,
    'ammonihah': CITY_MUSIC,
    'ammonihah_palace': PALACE_MUSIC,
    'hermounts': CITY_MUSIC,
    'hermounts_palace': PALACE_MUSIC,
    'zarahemla': CITY_MUSIC,
    'zarahemla_palace': PALACE_MUSIC,
    'melek': VILLAGE_MUSIC,
    'siron': VILLAGE_MUSIC,
    'jershon': VILLAGE_MUSIC,
    'house_of_moroni': VILLAGE_MUSIC,
    'melek_empty_house': SHOP_MUSIC,
    'overworld': OVERWORLD_MUSIC,
    'tunnels_of_the_north': CAVE_MUSIC,
    'cave_of_gadianton': CAVE_MUSIC,
    'sierra_pass': CAVE_MUSIC,
    'cavity_of_a_rock': CAVE_MUSIC,
    'passage_to_gid': CAVE_MUSIC,
    'sidom': CAMP_MUSIC,
    'sidom_tent1': CAMP_MUSIC,
    'sidom_tent2': CAMP_MUSIC,
    'minon': CAMP_MUSIC,
    'minon_tent1': CAMP_MUSIC,
    'minon_tent2': CAMP_MUSIC,
    'minon_tent3': CAMP_MUSIC,
    'sebus': CAMP_MUSIC,
    'sebus_tent1': CAMP_MUSIC,
    'sebus_tent2': CAMP_MUSIC,
    'middoni': CAMP_MUSIC,
    'middoni_tent1': CAMP_MUSIC,
    'middoni_tent2': CAMP_MUSIC,
    'middoni_tent3': CAMP_MUSIC,
    'destroyed_ammonihah': {
        'intro': None,
        'repeat': 'data/audio/music/destroyed.wav',
    },
    'gid_perimeter': MARCH_MUSIC,
    'aaron': CITY_MUSIC,
    'amulon': CITY_MUSIC,
    'angola': CITY_MUSIC,
    'ani-anti': CITY_MUSIC,
    'antiparah': CITY_MUSIC,
    'antiparah_perimeter': MARCH_MUSIC,
    'antum': CAVE_MUSIC,
    'boaz': CITY_MUSIC,
    'boaz_palace': PALACE_MUSIC,
    'cumeni': CITY_MUSIC,
    'cumeni_palace': PALACE_MUSIC,
    'desolation': CITY_MUSIC,
    'desolation_palace': PALACE_MUSIC,
    'east_desert_cave': CAVE_MUSIC,
    'east_lamanite_camp': CAMP_MUSIC,
    'east_lamanite_camp_tent1': CAMP_MUSIC,
    'east_lamanite_camp_tent2': CAMP_MUSIC,
    'east_lamanite_camp_tent3': CAMP_MUSIC,
    'gid': CITY_MUSIC,
    'helam': CITY_MUSIC,
    'jashon': CITY_MUSIC,
    'jashon_palace': PALACE_MUSIC,
    'jerusalem': CITY_MUSIC,
    'jerusalem_palace': PALACE_MUSIC,
    'jordan': CITY_MUSIC,
    'joshua': CITY_MUSIC,
    'joshua_palace': PALACE_MUSIC,
    'judea': CITY_MUSIC,
    'judea_palace': PALACE_MUSIC,
    'kishkumen': CITY_MUSIC,
    'midian': CITY_MUSIC,
    'moroni': CITY_MUSIC,
    'moroni_palace': PALACE_MUSIC,
    'moroni_cave': CAVE_MUSIC,
    'mulek': CITY_MUSIC,
    'nephihah': CITY_MUSIC,
    'nephihah_palace': PALACE_MUSIC,
    'north_grotto': CAVE_MUSIC,
    'omner': CITY_MUSIC,
    'onidah': CAVE_MUSIC,
    'shem': CITY_MUSIC,
    'shemlon': CITY_MUSIC,
    'shilom': CITY_MUSIC,
    'south_desert_cave': CAVE_MUSIC,
    'teancum': CITY_MUSIC,
    'teancum_palace': PALACE_MUSIC,
    'west_desert_cave': CAVE_MUSIC,
    'west_grotto': CAVE_MUSIC,
    'west_lamanite_camp': CAMP_MUSIC,
    'west_lamanite_camp_tent1': CAMP_MUSIC,
    'west_lamanite_camp_tent2': CAMP_MUSIC,
    'west_lamanite_camp_tent3': CAMP_MUSIC,
    'zeezrom': CITY_MUSIC,
    'waters_of_mormon': VILLAGE_MUSIC,
}

CAVE_NAMES = [
    'tunnels_of_the_north',
    'cave_of_gadianton',
    'sierra_pass',
    'cavity_of_a_rock',
    'passage_to_gid',
    'antum',
    'east_desert_cave',
    'moroni_cave',
    'north_grotto',
    'onidah',
    'south_desert_cave',
    'west_desert_cave',
    'west_grotto',
]

BATTLE_MUSIC = {
    'regular': {
        'intro': 'data/audio/music/regular_battle_intro.wav',
        'repeat': 'data/audio/music/regular_battle_repeat.wav',
    },
    'warlord': {
        'intro': 'data/audio/music/warlord_battle_intro.wav',
        'repeat': 'data/audio/music/warlord_battle_repeat.wav',
    },
    'story': {
        'intro': 'data/audio/music/story_battle_intro.wav',
        'repeat': 'data/audio/music/story_battle_repeat.wav',
    },
    'giddianhi': {
        'intro': 'data/audio/music/giddianhi_intro.wav',
        'repeat': 'data/audio/music/giddianhi_repeat.wav',
    },
    'zemnarihah': {
        'intro': None,
        'repeat': 'data/audio/music/zemnarihah.wav',
    },
}

WEAPON_POWER = {
    0: 35,
    5: 63,
    10: 69,
    15: 77,
    20: 87,
    25: 100,
    30: 116,
    35: 150,
    40: 180,
    45: 210,
    50: 255,
    55: 330,
    60: 405,
    65: 480,
    70: 660,
    75: 880,
    80: 1097,
    85: 1600,
    90: 2100,
    95: 2600,
    100: 3147,
    105: 4300,
    110: 5500,
    115: 6700,
    120: 8000,
    125: 10000,
    130: 12000,
    135: 14000,
    140: 16000,
    145: 20000,
    150: 24000,
    155: 28000,
    160: 32000,
    165: 40000,
    170: 48000,
    175: 56000,
    180: 64000,
    185: 80000,
    190: 96000,
    195: 112000,
    200: 128000,
    205: 145000,
    210: 164000,
    215: 183000,
    220: 202000,
    225: 221000,
    230: 240000,
    235: 270000,
    240: 300000,
    245: 330000,
    250: 360000,
    255: 430000,
}

ITEMS = {
    # weapons
    'dagger': {
        'attack_points': 10,
        'equip_type': 'weapon',
        'cost': 50,
        'type': 'weapon',
        'description': "Dagger: A small, simple blade. I suppose it's better than nothing. 10 attack points.",
    },
    'mace': {
        'attack_points': 15,
        'equip_type': 'weapon',
        'cost': 100,
        'type': 'weapon',
        'description': "Mace: Just a handle with a spiky ball on the end. Try to get the spiky part stuck in your enemy. 15 attack points.",
    },
    'ax': {
        'attack_points': 20,
        'equip_type': 'weapon',
        'cost': 200,
        'type': 'weapon',
        'description': "Ax: Similar to a woodcutter's ax, but sturdier. A nice upgrade over the clumsy mace. 20 attack points.",
    },
    'club': {
        'attack_points': 30,
        'equip_type': 'weapon',
        'cost': 400,
        'type': 'weapon',
        'description': "Club: It isn't good at cutting, but it can inflict some serious blunt force trauma to your enemy. 30 attack points.",
    },
    'spear': {
        'attack_points': 50,
        'equip_type': 'weapon',
        'cost': 1000,
        'type': 'weapon',
        'description': "Spear: This has a great reach and can pierce through some kinds of armor. 50 attack points.",
        'conditions': {
            'battle05': True,
        },
    },
    'wood~sword': {
        'attack_points': 60,
        'equip_type': 'weapon',
        'cost': 2000,
        'type': 'weapon',
        'description': "Wood Sword: Although it is made of wood, this sword's blade is surprisingly sharp. 60 attack points.",
        'conditions': {
            'battle17': True,
        },
    },
    'macana': {
        'attack_points': 70,
        'equip_type': 'weapon',
        'cost': 4000,
        'type': 'weapon',
        'description': "Macana: This wooden bat of sorts has strategically placed shards of rock, making it quite deadly. 70 attack points.",
        'conditions': {
            'battle17': True,
        },
    },
    'sling': {
        'attack_points': 80,
        'equip_type': 'weapon',
        'cost': 6000,
        'type': 'weapon',
        'description': "Sling: With this weapon, you can hurl stones at the enemy from afar, felling many of them before they even reach within striking distance of you. 80 attack points.",
        'conditions': {
            'battle17': True,
        },
    },
    'atlatl': {
        'attack_points': 100,
        'equip_type': 'weapon',
        'cost': 10000,
        'type': 'weapon',
        'description': "Atlatl: This contraption allows the user to launch spears at the enemy with tremendous speed and accuracy. 100 attack points.",
        'conditions': {
            'battle17': True,
        },
    },
    'lance': {
        'attack_points': 120,
        'equip_type': 'weapon',
        'cost': 20000,
        'type': 'weapon',
        'description': "Lance: With a hand guard and twice the reach of a spear, this weapon makes it difficult for the enemy to parry your thrust or counterattack. 120 attack points.",
        'conditions': {
            'battle49': True,
        },
    },
    'battleax': {
        'attack_points': 140,
        'equip_type': 'weapon',
        'cost': 50000,
        'type': 'weapon',
        'description': "Battleax: Much bigger than a simple ax. Its wide double blade will slice clean through most armor. 140 attack points.",
        'conditions': {
            'battle49': True,
        },
    },
    'cimeter': {
        'attack_points': 160,
        'equip_type': 'weapon',
        'cost': 230000,
        'type': 'weapon',
        'description': "Cimeter: A steel, single edged sword. Its strength, sharpness, and maneuverability give the wielder a distinct advantage. 160 attack points.",
        'conditions': {
            'battle49': True,
        },
    },
    'bow': {
        'attack_points': 180,
        'equip_type': 'weapon',
        'cost': 750000,
        'type': 'weapon',
        'description': "Bow: A bow and arrows will subdue your enemies from a great distance. 180 attack points.",
        'conditions': {
            'battle63': True,
        },
    },
    'sword': {
        'attack_points': 200,
        'equip_type': 'weapon',
        'cost': 1950000,
        'type': 'weapon',
        'description': "Sword: A large, double-edged steel blade. This is the best weapon that can be purchased in shops. 200 attack points.",
        'conditions': {
            'battle71': True,
        },
    },
    'cherev': {
        'attack_points': 230,
        'equip_type': 'weapon',
        'rare': True,
        'type': 'weapon',
        'description': "Cherev: One of four special swords crafted by the swordsmith. Its name is the Hebrew word for sword. 230 attack points.",
        'conditions': {
            'swordsmith_finished': True,
        },
    },
    'samson': {
        'attack_points': 235,
        'equip_type': 'weapon',
        'rare': True,
        'type': 'weapon',
        'description': "Samson: One of four special swords crafted by the swordsmith. Named after the Israelite judge who singlehandedly slew an entire army of Philistines. 235 attack points.",
        'conditions': {
            'swordsmith_finished': True,
        },
    },
    'hamashchit': {
        'attack_points': 240,
        'equip_type': 'weapon',
        'rare': True,
        'type': 'weapon',
        'description': "Hamashchit: One of four special swords crafted by the swordsmith. The name is Hebrew for the destroying angel. 240 attack points.",
        'conditions': {
            'swordsmith_finished': True,
        },
    },
    u'shamshirŕe': { # the ŕ is a hack to show a hyphen without capitalizing the next letter when calling title()
        'attack_points': 245,
        'equip_type': 'weapon',
        'rare': True,
        'type': 'weapon',
        'description': u"Shamshirŕe: One of four special swords crafted by the swordsmith. It is named after the famous sword of King Solomon. 245 attack points.",
        'conditions': {
            'swordsmith_finished': True,
        },
    },
    'sd~of~laban': {
        'attack_points': 255,
        'equip_type': 'weapon',
        'rare': True,
        'type': 'weapon',
        'description': "Sword Of Laban: This legendary sword had been handed down over many generations of kings and was thought to now be lost forever. The swordsmith had patterned his four special swords after this one, but imitations are not quite the same as the original. This is the strongest weapon in existence. 255 attack points.",
        'conditions': {
            'antum_treasure3': True,
        },
    },

    # armor
    'robe': {
        'armor_class': 20,
        'equip_type': 'armor',
        'cost': 50,
        'type': 'armor',
        'description': "Robe: It doesn't really protect you, but it at least keeps you warm. 20 armor class.",
    },
    'leather': {
        'armor_class': 35,
        'equip_type': 'armor',
        'cost': 150,
        'type': 'armor',
        'description': "Leather: Softens the blow of some fairly blunt weapons. 35 armor class.",
    },
    'padded': {
        'armor_class': 45,
        'equip_type': 'armor',
        'cost': 400,
        'type': 'armor',
        'description': "Padded Armor: It gets hot and stuffy in this, but it has several layers of protection against various weapons. 45 armor class.",
        'conditions': {
            'battle05': True,
        },
    },
    'ring~m': {
        'armor_class': 55,
        'equip_type': 'armor',
        'cost': 1000,
        'type': 'armor',
        'description': "Ring Mail: An interlinked mesh of metal rings sewn into a leather fabric. This can stop some direct thrusts of a sharp weapon. 55 armor class.",
        'conditions': {
            'battle17': True,
        },
    },
    'chain~m': {
        'armor_class': 70,
        'equip_type': 'armor',
        'cost': 4000,
        'type': 'armor',
        'description': "Chain Mail: A mesh of heavy-duty metal rings. Though heavier than ring mail, this breathes better and offers significantly greater protection. 70 armor class.",
        'conditions': {
            'battle17': True,
        },
    },
    'splint~m': {
        'armor_class': 85,
        'equip_type': 'armor',
        'cost': 20000,
        'type': 'armor',
        'description': "Splint Mail: This armor consists of long strips of metal attached to a leather backing. These solid splints will stop many blades that less advanced armor will not. 85 armor class.",
        'conditions': {
            'battle17': True,
        },
    },
    'plate~m': {
        'armor_class': 100,
        'equip_type': 'armor',
        'cost': 40000,
        'type': 'armor',
        'description': "Plate Mail: The first in the series of plate armors, this is made of copper plates. It provides solid coverage of almost the entire body, including the hands and feet. 100 armor class.",
        'conditions': {
            'battle49': True,
        },
    },
    'iron~m': {
        'armor_class': 115,
        'equip_type': 'armor',
        'cost': 100000,
        'type': 'armor',
        'description': "Iron Mail: A step up from the copper of plate mail, this armor can take a harder beating. 115 armor class.",
        'conditions': {
            'battle49': True,
        },
    },
    'steel~m': {
        'armor_class': 125,
        'equip_type': 'armor',
        'cost': 900000,
        'type': 'armor',
        'description': "Steel Mail: This mail is made of an alloy of iron and carbon materials, somehow making it both stronger and lighter than iron itself. 125 armor class.",
        'conditions': {
            'battle71': True,
        },
    },
    'tungsten~m': {
        'armor_class': 135,
        'equip_type': 'armor',
        'cost': 2300000,
        'type': 'armor',
        'description': "Tungsten Mail: Tungsten enables this armor to deflect most arrows and blades and even withstand intense heat. 135 armor class.",
        'conditions': {
            'battle71': True,
        },
    },
    'osmium~m': {
        'armor_class': 145,
        'equip_type': 'armor',
        'cost': 9999999,
        'type': 'armor',
        'description': "Osmium Mail: With the rarest metal known to man, this is the strongest armor available. But it doesn't come cheap. 145 armor class.",
        'conditions': {
            'battle71': True,
        },
    },

    # helmets
    'bandana': {
        'armor_class': 10,
        'equip_type': 'helmet',
        'cost': 20,
        'type': 'helmet',
        'description': "Bandana: This does nothing more than keep the sweat out of your eyes. 10 armor class.",
    },
    'cap': {
        'armor_class': 20,
        'equip_type': 'helmet',
        'cost': 100,
        'type': 'helmet',
        'description': "Cap: It doesn't offer much protection, but it can keep you warm during the winter battles. 20 armor class.",
    },
    'hood': {
        'armor_class': 40,
        'equip_type': 'helmet',
        'cost': 300,
        'type': 'helmet',
        'description': "Hood: Made from leather, this is the first headwear that will actually protect you fairly well from some weapons. 40 armor class.",
        'conditions': {
            'battle05': True,
        },
    },
    'wood~h': {
        'armor_class': 50,
        'equip_type': 'helmet',
        'cost': 800,
        'type': 'helmet',
        'description': "Wood Helmet: Made of a considerable thickness of wood, which is good at stopping light blades quite a few times before it is rendered useless. 50 armor class.",
        'conditions': {
            'battle17': True,
        },
    },
    'copper~h': {
        'armor_class': 60,
        'equip_type': 'helmet',
        'cost': 2000,
        'type': 'helmet',
        'description': "Copper Helmet: The first helmet made of a metal substance. This is lighter than a wood helmet and offers just as much protection. 60 armor class.",
        'conditions': {
            'battle17': True,
        },
    },
    'bronze~h': {
        'armor_class': 70,
        'equip_type': 'helmet',
        'cost': 4000,
        'type': 'helmet',
        'description': "Bronze Helmet: Bronze offers a bit more durability to this helmet as compared to copper. 70 armor class.",
        'conditions': {
            'battle17': True,
        },
    },
    'iron~h': {
        'armor_class': 80,
        'equip_type': 'helmet',
        'cost': 15000,
        'type': 'helmet',
        'description': "Iron Helmet: A step up from the bronze helmet, this armor can take a much harder beating. It is quite heavy though. 80 armor class.",
        'conditions': {
            'battle17': True,
        },
    },
    'steel~h': {
        'armor_class': 90,
        'equip_type': 'helmet',
        'cost': 150000,
        'type': 'helmet',
        'description': "Steel Helmet: Made of an alloy of iron and carbon materials, somehow making it both stronger and lighter than iron itself. 90 armor class.",
        'conditions': {
            'battle49': True,
        },
    },
    'tungsten~h': {
        'armor_class': 100,
        'equip_type': 'helmet',
        'cost': 625000,
        'type': 'helmet',
        'description': "Tungsten Helmet: Tungsten enables this helmet to deflect most arrows and blades and even withstand intense heat. 100 armor class.",
        'conditions': {
            'battle71': True,
        },
    },
    'osmium~h': {
        'armor_class': 110,
        'equip_type': 'helmet',
        'cost': 2100000,
        'type': 'helmet',
        'description': "Osmium Helmet: With the rarest metal known to man, this is the strongest helmet available. But it doesn't come cheap. 110 armor class.",
        'conditions': {
            'battle71': True,
        },
    },

    # company items (elixirs, resurrect, etc)
    'elixir~a': {
        'map_usage': 'company', # means you can use the item on a member of the company (aka traveling party)
        'battle_usage': 'ally',
        'healing_points': 200, # exactly 200 soldiers recover strength
        'cost': 10,
        'type': 'heal',
        'description': "Elixir A: Heals 200 soldiers of one ally. Can be used in battle or while traveling.",
    },
    'elixir~b': {
        'map_usage': 'company',
        'battle_usage': 'ally',
        'healing_points': 600,
        'cost': 30,
        'type': 'heal',
        'description': "Elixir B: Heals 600 soldiers of one ally. Can be used in battle or while traveling.",
        'conditions': {
            'battle17': True,
        },
    },
    'elixir~c': {
        'map_usage': 'company',
        'battle_usage': 'ally',
        'healing_points': 2000,
        'cost': 100,
        'type': 'heal',
        'description': "Elixir C: Heals 2000 soldiers of one ally. Can be used in battle or while traveling.",
        'conditions': {
            'battle17': True,
        },
    },
    'elixir~d': {
        'map_usage': 'company',
        'battle_usage': 'ally',
        'healing_points': 6000,
        'cost': 300,
        'type': 'heal',
        'description': "Elixir D: Heals 6000 soldiers of one ally. Can be used in battle or while traveling.",
        'conditions': {
            'battle17': True,
        },
    },
    'elixir~e': {
        'map_usage': 'company',
        'battle_usage': 'ally',
        'healing_points': 20000,
        'cost': 1000,
        'type': 'heal',
        'description': "Elixir E: Heals 20000 soldiers of one ally. Can be used in battle or while traveling.",
        'conditions': {
            'battle17': True,
        },
    },
    'elixir~f': {
        'map_usage': 'company',
        'battle_usage': 'ally',
        'healing_points': 60000,
        'cost': 3000,
        'type': 'heal',
        'description': "Elixir F: Heals 60000 soldiers of one ally. Can be used in battle or while traveling.",
        'conditions': {
            'battle49': True,
        },
    },
    'elixir~g': {
        'map_usage': 'company',
        'battle_usage': 'ally',
        'healing_points': 200000,
        'cost': 10000,
        'type': 'heal',
        'description': "Elixir G: Heals 200000 soldiers of one ally. Can be used in battle or while traveling.",
        'conditions': {
            'battle49': True,
        },
    },
    'elixir~h': {
        'map_usage': 'company',
        'battle_usage': 'ally',
        'healing_points': 600000,
        'cost': 30000,
        'type': 'heal',
        'description': "Elixir H: Heals 600000 soldiers of one ally. Can be used in battle or while traveling.",
        'conditions': {
            'battle49': True,
        },
    },
    'elixir~i': {
        'map_usage': 'company',
        'battle_usage': 'ally',
        'healing_points': 2000000,
        'cost': 100000,
        'type': 'heal',
        'description': "Elixir I: Heals 2000000 soldiers of one ally. Can be used in battle or while traveling.",
        'conditions': {
            'battle71': True,
        },
    },
    'elixir~j': {
        'map_usage': 'company',
        'battle_usage': 'ally',
        'healing_points': 6000000,
        'cost': 300000,
        'type': 'heal',
        'description': "Elixir J: Heals 6000000 soldiers of one ally. Can be used in battle or while traveling.",
        'conditions': {
            'battle71': True,
        },
    },
    'elixir~k': {
        'map_usage': 'company',
        'battle_usage': 'ally',
        'healing_points': 20000000,
        'cost': 1000000,
        'type': 'heal',
        'description': "Elixir K: Heals 20000000 soldiers of one ally. Can be used in battle or while traveling.",
        'conditions': {
            'battle71': True,
        },
    },
    'resurrect': {
        'map_usage': 'company',
        'cost': 50,
        'type': 'heal',
        'description': "Resurrect: Restores one soldier to a fallen warlord. Can only be used while traveling.",
    },

    # battle items
    'power~pill': { # causes a guaranteed excellent hit
        'map_usage': 'battle',
        'battle_usage': 'enemy',
        'effect': 'excellent',
        'cost': 50,
        'type': 'attack',
        'description': "Power Pill: Ensures an excellent physical attack on the target enemy. Can only be used in battle.",
        'conditions': {
            'battle05': True,
        },
    },
    'nightshade': { # item equivalent to dispel, 75% success
        'map_usage': 'battle',
        'battle_usage': 'enemies',
        'effect': 'dispel',
        'cost': 100000,
        'type': 'attack',
        'description': "Nightshade: Remove all bad status effects on allies and all good status effects on enemies. 75 percent success probability.",
        'conditions': {
            'battle71': True,
        },
    },
    'javelin': { # instantly kills enemy if user is teancum, 100% success
        'map_usage': 'battle',
        'battle_usage': 'enemy',
        'effect': 'assassin',
        'cost': 2000,
        'type': 'attack',
        'description': "Javelin: A throwing spear specially crafted for Teancum. This is a single-use item. In battle, have Teancum target an enemy with it, and the enemy will be instantly defeated. Always successful with Teancum, always fails with anyone else. You can buy a replacement javelin from the swordsmith's apprentice.",
        'conditions': {
            'got_javelin': True,
        },
    },
    'remedy': { # cures any negative status ailments on a single ally
        'map_usage': 'battle',
        'battle_usage': 'ally',
        'effect': 'remedy',
        'cost': 100,
        'type': 'heal',
        'description': "Remedy: Use this on an ally to remove all bad status effects. Always successful. Can only be used in battle.",
    },
    't~of~liberty': { # cancels all enemy reinforcements, meant to be used in battle21
        'map_usage': 'battle',
        'battle_usage': 'enemies',
        'effect': 'cancel_reinforcements',
        'rare': True,
        'type': 'attack',
        'description': "Title Of Liberty: Moroni fashioned this banner out of a robe and spear to inspire the Nephites to fight for their freedom. Use it in the battle against Amalickiah at Zarahemla to stop him from receiving reinforcements.",
        'conditions': {
            'got_title_of_liberty': True,
        },
    },
    'ether': { # replenishes tactical points
        'map_usage': 'battle',
        'battle_usage': 'allies',
        'effect': 'ether',
        'rare': True,
        'type': 'heal',
        'description': "Ether: This rare item replenishes all tactical points. Can only be used in battle.",
        'conditions': {
            'west_desert_cave_treasure1': True,
        },
    },

    # kolob (city map usage)
    'kolob': {
        'map_usage': 'city', # means it brings up a menu of main visited cities to teleport to
        'cost': 200,
        'type': 'map',
        'description': "Kolob: Use this to instantly transport to certain major cities. Can only be used while traveling.",
    },

    # cloak (cloak map usage)
    'cloak': {
        'map_usage': 'cloak', # means it prevents random encounters for a finite number of steps
        'cost': 200,
        'type': 'map',
        'description': "Cloak: Use this to avoid random encounters with enemies for some time. Can only be used while traveling.",
        'conditions': {
            'battle17': True,
        },
    },
    's.~cloak': {
        'map_usage': 'cloak',
        'type': 'map',
        'rare': True,
        'description': "Super Cloak: This rare item lasts ten times as long as a cloak. Use it to avoid random encounters with enemies. Can only be used while traveling.",
        'conditions': {
            'state:got_cloak': True,
        },
    },

    # scout
    'scout': {
        'map_usage': 'scout', # enable auto-train and avoid getting caught off guard for a while
        'type': 'map',
        'description': "Scout: You can hire a scout from certain people in the cities of the land northward. To deploy a scout, use him from the ITEM menu. He will go ahead of your army for a while. This makes you automatically use the Train tactic during RISK IT and ALL OUT, if you have the tactic and the requisite tactical points. It also helps you avoid getting caught off guard and always retreat successfully from random encounters.",
        'conditions': {
            'battle71': True,
        },
    },

    # unlock items
    'silver~key': {
        'map_usage': 'unlock', # means it attempts to unlock a locked treasure on the cell/tile you're on
        'cost': 10000,
        'rare': True,
        'type': 'map',
        'description': "Silver Key: You bought this rare key from a shady guy in Bountiful. What does it unlock?",
        'conditions': {
            'bought_key': True,
        },
    },
    'gold~key': {
        'map_usage': 'unlock',
        'rare': True,
        'type': 'map',
        'description': "Gold Key: An old hermit in the city of Moroni wanted you to have this rare key. But what does it unlock?",
        'conditions': {
            'got_gold_key': True,
        },
    },

    # save items
    'g.~plates': { # short for gold plates
        'map_usage': 'save', # means you can use it to save your game anywhere except in battle
        'rare': True,
        'type': 'save',
        'description': "Gold Plates: A former resident of Ammonihah directed you to find these plates in his old home. Use them to save your game almost anywhere. Can only be used while traveling.",
        'conditions': {
            'destroyed_ammonihah_treasure': True,
        },
    },

    # explosive items
    'explosive': {
        'map_usage': 'explosive', # interacts with the wall north of gideon to blow it up
        'rare': True,
        'type': 'map',
        'description': "Explosive: Hagoth gave you this mysterious substance so that you could blow a hole in the wall north of the city of Gideon.",
        'conditions': {
            'got_explosive': True,
        },
    },

    # unusable items (just carrying it has an effect, or it gets used indirectly)
    'liahona': { # lets the user be his own tactician
        'rare': True,
        'type': 'passive',
        'description': "Liahona: An ancient compass that allows the carrier to use his own tactics and tactical points in battle, instead of those of the designated tactician.",
        'conditions': {
            'north_grotto_treasure1': True,
        },
    },
    'horse': { # sometimes a captured general will ask for a horse in exchange for joining you
        'cost': 400,
        'type': 'passive',
        'description': "Horse: Sometimes a captured warlord is willing to join your side if you offer him a horse. It could be handy to always keep one or two with you.",
    },
    'iron~ore': { # Swordsmith asks for it
        'rare': True,
        'type': 'passive',
        'description': "Iron Ore: A deposit of raw iron you found in a cave. Was somebody looking for this?",
        'conditions': {
            'passage_to_gid_treasure1': True,
        },
    },
    'diamond': { # Swordsmith asks for it
        'rare': True,
        'type': 'passive',
        'description': "Diamond: This nugget of sparkling rock was formed from carbon pressurized under the earth for thousands of years. It can cut through even the strongest of metals. Was somebody looking for this?",
        'conditions': {
            'west_lamanite_camp_treasure1': True,
        },
    },
}

STATS = {
    'SOLDIERS': {
        'sort_order': -1,
        'description': "Soldiers: The maximum soldiers of this warlord. If it has a * next to it, the warlord's maximum soldiers will increase as you level up. Note that physical damage inflicted is influenced by how many current soldiers the warlord has. The damage doubles each time the current soldiers reaches a power of ten. 1, 10, 100, 1000, and so on. For example, a warlord with 1000 soldiers will hit twice as hard as when he has 999 soldiers.",
    },
    'STR': {
        'sort_order': 0,
        'description': "Strength: The warlord's inherent physical strength, ranging from 0 to 255. This helps determine damage from physical attacks.",
    },
    'DEF': {
        'sort_order': 1,
        'description': "Defense: The warlord's ability to resist physical attacks, ranging from 0 to 255. A higher defense means that the warlord will take less physical damage.",
    },
    'INT': {
        'sort_order': 2,
        'description': "Intelligence: Ranging from 0 to 255, this is used to determine the effectiveness of tactics.",
    },
    'AGI': {
        'sort_order': 3,
        'description': "Agility: The warlord's ability to take a turn sooner, ranging from 0 to 255. For each volley, warlords take turns in order of their agility, from highest to lowest. Agility also influences the chance of catching the enemy off guard.",
    },
    'EVA': {
        'sort_order': 4,
        'description': "Evasion: The warlord's ability to dodge a physical attack, ranging from 0 to 255.",
    },
    'T.P': {
        'sort_order': 5,
        'description': "Tactical Points: The maximum tactical points for this warlord. If it has a * next to it, the warlord's maximum tactical points will increase as you level up. Each tactic costs a number of tactical points. Your team's current tactical points and available tactics are based on who is chosen as your acting tactician, by choosing FORMATION and STRAT in the command menu. Enemies do not have a team tactician. Instead, each enemy uses his own tactics and tactical points.",
    },
    'A.P': {
        'sort_order': 6,
        'description': "Attack Points: The attack points of the warlord's equipped weapon, ranging from 0 to 255. This greatly influences how much damage is inflicted in physical attacks.",
    },
    'A.C': {
        'sort_order': 7,
        'description': "Armor Class: The combined armor class of the warlord's equipped body armor and helmet, ranging from 0 to 255. This reduces how much damage is received from physical attacks.",
    },
}

MAX_ITEMS_PER_PERSON = 8

FACELESS_ENEMIES = [
    'kingmen',
    'robbers',
    'lamanites',
    'amlicites',
    'zoramites',
    'amalekites',
]

CHAPTER11_CITIES = {
    '144 311': 'helam',
    '175 350': 'amulon',
    '206 346': 'shilom',
    '212 377': 'midian',
    '255 356': 'ani-anti',
    '256 327': 'jerusalem',
    '284 336': 'shemlon',
}

NAMED_TELEPORTS = {
    'zarahemla': [152, 187],
    'manti': [207, 256],
    'bountiful': [116, 138],
    'gid': [164, 114],
    'nephihah': [246, 115],
    'judea': [89, 162],
    'cumeni': [116, 318],
    'moroni': [247, 278],
    'jerusalem': [255, 327],
    'kishkumen': [16, 125],
    'jashon': [101, 43],
    'teancum': [45, 34],
}

# cities that have palaces and record offices, so that you can set up hq there
HQ = [
    'zarahemla',
    'gideon',
    'ishmael',
    'manti',
    'bountiful',
    'nephihah',
    'judea',
    'cumeni',
    'moroni',
    'jerusalem',
    'joshua',
    'jashon',
    'boaz',
    'teancum',
    'desolation',
]

# Used for setting last_overworld_position when loading the game
HQ_LOCATIONS = {
    'zarahemla': [153, 187],
    'gideon': [180, 174],
    'ishmael': [134, 267],
    'manti': [208, 256],
    'bountiful': [117, 138],
    'nephihah': [247, 115],
    'judea': [90, 162],
    'cumeni': [117, 318],
    'moroni': [248, 278],
    'jerusalem': [256, 327],
    'joshua': [58, 90],
    'jashon': [102, 43],
    'boaz': [126, 63],
    'teancum': [46, 34],
    'desolation': [37, 87],
}

MAX_COMPANY_SIZE = 7

# we may or may not reference these
EVENT_NAMES = {
    QUIT: 'QUIT',
    ACTIVEEVENT: 'ACTIVEEVENT',
    KEYDOWN: 'KEYDOWN',
    KEYUP: 'KEYUP',
    MOUSEMOTION: 'MOUSEMOTION',
    MOUSEBUTTONDOWN: 'MOUSEBUTTONDOWN',
    MOUSEBUTTONUP: 'MOUSEBUTTONUP',
    JOYAXISMOTION: 'JOYAXISMOTION',
    JOYBALLMOTION: 'JOYBALLMOTION',
    JOYHATMOTION: 'JOYHATMOTION',
    JOYBUTTONDOWN: 'JOYBUTTONDOWN',
    JOYBUTTONUP: 'JOYBUTTONUP',
    VIDEORESIZE: 'VIDEORESIZE',
    VIDEOEXPOSE: 'VIDEOEXPOSE',
}

START_WITH_SHIZ_MULTIPLIER = 1.5
