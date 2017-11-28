import json
import multiprocessing, argparse
from server.core.engine import Engine
from server.network.server import ThreadedServer
from common.command import init_logger, logger
from common.constants import TRANSPORT

if __name__ == '__main__':
    """
    Starts the server and the engine in separate processes. 
    They are communication via a request and response queue.
    
    Initial user/dragons can be passed in the engine as a json array. Each object should have type, r, and c.
    """
    parser = argparse.ArgumentParser(description='DAS Server app')
    parser.add_argument("--users", nargs="?", dest="users", required=False)
    parser.add_argument("--port", nargs="?", dest="port" , default=TRANSPORT.port)
    parser.add_argument("--vis", action="store_true")

    args = parser.parse_args()

    init_logger("log/server.log")

    logger.debug(args)
    request_queue = multiprocessing.Queue()
    response_queue = multiprocessing.Queue()

    initial_users = []
    if args.users:
        initial_users = json.load(open(args.users))

    engine = Engine(request_queue, response_queue, initial_users, args.vis)
    engine.start()

    server = ThreadedServer(request_queue, response_queue, int(args.port), '')
    server.listen()
