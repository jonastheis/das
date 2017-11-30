import time
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError
from .user import User
from common.constants import USERS


class Visualizer(object):
    """
    Displays the game on the terminal in real time.
    Needs to run in the main thread
    """

    def __init__(self, game, id=None):
        self.id = id
        self.game = game

    def visualize(self):
        """
        Wrapper for self._visualize.
        Sets up the screen environment from a asciimatics
        """
        screen = Screen.open()
        restore = True
        try:
            try:
                self._visualize(screen)
            except ResizeScreenError:
                restore = False
                raise
        finally:
            screen.close(restore)

    def _visualize(self, screen):
        """
        Visualizes the game on the screen in real time.
        :param screen: the terminal window
        """
        col = round(screen.width / len(self.game.map))
        row = round(screen.height / len(self.game.map[0]))

        while self.game.up:
            for i in range(0, len(self.game.map)):
                for j in range(0, len(self.game.map[0])):
                    obj = self.game.map[i][j]
                    if type(obj) is User and obj.type == USERS.PLAYER:
                        if self.id and self.id == obj.id:
                            color = Screen.COLOUR_CYAN
                        else:
                            color = Screen.COLOUR_GREEN
                        text = str(obj)
                    elif type(obj) is User and obj.type == USERS.DRAGON:
                        color = Screen.COLOUR_MAGENTA
                        text = str(obj)
                    else:
                        color = Screen.COLOUR_WHITE
                        text = str(obj) + "        "

                    screen.print_at(text, col * i, row * j, colour=color)

            screen.refresh()
            time.sleep(0.3)
