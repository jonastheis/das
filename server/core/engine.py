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

    def __init__(self, request_queue, response_queue, metadata_queue):
        multiprocessing.Process.__init__(self)
        self.request_queue = request_queue
        self.response_queue = response_queue
        self.metadata_queue = metadata_queue
        self.game = game.Game()

        # Just for test
        self.game.add_user(User(USERS.DRAGON), 0, 0)

        self.T = 5


    def run(self):
        """
        Overloaded function provided by multiprocessing.Process. Called upon start().
        """
        while True:
            self.process_commands()

            # periodically process commands
            time.sleep(self.T)

    def get_all_requests(self):
        # TODO: check whether it's possible to sort commands in queue or sort here by timestamp
        commands = []
        while True:
            try:
                commands.append(self.request_queue.get_nowait())
            except queue.Empty:
                break
        return commands

    def process_commands(self):
        # TODO: now that I think about it, passing response_queue to command is not ok. We can just append it here
        commands = self.get_all_requests()
        if len(commands):
            logger.info("Interval reached. Processing {} commands".format(len(commands)))
            self.game.commands+= commands
            self.game.mega_epoch(False, self.response_queue)
            logger.debug("New game state:")
            print(self.game)
        else:
            logger.info("Interval reached. No command to process")

        # for command in commands:
        #     # TODO: command needs to know the game as well
        #     print("applying command: ", command)
        #     command.apply(self.response_queue)
