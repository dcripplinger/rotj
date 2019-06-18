from pygame.locals import *

from constants import BLACK, GAME_WIDTH
from text import TextBox


class PauseMenu(object):
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.title = TextBox('PAUSE MENU', GAME_WIDTH, 16, adjust='center')

    def draw(self):
        self.screen.fill(BLACK)
        self.screen.blit(self.title.surface, (0, 8))

    def update(self, dt):
        pass

    def handle_input(self, pressed):
        if pressed[K_RETURN]:
            self.game.close_pause_menu()