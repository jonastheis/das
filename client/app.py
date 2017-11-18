from common.game import Game
from client.network.transport import ClientTransport
from common.constants import TRANSPORT, USERS, DIRECTIONS
from common.command import MoveCommand
import threading, random, time


class ClientApp():
    def __init__(self):
        self.game = Game()
        self.transport_layer = ClientTransport(self, TRANSPORT.port, TRANSPORT.host)

        id, map = self.transport_layer.setup_client()
        self.id = id
        # replace json objects with user object (oh I miss you JS :( )
        self.game.from_serialized_map(map, id)
        print("Client setup data")
        print(id)
        print(self.game)
        print("________________________________________")


        self.transport_layer.listen()
        self.my_user = None

    def generate_commands(self, iterations):
        """
        Run _simulate in a new thread
        """
        threading.Thread(target=self._generate_commands, args=(iterations,)).start()


    def _generate_commands(self, iterations):
        """
        Generate simulation commands
        :param iterations: Number of iterations
        :return: None
        """
        print("Generating commands for {} iterations".format(iterations))
        for i in range(iterations):
            new_command = self.simulate_player(self.id)
            self.game.commands.append(new_command)

    def simulate_player(self, id):
        """
        Simulate the actions of one player specified by id param
        :return:
        """
        value = random.choice([1, -1])
        direction = random.choice([DIRECTIONS.V, DIRECTIONS.H])
        return MoveCommand(id, value, direction)

    def simulate_dragon(self, d):
        pass

    def run(self, commands_per_second):
        """
        :param commands_per_second: number of commands per second
        run _run in a new thread
        """
        threading.Thread(target=self._run, args=(commands_per_second,)).start()

    def _run(self, command_per_second):
        print("Current number of commands for emulation {}".format(len(self.game.commands)))
        while True:
            time.sleep(1/command_per_second)
            if len(self.game.commands):
                print("##################")
                command_to_apply = self.game.commands[0]
                print(command_to_apply)

                self.game.epoch()
                self.transport_layer.send_data(command_to_apply.to_json())

                print(self.game)
                print("##################")

            else:
                continue

if __name__ == "__main__":
    client = ClientApp()
    client.generate_commands(1000)
    client.run(1)

