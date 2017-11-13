from __future__ import print_function
import math, json, socket, threading, select, sys, random, time
# from common.network_util import read_encoded

class Game:
    def __init__(self):
        self.row = 5
        self.col = 5

        self.map = [[0 for j in range(self.col)] for i in range(self.row)]

        self.active_users = 0
        self.commands = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('localhost', 8081))
        threading.Thread(target=self.sock_check_for_update).start()

    def __str__(self):
        _str = ""
        for i in range(self.row):
            for j in range(self.col):
                _str += str(self.map[i][j])
                _str += "\t"
            _str += "\n"
        return _str

    def sock_check_for_update(self):
        print("Thread for listening is started\n")
        while True:
            socket_list = [self.sock]
            read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
            for sock in read_sockets:
                # incoming message from remote server
                data = sock.recv(1024)
                # data = read_encoded(sock)
                if not data:
                    print('\nDisconnected from server')
                    sys.exit()
                else:
                    print("received" , data)

    def add_user(self, p, r, c):
        if self.map[r][c] == 0:
            self.map[r][c] = p
            self.active_users += 1
            return True
        else:
            return False

    def remove_user(self, r, c):
        if self.map[r][c] == 0:
            return False
        else:
            self.map[r][c] = 0
            self.active_users -= 1
            return True

    def epoch(self):
        if len(self.commands):
            command = self.commands[0]
            self.apply_command(command)

            # Send the command to the server to be broadcasted to everyone
            self.sock.send(json.dumps(command))
            self.commands = self.commands[1:]
        else:
            return

    def apply_command(self, command):
        if command['type'] == 'move':
            _user, _row, _col = self.get_user_by_id(command['user'])

            if _user == 0 :
                print("No Player Found")
                return

            # Dragons cannot move
            if _user.type == 'd':
                print("Dragons cannot move")
                return

            target_row = _row
            target_col = _col


            if command['direction'] == 'v':
                target_row += command['value']
            elif command['direction'] == 'h':
                target_col += command['value']

            if self.map[target_row][target_col] != 0:
                print("Position [{}, {}] already full".format(target_row, target_col))
                return

            self.map[_row][_col] = 0
            self.map[target_row][target_col] = _user

        elif command['type'] == 'attack':
            attacker, attacker_row, attacker_col = self.get_user_by_id(command['user'])
            target, target_row, target_col = self.get_user_by_id(command['target'])

            if attacker == 0:
                print("Attacker not found")
                return

            if target == 0:
                print("Target not found")
                return

            distance = self.get_distance([attacker_row, attacker_col], [target_row, target_col])

            if distance > 2:
                print("Attack distance bigger than 2")
                return

            target.hp -= attacker.ap

            if target.hp <= 0:
                self.remove_user(target_row, target_col)

        elif command['type'] == 'heal':
            healer, healer_row, healer_col = self.get_user_by_id(command['user'])
            target, target_row, target_col = self.get_user_by_id(command['target'])

            if healer == 0:
                print("Attacker not found")
                return

            if target == 0:
                print("Target not found")
                return

            distance = self.get_distance([healer_row, healer_col], [target_row, target_col])

            if distance > 5:
                print("Heal distance bigger than 5")
                return

            heal_amount = healer.ap
            target.hp += heal_amount
            if target.hp > target.MAX_HP :
                target.hp = target.MAX_HP

    def get_user_by_id(self, id):
        for i in range(self.row):
            for j in range(self.col):
                if self.map[i][j] != 0 and self.map[i][j].id == id :
                    return self.map[i][j], i, j
        return 0 ,-1 ,-1

    def get_distance(self, pos, sop):
        return math.fabs(pos[0] - sop[0]) + math.fabs(pos[1] - sop[1])

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
        while True:
            time.sleep(1/command_per_second)
            if len(self.commands):
                self.epoch()
            else:
                continue

    def simulate(self, iterations):
        """
        Run _simulate in a new thread
        """
        threading.Thread(target=self._simulate, args=(iterations,)).start()

    def _simulate(self, iterations):
        for iter in range(iterations):
            for i in range(self.row):
                for j in range(self.col):
                    if self.map[i][j] != 0 :
                        new_command = self.simulate_player(i,j)
                        self.commands.append(new_command)

    def simulate_player(self, r, c):
        value = random.choice([1, -1])
        direction = random.choice(['h', 'v'])
        return {'type': 'move', 'direction': direction, 'value': value, 'user': (self.map[r][c]).id}

    def simulate_dragon(self, e, c):
        pass
