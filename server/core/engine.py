import multiprocessing
import time
import queue
from common import game
from common.user import User
from common.constants import USERS, logger


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

        # Just for test
        self.game.add_user(User(USERS.DRAGON), 0, 0)

        self.T = .5


    def run(self):
        """
        Overloaded function provided by multiprocessing.Process. Called upon start().
        """
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
        # TODO: now that I think about it, passing response_queue to command is not ok. We can just append it here
        commands = self.get_all_requests()
        if len(commands):
            logger.info("Interval reached. Processing {} commands".format(len(commands)))
            self.game.commands += commands
            self.game.mega_epoch(False, self.response_queue)
        else:
            logger.info("Interval reached. No command to process")

