import json, math

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
        Utility Func
        return a user based on its id
        will search the entire map and compare values with the given id
        """
        for i in range(game.row):
            for j in range(game.col):
                if game.map[i][j] != 0 and game.map[i][j].id == id :
                    return game.map[i][j]
        return 0

    def get_distance(self, pos, sop):
        return math.fabs(pos[0] - sop[0]) + math.fabs(pos[1] - sop[1])


class MoveCommand(Command):
    def __init__(self, user_id, value, direction):
        Command.__init__(self, 'move', user_id)
        self.value = value
        self.direction = direction


    def apply(self, game):
        _user = self.get_user_by_id(game, self.user_id)
        _row, _col = _user.pos

        if _user == 0:
            print("No Player Found")
            return False

        # Dragons cannot move
        if _user.type == 'd':
            print("Dragons cannot move")
            return False

        target_row = _row
        target_col = _col

        if self.direction == 'v':
            target_row += self.value
        elif self.direction == 'h':
            target_col += self.value

        # Check if target pos is full
        if game.map[target_row][target_col] != 0:
            print("Position [{}, {}] already full".format(target_row, target_col))
            return False

        # Check if target is in boundaries of the map
        if target_row >= game.row or target_col >= game.col or target_row < 0 or target_col < 0:
            print("Position [{}, {}] out of scope of game".format(target_row, target_col))
            return False

        game.map[_row][_col] = 0
        # update game map
        game.map[target_row][target_col] = _user
        # update user position
        _user.pos = [target_row, target_col]


    def reverse(self, game):
        pass


    def __str__(self):
        return Command.__str__(self) + "[value {} direction {}]".format(self.value, self.direction)


class AttackCommand(Command):
    def __init__(self, user_id, target_id):
        Command.__init__(self, 'attack', user_id)
        self.target_id = target_id

    def apply(self, game):
        attacker = self.get_user_by_id(game, self.user_id)
        target = self.get_user_by_id(game, self.target_id)


        if attacker == 0:
            print("Attacker not found")
            return False

        if target == 0:
            print("Target not found")
            return False

        attacker_row, attacker_col = attacker.pos
        target_row, target_col = target.pos

        distance = self.get_distance([attacker_row, attacker_col], [target_row, target_col])

        if distance > 2:
            print("Attack distance bigger than 2")
            return False

        target.hp -= attacker.ap

        if target.hp <= 0:
            game.remove_user(target_row, target_col)

    def reverse(self, game):
        pass


class HealCommand(Command):
    def __init__(self, user_id, target_id):
        Command.__init__(self, 'heal', user_id)
        self.target_id = target_id

    def apply(self, game):
        healer = self.get_user_by_id(game, self.user_id)

        target = self.get_user_by_id(game, self.target_id)

        if healer == 0:
            print("Healer not found")
            return False

        if target == 0:
            print("Target not found")
            return False

        healer_row, healer_col = healer.pos
        target_row, target_col = target.pos

        distance = self.get_distance([healer_row, healer_col], [target_row, target_col])

        if distance > 5:
            print("Heal distance bigger than 5")
            return

        heal_amount = healer.ap
        target.hp += heal_amount

        if target.hp > target.MAX_HP:
            target.hp = target.MAX_HP

    def reverse(self, game):
        pass





