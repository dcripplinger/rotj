#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import builtins
import ctypes
import os
import sys

import pygame

from game import Game

def _validate_debug_args(args):

    def bail_out():
        print("If you're going to provide debug args")
        print("Usage: rotj.py <map name> <x coord> <y coord>")
        print("Otherwise start rotj with no arguments")
        raise ValueError("Debug args are not correct, see info directly above this stack trace ^^^")

    if len(args) == 1:
        return None

    if len(args[1]) < 3:
        bail_out()
    try:
        x = int(args[2])
        y = int(args[3])
    except:
        bail_out()

    return {"map": args[1], "coords": (x, y)}

if __name__ == '__main__':
    debug_info = _validate_debug_args(sys.argv)
    if os.name == 'nt':
        ctypes.windll.user32.SetProcessDPIAware()
    pygame.display.init()
    info_object = pygame.display.Info()
    os.environ['SDL_VIDEO_WINDOW_POS'] = "{},{}".format(int(.1*info_object.current_w), int(.1*info_object.current_h))
    screen = pygame.display.set_mode((int(.8*info_object.current_w), int(.8*info_object.current_h)))
    pygame.mixer.init(frequency=44100)
    try:
        game = Game(screen, debug_info)
        game.run()
    except:
        pygame.quit()
        raise
