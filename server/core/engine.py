import multiprocessing
import time
import queue


class Engine(multiprocessing.Process):
    """
    Runs as a separate process to execute the game logic based on inputs (commands) of clients.
    Once launched it remains running.
    """

    def __init__(self, request_queue, response_queue):
        multiprocessing.Process.__init__(self)
        self.request_queue = request_queue
        self.response_queue = response_queue

    def run(self):
        """
        Overloaded function provided by multiprocessing.Process. Called upon start().
        """
        while True:
            self.process_commands()

            # periodically process commands
            time.sleep(5)

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
        commands = self.get_all_requests()
        for command in commands:
            # TODO: command needs to know the game as well
            print("applying command: ", command)
            command.apply(self.response_queue)
