import multiprocessing
from server.core.engine import Engine
from server.network.server import ThreadedServer


if __name__ == '__main__':
    request_queue = multiprocessing.Queue()
    response_queue = multiprocessing.Queue()
    metadata_queue = multiprocessing.Queue()

    engine = Engine(request_queue, response_queue, metadata_queue)
    engine.start()

    port_num = 8081
    server = ThreadedServer(request_queue, response_queue, metadata_queue, port_num, '')
    server.listen()
