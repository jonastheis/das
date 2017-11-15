import threading, random, time
from .transport import ClientTransport
from .command import MoveCommand
from common.constants import *


class Game:
    def __init__(self, port=TRANSPORT.port, host=TRANSPORT.host):
        self.row = 5
        self.col = 5

        self.map = [[0 for j in range(self.col)] for i in range(self.row)]

        self.commands = []
        self.users = []

        self.transport_layer = ClientTransport(self, port, host)

    def __str__(self):
        _str = ""
        for i in range(self.row):
            for j in range(self.col):
                _str += str(self.map[i][j])
                _str += "\t"
            _str += "\n"
        return _str

    def add_user(self, p, r, c):
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

    def epoch(self):
        if len(self.commands):
            command = self.commands[0]
            command.apply(self)

            # Send the command to the server to be broadcasted to everyone
            self.transport_layer.send_data(command.to_json())
            self.commands = self.commands[1:]
        else:
            return

    def emulate_all(self):
        """
        only for test.
        Run all commands in self.commands
        """
        i = 1
        while len(self.commands):
            print("###Epoch {0}".format(i))
            print(self.commands[0])
            i += 1
            self.epoch()
            print(self.__str__())

    def emulate(self, commands_per_second):
        """
        :param commands_per_second: number of commands per second
        run _emulate in a new thread
        """
        threading.Thread(target=self._emulate, args=(commands_per_second,)).start()

    def _emulate(self, command_per_second):
        print("Current number of commands for emulation {}".format(len(self.commands)))
        while True:
            time.sleep(1/command_per_second)
            if len(self.commands):
                print("##################")
                print(self.commands[0])
                self.epoch()
                print(self.__str__())
                print("##################")
            else:
                continue

    def simulate(self, iterations):
        """
        Run _simulate in a new thread
        """
        threading.Thread(target=self._simulate, args=(iterations,)).start()

    def _simulate(self, iterations):
        for i in range(iterations):
            for user in self.users:
                if user.type == USERS.PLAYER:
                    new_command = self.simulate_player(user)
                    self.commands.append(new_command)

    def simulate_player(self, p):
        value = random.choice([1, -1])
        direction = random.choice([DIRECTIONS.V, DIRECTIONS.H])
        return MoveCommand(p.id, value, direction)

    def simulate_dragon(self, d):
        pass
