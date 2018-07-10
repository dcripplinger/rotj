#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os

import pygame

from game import Game

os.environ['SDL_VIDEO_WINDOW_POS'] = "100,100"

if __name__ == '__main__':
    pygame.display.init()
    info_object = pygame.display.Info()
    screen = pygame.display.set_mode((int(.8*info_object.current_w), int(.8*info_object.current_h)))
    pygame.mixer.init(frequency=44100)
    try:
        game = Game(screen)
        game.run()
    except:
        pygame.quit()
        raise
