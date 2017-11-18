import json, math
from common.constants import *

class Command:
    def __init__(self, type, user_id):
        self.type = type
        self.user_id = user_id
        # For future
        self.timestamp = None

    def __str__(self):
        return "Command [{}] applied to {}".format(self.type, self.user_id)

    def apply(self, game):
        pass

    def reverse(self, game):
        pass

    def to_json(self):
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, json_str):
        json_dict = json.loads(json_str)
        return cls(**json_dict)


    def get_user_by_id(self, game, id):
        """
        Utility func
        return a user based on its id
        will search the entire map and compare values with the given id
        """
        for i in range(game.row):
            for j in range(game.col):
                if game.map[i][j] != 0 and game.map[i][j].id == id :
                    return game.map[i][j]
        return 0

    def get_distance(self, pos, sop):
        """
        Utility func
        """
        return math.fabs(pos[0] - sop[0]) + math.fabs(pos[1] - sop[1])




