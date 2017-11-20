import multiprocessing
from server.core.engine import Engine
from server.network.server import ThreadedServer
from common.command import init_logger


if __name__ == '__main__':
    """
    Starts the server and the engine in separate processes. 
    They are communication via a request and response queue.
    """
    init_logger("log/server.log")

    request_queue = multiprocessing.Queue()
    response_queue = multiprocessing.Queue()

    engine = Engine(request_queue, response_queue)
    engine.start()

    port_num = 8081
    server = ThreadedServer(request_queue, response_queue, port_num, '')
    server.listen()
