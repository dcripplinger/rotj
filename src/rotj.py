#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import argparse
import builtins
import ctypes
import os
import sys

import pygame

from game import Game


class PosAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, 'map', None if values[0] == 'None' else values[0])
        x = int(values[1])
        y = int(values[2])
        setattr(namespace, 'position', (x, y))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--devtools', action='store_true', help='enable dev tools in the pause menu')
    parser.add_argument('--pos', nargs=3, action=PosAction, metavar=('MAPNAME', 'X', 'Y'), help='load a game at a specific position')
    args = parser.parse_args()
    if not hasattr(args, 'map'):
        setattr(args, 'map', None)
        setattr(args, 'position', None)
    return args


if __name__ == '__main__':
    args = parse_args()
    if os.name == 'nt':
        ctypes.windll.user32.SetProcessDPIAware()
    pygame.display.init()
    info_object = pygame.display.Info()
    os.environ['SDL_VIDEO_WINDOW_POS'] = "{},{}".format(int(.1*info_object.current_w), int(.1*info_object.current_h))
    screen = pygame.display.set_mode((int(.8*info_object.current_w), int(.8*info_object.current_h)))
    # In Sway we have wait and see what size the window really is (otherwise the
    # game doesn't draw)
    if 'SWAYSOCK' in os.environ:
        swaymsg_output = os.popen(
            # I would expect a race condition, but both of these seem to always 
            # work. Testing for focused is slightly better in the case that 
            # someone is playing several pygames at once
            #'swaymsg -rt get_tree | grep -B 12 pygame | grep -A 4 window_rect'
            '''swaymsg -rt get_tree | grep -A 20 '"focused": true' | grep -A'''
                + '''4 window_rect'''
        ).read().split('\n')[3:5]
        sway_window_size = [
            int(line.split(':')[1].strip(' ,')) for line in swaymsg_output
        ]
        screen = pygame.display.set_mode((*sway_window_size,))
    pygame.mixer.init(frequency=44100)
    try:
        game = Game(screen, args)
        game.run()
    except:
        pygame.quit()
        raise
