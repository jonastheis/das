import multiprocessing
import time
import queue


class Engine(multiprocessing.Process):
    """
    Runs as a separate process to execute the game logic based on inputs (events) of clients.
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
            self.process_events()

            # periodically process events
            time.sleep(5)

    def get_all_requests(self):
        """
        Gets all events in a burst manner from the queue.
        :return: list of all the events sorted by timestamp
        """
        # TODO: check whether it's possible to sort events in queue or sort here by timestamp
        events = []
        while True:
            try:
                events.append(self.request_queue.get_nowait())
            except queue.Empty:
                break
        return events

    def process_events(self):
        """
        Processes all currently available events.
        """
        events = self.get_all_requests()
        for event in events:
            # TODO: event needs to know the game as well
            print("applying event: ", event)
            event.apply(self.response_queue)
