import multiprocessing
import time
import queue
from server.network.server import ThreadedServer


def run_game(request_queue, response_queue):
    while True:
        commands = queue_get_all(request_queue)

        # TODO: process commands in a new thread
        print(commands)
        # send result back to client(s) if needed

        # periodically process commands
        time.sleep(5)


def queue_get_all(q):
    items = []
    while True:
        try:
            items.append(q.get_nowait())
        except queue.Empty:
            break
    return items



if __name__ == '__main__':
    request_queue = multiprocessing.Queue()
    response_queue = multiprocessing.Queue()
    multiprocessing.Process(target=run_game, args=(request_queue,response_queue)).start()

    port_num = 8081
    server = ThreadedServer(request_queue, response_queue, port_num, '')

    server.listen()