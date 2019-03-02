#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import ctypes
import os

import pygame

from game import Game

if __name__ == '__main__':
    if os.name == 'nt':
        ctypes.windll.user32.SetProcessDPIAware()
    pygame.display.init()
    info_object = pygame.display.Info()
    os.environ['SDL_VIDEO_WINDOW_POS'] = "{},{}".format(int(.1*info_object.current_w), int(.1*info_object.current_h))
    screen = pygame.display.set_mode((int(.8*info_object.current_w), int(.8*info_object.current_h)))
    pygame.mixer.init(frequency=44100)
    try:
        game = Game(screen)
        game.run()
    except:
        pygame.quit()
        raise
