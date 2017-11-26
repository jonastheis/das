import json, math, time
from common.constants import *
from common.user import User


class Command(object):
    """
    The common pattern for each command's apply is as follows:
    They should all return Boolean values indicating if sth went wrong or not
    Each command will optionally override to_json_broadcast
    Note that the generic to_json should NEVER be overriden becasue it is used in the client side to send the message
    to the server
    TODO: currently, only Join, Leave and Move have this patters
    """
    def __init__(self, client_id, timestamp):
        self.type = type(self).__name__
        self.timestamp = timestamp
        self.client_id = client_id

    def apply(self, game):
        pass

    def to_json(self):
        """
        Generic method for converting an object to json
        :return:
        """
        return json.dumps(self.__dict__)

    def to_json_broadcast(self):
        """
        To be used when sending a command from the server to all other clients.
        """
        return self.to_json()

    @classmethod
    def from_json(cls, json_str):
        # TODO: there should be a better way to fix this
        json_data = json.loads(json_str)
        if json_data['type'] == 'MoveCommand':
            command_obj = MoveCommand(
                json_data['client_id'],
                json_data['value'],
                json_data['direction'],
                json_data['timestamp'])

        elif json_data['type'] == 'NewPlayerCommand':
            command_obj = NewPlayerCommand(
                json_data['client_id'],
                json_data['timestamp'],
                json_data['player_dict'])

        elif json_data['type'] == 'PlayerLeaveCommand':
            command_obj = PlayerLeaveCommand(
                json_data['client_id'],
                json_data['timestamp'],
                json_data['is_killed'])

        elif json_data['type'] == 'AttackCommand':
            command_obj = AttackCommand(
                json_data['client_id'],
                json_data['target_id'],
                json_data['timestamp'])

        elif json_data['type'] == 'HealCommand':
            command_obj = HealCommand(
                json_data['client_id'],
                json_data['target_id'],
                json_data['timestamp'])
        else:
            logger.error("Error:: Unrecognized command received. skipping...")
        return command_obj

    def __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items())
        )

    def __repr__(self):
        return self.__str__()

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


class NewPlayerCommand(Command):
    def __init__(self, client_id, timestamp=time.time(), player_dict=None):
        Command.__init__(self, client_id, timestamp)
        self.initial_state = ""
        self.player_dict = player_dict

    def apply(self, game):
        new_user = User(USERS.PLAYER, self.client_id)

        if game.is_server:
            game.add_user(new_user)
            self.player_dict = new_user.to_json()
            self.initial_state = game.serialize()
        else:
            for (key, val) in self.player_dict.items():
                setattr(new_user, key, val)
            game.add_user(new_user, new_user.pos[0], new_user.pos[1])

        return True

    def to_json_broadcast(self):
        dict = self.__dict__.copy()
        del dict["initial_state"]
        return json.dumps(dict)


class PlayerLeaveCommand(Command):
    def __init__(self, client_id, is_killed=False, timestamp=time.time()):
        Command.__init__(self, client_id, timestamp)
        self.is_killed = is_killed

    def apply(self, game):
        game.remove_user_by_id(self.client_id)
        return True


class MoveCommand(Command):
    def __init__(self, client_id, value, direction, timestamp=time.time()):
        Command.__init__(self, client_id, timestamp)
        self.value = value
        self.direction = direction

    def apply(self, game):
        _user = self.get_user_by_id(game, self.client_id)

        if _user == 0:
            logger.error("No Player Found")
            return False

        # Dragons cannot move
        if _user.type == USERS.DRAGON:
            logger.error("Dragons cannot move")
            return False

        _row, _col = _user.pos

        target_row = _row
        target_col = _col

        # make sure only 1 step
        if abs(self.value) != 1:
            logger.error("Invalid step count")
            return False

        if self.direction == DIRECTIONS.V:
            target_row += self.value
        elif self.direction == DIRECTIONS.H:
            target_col += self.value

        # Check if target is in boundaries of the map
        if target_row >= game.row or target_col >= game.col or target_row < 0 or target_col < 0:
            logger.error("Position [{}, {}] out of scope of game".format(target_row, target_col))
            return False

        # Check if target pos is full
        if game.map[target_row][target_col] != 0:
            logger.error("Position [{}, {}] already full".format(target_row, target_col))
            return False

        # update game map
        game.map[_row][_col] = 0
        game.map[target_row][target_col] = _user
        # update user position
        _user.pos = [target_row, target_col]

        return True

    def __str__(self):
        return Command.__str__(self) + "[value {} direction {}]".format(self.value, self.direction)


class AttackCommand(Command):
    def __init__(self, client_id, target_id, timestamp=time.time()):
        Command.__init__(self, client_id, timestamp)
        self.target_id = target_id
        self.user_id = client_id

    def apply(self, game, response_queue=None):
        attacker = self.get_user_by_id(game, self.user_id)
        target = self.get_user_by_id(game, self.target_id)

        if attacker == 0:
            logger.error("Attacker not found")
            return False

        if target == 0:
            logger.error("Target not found")
            return False

        attacker_row, attacker_col = attacker.pos
        target_row, target_col = target.pos

        distance = self.get_distance([attacker_row, attacker_col], [target_row, target_col])

        if distance > 2:
            logger.error("Attack distance bigger than 2")
            return False

        target.hp -= attacker.ap
        attacker.hp -= target.ap

        if target.hp <= 0:
            game.remove_user_by_id(self.target_id)
        if attacker.hp <= 0 and game.is_server:
            logger.debug("Attacker is DEAD @#############")
            # If I am being killed during the game
            response_queue.put(PlayerLeaveCommand(self.client_id, True))
            game.remove_user_by_id(self.client_id)

        return True


class HealCommand(Command):
    def __init__(self, client_id, target_id, timestamp=time.time()):
        Command.__init__(self, client_id, timestamp)
        self.target_id = target_id

    def apply(self, game):
        healer = self.get_user_by_id(game, self.client_id)
        target = self.get_user_by_id(game, self.target_id)

        if healer == 0:
            logger.error("Healer not found")
            return False
        if healer.type != USERS.PLAYER:
            logger.error("Dragons can't heal")
            return False

        if target == 0:
            logger.error("Target not found")
            return False
        if target.type != USERS.PLAYER:
            logger.error("Can't heal a dragon")
            return False

        if self.client_id == self.target_id:
            logger.error("Can't heal yourself")
            return False

        healer_row, healer_col = healer.pos
        target_row, target_col = target.pos

        distance = self.get_distance([healer_row, healer_col], [target_row, target_col])

        if distance > 5:
            logger.error("Heal distance bigger than 5")
            return

        heal_amount = healer.ap
        target.hp += heal_amount

        if target.hp > target.MAX_HP:
            target.hp = target.MAX_HP

        return True
