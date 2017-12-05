import copy, logging
from common.user import User
gLogger = logging.getLogger("game." + __name__.split(".")[-1])


class Game:
    def __init__(self):
        self.row = 25
        self.col = 25

        self.map = [[0 for j in range(self.col)] for i in range(self.row)]

        self.commands = []
        self.users = []
        self.is_server = False
        self.up = True


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
            gLogger.info("New user added [{}] to the map at [{},{}]".format(p, r, c))
            return True
        else:
            gLogger.error("Failed to add user. Position full at [{},{}]".format(r, c))
            return False

    def remove_user(self, r, c):
        if self.map[r][c] == 0:
            gLogger.error("Failed to remove user. cell empty [{},{}]".format(r, c))
            return False
        else:
            gLogger.info("Removed user [{}] from [{},{}]".format(self.map[r][c], r, c))
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

    def from_serialized_map(self, _map):
        for i in range(len(_map)):
            for j in range(len(_map[0])):
                if _map[i][j] != 0:
                    user_dict = _map[i][j]
                    user_obj = User(user_dict['type'])
                    for (key, val) in user_dict.items():
                        setattr(user_obj, key, val)
                    self.map[i][j] = user_obj
                    self.users.append(user_obj)