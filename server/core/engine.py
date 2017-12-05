import multiprocessing
import time
import queue
import threading
from common import game
from common.command import AttackCommand
from common.user import User
from common.visualizer import Visualizer

import logging
logger = logging.getLogger("sys." + __name__.split(".")[-1])


class Engine(multiprocessing.Process):
    """
    Runs as a separate process to execute the game logic based on inputs (commands) of clients.
    Once launched it remains running.
    """

    def __init__(self, request_queue, response_queue, meta_request_queue, meta_response_queue, initial_users, vis=False):
        multiprocessing.Process.__init__(self)
        self.request_queue = request_queue
        self.response_queue = response_queue
        self.meta_request_queue = meta_request_queue
        self.meta_response_queue = meta_response_queue
        self.game = game.Game()
        self.game.is_server = True
        self.vis = vis

        for user in initial_users:
            self.game.add_user(User(user['type']), user['r'], user['c'])

        self.T = 500

        logger.info("Engine successfully started.")

    def run(self):
        """
        Overloaded function provided by multiprocessing.Process. Called upon start().
        """

        # start meta_request thread
        self.process_meta_requests()

        # visualizer needs to run in main thread
        if self.vis:
            threading.Thread(target=self._run).start()

            # start visualization
            visualizer = Visualizer(self.game)
            visualizer.visualize()
        else:
            self._run()

    def _run(self):
        while True:
            self.process_commands()

            # periodically process commands
            time_ms = int(round(time.time() * 1000))
            time_sync = int(time_ms/self.T) * self.T + self.T

            time.sleep((time_sync - time_ms) / 1000)


    def get_all_requests(self):
        """
        Gets all events in a burst manner from the queue.
        :return: list of all the events sorted by timestamp
        """
        current_tick = time.time()
        all_commands = []
        exec_commands = []

        while True:
            try:
                all_commands.append(self.request_queue.get_nowait())
            except queue.Empty:
                break
        # sort list by timestamp
        all_commands.sort(key=lambda command: (command.timestamp, command.client_id))

        threshold = self.T / 2000

        for command in all_commands:
            print(current_tick, command.timestamp, current_tick-command.timestamp , threshold)
            if current_tick - command.timestamp < threshold :
                logger.error("Putting back {}".format(command))
                self.request_queue.put(command)
            else:
                exec_commands.append(command)


        return exec_commands

    def process_commands(self):
        """
        Processes all currently available command/events.
        """
        commands = self.get_all_requests()

        if len(commands):
            logger.debug("Interval reached. Processing {} commands".format(len(commands)))

            while len(commands):
                command = commands.pop(0)

                if type(command) is AttackCommand:
                    status = command.apply(self.game, self.response_queue)
                else:
                    status = command.apply(self.game)

                # only send to clients if successful
                if status:
                    self.response_queue.put(command)
        else:
            logger.debug("Interval reached. No command to process")

    def process_meta_requests(self):
        """
        Starts the meta_request thread.
        """
        threading.Thread(target=self._process_meta_requests).start()

    def _process_meta_requests(self):
        """
        Waits (blocking) for requests from the server process and handles them.
        """
        while True:
            req = self.meta_request_queue.get()

            if req['type'] == "get_map":
                self.meta_response_queue.put(self.game.serialize())
