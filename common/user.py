import sys, random, time
from common.constants import USERS

class User:
    def __init__(self, type, id="NOT_DEFINED"):
        if type == USERS.DRAGON:
            # Users will always be created by server. Hence Id should be given on the fly
            id = "D@{}".format(time.time())
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
        self.id = id

    def __str__(self):
        return "{}@{}({})".format(self.type, self.id[:1], self.hp)

    def to_json(self):
        return self.__dict__
