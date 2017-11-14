import sys
import random
from common.constants import USERS

class User:
    def __init__(self, type):
        if type == USERS.DRAGON:
            self.hp = random.randint(50, 100)
            self.ap = random.randint(5, 20)

        elif type == USERS.PLAYER:
            self.hp = random.randint(10, 20)
            self.ap = random.randint(1, 10)

        else:
            print("Wrong player type")
            sys.exit()

        self.pos = []
        self.MAX_HP = self.hp
        self.type = type
        self.id = random.randint(0, 1000)

    def __str__(self):
        return self.type + '(' + str(self.hp) + ')'