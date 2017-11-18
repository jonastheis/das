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

    def epoch(self, response_queue=None):
        """
        applies one command to the game object and map
        will cause that command to be removed from the list
        :return: Status of the applied commands
        """
        if len(self.commands):
            command = self.commands[0]
            status = command.apply(self, response_queue)

            self.commands = self.commands[1:]

            return status or False

        else:
            return False


    def mega_epoch(self, log=True, response_queue=None):
        """
        same as epoch() but will run all commands in the command queue
        previous name: emulate_all()
        :return: a list of failed commands
        """
        i = 1
        errs = []
        while len(self.commands):
            command_to_apply = self.commands[0]
            i += 1
            status = self.epoch(response_queue)
            if not status:
                errs.append(command_to_apply)

            if log:
                print("###Epoch {0}".format(i))
                print(command_to_apply)
                print(self)

        return errs

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