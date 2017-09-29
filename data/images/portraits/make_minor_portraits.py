import itertools
import subprocess
import random

random.seed(1)

features = {
    'fighters': [
        {
            'name': 'body',
            'count': 1,
        },
        {
            'name': 'mouth',
            'count': 3,
        },
        {
            'name': 'eyes',
            'count': 5,
        },
        {
            'name': 'nose',
            'count': 4,
        },
        {
            'name': 'shoulders',
            'count': 5,
        },
        {
            'name': 'helmet',
            'count': 4,
        },
        {
            'name': 'eyebrows',
            'count': 4,
        },
        {
            'name': 'facial_hair',
            'count': 6,
        },
    ],
    'strategists': [
        {
            'name': 'body',
            'count': 1,
        },
        {
            'name': 'mouth',
            'count': 3,
        },
        {
            'name': 'eyes',
            'count': 4,
        },
        {
            'name': 'nose',
            'count': 4,
        },
        {
            'name': 'shoulders',
            'count': 4,
        },
        {
            'name': 'helmet',
            'count': 4,
        },
        {
            'name': 'eyebrows',
            'count': 3,
        },
        {
            'name': 'facial_hair',
            'count': 3,
        },
    ],
}


def get_combinations(features):
    ranges = [range(1, feature['count']+1) for feature in features]
    return itertools.product(*ranges)


def format_combo(combo):
    string = ''
    for number in combo:
        string = '{}{:02d}'.format(string, number)
    return string


def i_dont_like_this_combo(combo, is_dark, is_strategist):
    if not is_strategist:
        # eyebrows_01 with helmet_03
        if combo[6]==1 and combo[5]==3:
            return True
        # helmet_03 with shoulders_01
        if combo[5]==3 and combo[4]==1:
            return True
        # helmet_04 with shoulders_01
        if combo[5]==4 and combo[4]==1:
            return True
        # nose_02 with facial_hair_03
        if combo[3]==2 and combo[7]==3:
            return True
        # helmet_01 with shoulders_03
        if combo[5]==1 and combo[4]==3:
            return True
        # facial_hair_05 with shoulders_02
        if combo[7]==5 and combo[4]==2:
            return True
        # facial_hair_06 with shoulders_02
        if combo[7]==6 and combo[4]==2:
            return True
        # facial_hair_01 with helmet_01
        if combo[7]==1 and combo[5]==1:
            return True
        # facial_hair_05 with helmet_01
        if combo[7]==5 and combo[5]==1:
            return True
        # facial_hair_06 with helmet_01
        if combo[7]==6 and combo[5]==1:
            return True
        # facial_hair_01 with helmet_02
        if combo[7]==1 and combo[5]==2:
            return True
        # facial_hair_02 with mouth_02
        if combo[7]==2 and combo[1]==2:
            return True
        # facial_hair_04 with mouth_03
        if combo[7]==4 and combo[1]==3:
            return True
        # facial_hair_04 with mouth_02
        if combo[7]==4 and combo[1]==2:
            return True
        # facial_hair_02 with mouth_03
        if combo[7]==2 and combo[1]==3:
            return True
        # shoulders_03 with helmet_01
        if combo[4]==3 and combo[5]==1:
            return True
        # shoulders_03 with helmet_02
        if combo[4]==3 and combo[5]==2:
            return True
        # mouth_01 with eyes_05
        if combo[1]==1 and combo[2]==5:
            return True
        # dark: helmet_02 with shoulders_01
        if is_dark and combo[5]==2 and combo[4]==1:
            return True
    return False

for warlord_type in ['fighters', 'strategists']:
    for skin in ['light', 'dark']:
        for combo in get_combinations(features[warlord_type]):
            if i_dont_like_this_combo(combo, is_dark=(skin=='dark'), is_strategist=(warlord_type=='strategists')):
                continue
            arg_list = ['convert',]
            random_background_number = random.randrange(1, 6+1)
            arg_list.append('features/background_{:02d}.png'.format(random_background_number))
            for i, feature in enumerate(features[warlord_type]):
                arg_list.append('features/{}/{}/{}_{:02d}.png'.format(warlord_type, skin, feature['name'], combo[i]))
            arg_list.append('-background')
            arg_list.append('none')
            arg_list.append('-flatten')
            arg_list.append('minor/{}/{}/{}.png'.format(warlord_type, skin, format_combo(combo)))
            subprocess.call(arg_list)
