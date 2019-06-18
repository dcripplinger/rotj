from constants import BLACK


class PauseMenu(object):
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game

    def draw(self):
        self.screen.fill(BLACK)

    def update(self, dt):
        pass

    def handle_input(self, pressed):
        pass