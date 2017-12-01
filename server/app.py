import json, time
import multiprocessing, argparse
from server.core.engine import Engine
from server.network.p2p_server import P2PComponent
from server.network.server import ClientServer
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
    parser.add_argument("--log-prefix", dest="prefix", default="DEFAULT")
    parser.add_argument("--peer")

    args = parser.parse_args()

    init_logger("log/server_{}.log".format(args.prefix))

    request_queue = multiprocessing.Queue()
    response_queue = multiprocessing.Queue()

    initial_users = []
    if args.users:
        initial_users = json.load(open(args.users))

    engine = Engine(request_queue, response_queue, initial_users)
    engine.start()

    client_server = ClientServer(request_queue, response_queue, int(args.port), '')
    client_server.listen()

    p2p_server = P2PComponent(request_queue, response_queue, int(args.port)+10, '127.0.0.1', ['127.0.0.1:7010'])


