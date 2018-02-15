# -*- coding: UTF-8 -*-

from constants import GAME_WIDTH
from text import create_prompt


class Narration(object):
    """
    A black screen with a narration in it meant as a segway in the story. The map should get reloaded after
    transitioning out of this.
    """
    
    def __init__(self, screen, text):
        self.screen = screen
        self.dialog = create_prompt(text)

    def draw(self):
        if self.dialog:
            self.screen.blit(self.dialog.surface, (0, 144))

    def update(self, dt):
        if self.dialog:
            self.dialog.update(dt)

    def handle_input(self, pressed):
        if self.dialog:
            self.dialog.handle_input(pressed)
