import multiprocessing
import time
import queue
import threading
from common import game
from common.user import User
from common.constants import USERS, logger
from common.visualizer import Visualizer


class Engine(multiprocessing.Process):
    """
    Runs as a separate process to execute the game logic based on inputs (commands) of clients.
    Once launched it remains running.
    """

    def __init__(self, request_queue, response_queue):
        multiprocessing.Process.__init__(self)
        self.request_queue = request_queue
        self.response_queue = response_queue
        self.game = game.Game()
        self.game.is_server = True

        # Just for test
        self.game.add_user(User(USERS.DRAGON), 0, 0)
        self.game.add_user(User(USERS.DRAGON), 4, 4)

        self.T = .5


    def run(self):
        """
        Overloaded function provided by multiprocessing.Process. Called upon start().
        """

        threading.Thread(target=self._run).start()

        # start visualization
        visualizer = Visualizer(self.game)
        visualizer.visualize()

    def _run(self):
        while True:
            self.process_commands()

            # periodically process commands
            time.sleep(self.T)

    def get_all_requests(self):
        """
        Gets all events in a burst manner from the queue.
        :return: list of all the events sorted by timestamp
        """
        commands = []
        while True:
            try:
                commands.append(self.request_queue.get_nowait())
            except queue.Empty:
                break
        # sort list by timestamp
        commands.sort(key=lambda command: command.timestamp)
        return commands

    def process_commands(self):
        """
        Processes all currently available command/events.
        """
        commands = self.get_all_requests()

        if len(commands):
            logger.info("Interval reached. Processing {} commands".format(len(commands)))

            while len(commands):
                command = commands.pop(0)
                status = command.apply(self.game)

                # only send to clients if successful
                if status:
                    self.response_queue.put(command)
        else:
            logger.info("Interval reached. No command to process")

