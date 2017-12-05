import math, argparse
from common.game import Game
from client.network.transport import ClientTransport
from common.constants import TRANSPORT, USERS, DIRECTIONS, init_logger, MSG_TYPE
from common.command import MoveCommand, HealCommand, AttackCommand
from common.visualizer import Visualizer
import threading, random, time
import json

import logging
logger = logging.getLogger("sys." + __name__.split(".")[-1])
gameLogger = logging.getLogger("game." + __name__.split(".")[-1])


class ClientApp():
    def __init__(self, servers):
        self.game = Game()
        self.transport_layer = ClientTransport(self.game, servers)

        id, map = self.transport_layer.setup_client()
        self.id = id
        # replace json objects with user object
        self.game.from_serialized_map(map)
        logger.info("Setup data -> id: {0}".format(id))

        self.transport_layer.id = id
        self.transport_layer.listen()

        self.my_user = next(filter(lambda el: el.id == self.id, self.game.users))

    def generate_commands(self, iterations, malicious):
        """
        Run _generate_commands in a new thread
        """
        threading.Thread(target=self._generate_commands, args=(iterations, malicious)).start()

    def _generate_commands(self, iterations, malicious):
        """
        Generate simulation commands
        :param iterations: Number of iterations
        :return: None
        """
        logger.debug("Generating commands for {} iterations".format(iterations))
        for i in range(iterations):
            if not malicious:
                new_command = self.simulate_player()
            else:
                new_command = self.simulate_malicious_player()
            # If there is no dragon and no one with hp<50%, no commands will be generated. In that case do nothing
            if new_command:
                self.game.commands.append(new_command)

    def simulate_player(self):
        """
        Simulate the actions of the self player based on game spec
        :return: Command Object
        """

        ######## Option 1: heal a close-by player
        heal_candidates = self.get_users_in_range(self.my_user.pos, 5, USERS.PLAYER)
        for user in heal_candidates:
            if user.id != self.my_user.id:
                if user.hp < user.MAX_HP/2:
                    return HealCommand(self.id, user.id)

        ######## Option 2: Attack a close dragon if available
        attack_candidates = self.get_users_in_range(self.my_user.pos, 2, USERS.DRAGON)
        if len(attack_candidates):
            target = attack_candidates[0]
            return AttackCommand(self.id, target.id)

        ######## Option 3: Move toward the closest dragon
        dragons = list(filter(lambda _user: _user.type == USERS.DRAGON, self.game.users))
        if len(dragons):
            # sort dragons by distance
            # NOTE: we assume that the distance of the closest dragon is more than 2.
            # Because otherwise we would have returned with an attack command
            dragons.sort(key=lambda dragon: math.fabs(dragon.pos[0]-self.my_user.pos[0]) + math.fabs(dragon.pos[1]-self.my_user.pos[1]))

            # Move options: Move vertically toward that dragon or Horizontally
            # If they are in the same row/col we know what to do
            move_target = dragons[0]
            value = None
            move_direction = None

            if self.my_user.pos[0] == move_target.pos[0]:
                move_direction = DIRECTIONS.H
            elif self.my_user.pos[1] == move_target.pos[1]:
                move_direction = DIRECTIONS.V
            else:
                # If not, we choose randomly
                move_direction = random.choice([DIRECTIONS.H, DIRECTIONS.V])


            if move_direction == DIRECTIONS.H:
                value = 1 if move_target.pos[1] > self.my_user.pos[1] else -1
            else:
                value = 1 if move_target.pos[0] > self.my_user.pos[0] else -1

            if value and move_direction:
                return MoveCommand(self.id, value, move_direction)

        logger.warning("Failed to find a simulation for player. Random walk it is...")
        return MoveCommand(self.id, random.choice([1, -1]), random.choice([DIRECTIONS.H, DIRECTIONS.V]))

    def simulate_malicious_player(self):
        """
        Simulate the actions of a malicious player
        :return: Command Object
        """

        ######## Option 1: attack a close-by player
        attack_candidates = self.get_users_in_range(self.my_user.pos, 1, USERS.PLAYER)
        for user in attack_candidates:
            if user.id != self.my_user.id:
                return AttackCommand(self.id, user.id)

        ######## Option 2: Heal a close by dragon
        attack_candidates = self.get_users_in_range(self.my_user.pos, 2, USERS.DRAGON)
        if len(attack_candidates):
            target = attack_candidates[0]
            return HealCommand(self.id, target.id)

        ######## Option 3: Move toward the closest dragon
        dragons = list(filter(lambda _user: _user.type == USERS.DRAGON, self.game.users))
        if len(dragons):
            # sort dragons by distance
            # NOTE: we assume that the distance of the closest dragon is more than 2.
            # Because otherwise we would have returned with an attack command
            dragons.sort(key=lambda dragon: math.fabs(dragon.pos[0]-self.my_user.pos[0]) + math.fabs(dragon.pos[1]-self.my_user.pos[1]))

            # Move options: Move vertically toward that dragon or Horizontally
            # If they are in the same row/col we know what to do
            move_target = dragons[0]
            value = None
            move_direction = None

            if self.my_user.pos[0] == move_target.pos[0]:
                move_direction = DIRECTIONS.H
            elif self.my_user.pos[1] == move_target.pos[1]:
                move_direction = DIRECTIONS.V
            else:
                # If not, we choose randomly
                move_direction = random.choice([DIRECTIONS.H, DIRECTIONS.V])


            if move_direction == DIRECTIONS.H:
                value = 10 if move_target.pos[1] > self.my_user.pos[1] else -10
            else:
                value = 10 if move_target.pos[0] > self.my_user.pos[0] else -10

            if value and move_direction:
                return MoveCommand(self.id, value, move_direction)

        logger.warning("Failed to find a simulation for player. Random walk it is...")
        return MoveCommand(self.id, random.choice([10, -10]), random.choice([DIRECTIONS.H, DIRECTIONS.V]))

    def get_users_in_range(self, point, limit, type=-1):
        """
        Utility function for simulation. Return a list of all users (player and dragons) in a range
        if type is specified, only users from that type will be returned
        :param limit: distance limit
        :param point: the root point of the distance
        ":type: type of players to return
        :return: User[]
        """
        users = []
        for user in self.game.users:
            if (math.fabs(point[0] - user.pos[0])) + (math.fabs(point[1] - user.pos[1])) <= limit:
                if type == -1:
                    users.append(user)
                else:
                    if user.type == type:
                        users.append(user)

        return users

    def run(self, commands_per_second, malicious):
        """
        :param commands_per_second: number of commands per second
        run _run in a new thread
        """
        threading.Thread(target=self._run, args=(commands_per_second, malicious)).start()

    def _run(self, command_per_second, malicious):
        while self.game.up:
            time.sleep(1/command_per_second)
            # Generate one or max two new commands that will be appended to the end of the list
            self._generate_commands(1, malicious)
            if len(self.game.commands):
                command_to_apply = self.game.commands.pop(0)
                self.transport_layer.send_data(command_to_apply.to_json(), MSG_TYPE.COMMAND)

if __name__ == "__main__":
    """
    Arguments to the command line: 
    --vis to enable/disable the visualizer
    --log-prefix to choose the file name of the log
    --config to pass list of possibly available game servers
    
    CRITICAL	50
    ERROR	40
    WARNING	30
    INFO	20
    DEBUG	10
    NOTSET	0
    """
    parser = argparse.ArgumentParser(description="DAS Client app")

    parser.add_argument("--vis", action="store_true")
    parser.add_argument("--log-prefix", dest="prefix", default=time.time())
    parser.add_argument("--config", nargs="?", dest="config", required=False, default='./test/das_config.json')
    parser.add_argument("--game-log", dest="gameLog", action="store_false", default=True)
    parser.add_argument("--malicious", action="store_true", default=False)
    parser.add_argument("--log-level", dest="logLevel", default="20")

    args = parser.parse_args()
    args.logLevel = int(args.logLevel)

    # get available server
    config = json.load((open(args.config)))
    servers = []
    for server in config['servers']:
        servers.append((server.split(':')[0], int(server.split(':')[1])))


    init_logger("log/client_{}.log".format(args.prefix), args.gameLog, args.logLevel)
    client = ClientApp(servers)

    client.run(.5, args.malicious)

    # start visualization
    if args.vis:
        visualizer = Visualizer(client.game, client.id)
        visualizer.visualize()