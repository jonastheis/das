from common.constants import *
import copy

from common.user import User


class Game:
    def __init__(self):
        self.row = 5
        self.col = 5

        self.map = [[0 for j in range(self.col)] for i in range(self.row)]

        self.commands = []
        self.users = []
        self.is_server = False


    def __str__(self):
        _str = ""
        for i in range(self.row):
            for j in range(self.col):
                _str += str(self.map[i][j])
                _str += "\t"
            _str += "\n"
        return _str

    def add_user(self, p, r=-1, c=-1):
        if r == -1 and c == -1:
            for i in range(self.row):
                broken = False
                for j in range(self.col):
                    if self.map[i][j] == 0:
                        r, c = i, j
                        broken = True
                        break
                if broken : break

        if self.map[r][c] == 0:
            self.map[r][c] = p
            p.pos = [r, c]
            self.users.append(p)
            return True
        else:
            return False

    def remove_user(self, r, c):
        if self.map[r][c] == 0:
            return False
        else:
            self.users.remove(self.map[r][c])
            self.map[r][c] = 0
            return True

    def remove_user_by_id(self, user_id):
        for i in range(self.row):
            for j in range(self.col):
                if self.map[i][j] != 0 and self.map[i][j].id == user_id:
                    self.remove_user(i, j)

    def serialize(self):
        _map = copy.deepcopy(self.map)
        for i in range(self.row):
            for j in range(self.col):
                if _map[i][j] != 0:
                    _map[i][j] = (_map[i][j]).to_json()
        return _map

    def from_serialized_map(self, _map, id):
        for i in range(len(_map)):
            for j in range(len(_map[0])):
                if _map[i][j] != 0:
                    user_dict = _map[i][j]
                    user_obj = User(user_dict['type'])
                    for (key, val) in user_dict.items():
                        setattr(user_obj, key, val)
                    self.map[i][j] = user_obj
                    self.users.append(user_obj)