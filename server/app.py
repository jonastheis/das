import json
import multiprocessing, argparse
from server.core.engine import Engine
from server.network.p2p_server import P2PComponent
from server.network.client_server import ClientServer
from common.command import init_logger
from common.constants import TRANSPORT

import logging
logger = logging.getLogger("sys." + __name__.split(".")[-1])

if __name__ == '__main__':
    """
    Starts the server and the engine in separate processes. 
    They are communication via a request and response queue.
    
    Initial user/dragons can be passed in the engine as a json array. Each object should have type, r, and c.
    """
    parser = argparse.ArgumentParser(description='DAS Server app')
    parser.add_argument("--users", nargs="?", dest="users", required=False)
    parser.add_argument("--config", nargs="?", dest="config", required=False)
    parser.add_argument("--port", nargs="?", dest="port" , default=TRANSPORT.port)
    parser.add_argument("--vis", action="store_true")
    parser.add_argument("--log-prefix", dest="prefix", default="DEFAULT")
    parser.add_argument("--peer")

    args = parser.parse_args()

    init_logger("log/server_{}.log".format(args.prefix))

    request_queue = multiprocessing.Queue()
    response_queue = multiprocessing.Queue()
    meta_request_queue = multiprocessing.Queue()
    meta_response_queue = multiprocessing.Queue()

    initial_users = []
    if args.users:
        initial_users = json.load(open(args.users))

    peers = []
    if args.config:
        config = json.load((open(args.config)))
        peers = config['peers']

    client_server = ClientServer(request_queue, response_queue, meta_request_queue, meta_response_queue, int(args.port), '')
    client_server.listen()

    p2p_server = P2PComponent(
        request_queue, response_queue, meta_request_queue, meta_response_queue,
        client_server,
        int(args.port) + 10, '',
        peers)

    if not initial_users:
        # ask (blocking) other servers for the initial game state
        initial_state = p2p_server.gather_initial_state()
        engine = Engine(request_queue, response_queue, meta_request_queue, meta_response_queue, initial_users, args.vis)
        engine.game.from_serialized_map(initial_state)
        engine.start()
    else:
        engine = Engine(request_queue, response_queue, meta_request_queue, meta_response_queue, initial_users, args.vis)
        engine.start()
