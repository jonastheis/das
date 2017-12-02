import json
from .base_server import BaseServer
from .p2p_connection import P2PConnection
import socket, threading
import queue
import logging
logger = logging.getLogger("sys." + __name__.split(".")[-1])


class P2PComponent(BaseServer):
    def __init__(self, request_queue, response_queue, meta_request_queue, meta_response_queue, client_server, port, host="127.0.0.1", peers=[]):
        """
        :param request_queue:
        :param response_queue:
        :param client_server: an instance of the client server obj
        :type client_server: ClientServer
        :param port: Port to listen to (default is client_server.port + 10)
        :param host: hostname
        :param peers: List of network addresses: ['localhost:8000', ]

        The main difference of this type of server (aka. component)
        is that Both "accepted" connections and "established" connections are stored using the base_connection class
        as an element in self.connections.
        """
        BaseServer.__init__(self, request_queue, response_queue, port, host=host)
        self.client_server = client_server
        self.meta_request_queue = meta_request_queue
        self.meta_response_queue = meta_response_queue
        self.init_queue = queue.Queue()

        # Initial connection to all other peers
        for peer in peers:
            # exclude self
            if peer == "{}:{}".format(host, port):
                continue
            self.connect_to_peer(peer.split(":")[0], peer.split(":")[1])

        logger.info("Current Peers {}".format(self.connections))

        self.listen()
        self.set_interval(self.heart_beat, 2)

        request_thread = threading.Thread(target=self.broadcast_requests)
        request_thread.start()

    def set_interval(self, func, sec):
        """
        Utility function to create intervals
        """
        def func_wrapper():
            self.set_interval(func, sec)
            func()

        t = threading.Timer(sec, func_wrapper)
        t.start()
        return t

    def broadcast_requests(self):
        """
        Threaded func.
        Always check the duplicate queue of the client_server and remove/send any commands from it
        :return:
        """
        while True:
            command = self.client_server.broadcast_queue.get()
            logger.debug("Broadcasting {}".format(command))
            # TODO: check whether to_json_broadcast always works
            self.broadcast(json.dumps({"type": "bc", "command": command.to_json_broadcast()}))

    def on_connection(self, connection, address):
        """
        called by baseServer whenever a new connection is established
        :param connection: socket object
        :param address: address of the connection
        :return:
        """
        logger.info("Connection from Another server {0}:{1}".format(address[0], address[1]))
        _id = self.create_id(address[0], address[1])
        new_peer = P2PConnection(connection, address, _id, self)
        self.connections[_id] = new_peer

    def create_id(self, host, port):
        return "peer@{}:{}".format(host, port)

    def heart_beat(self):
        """
        Send a small message to all connections
        """
        #logger.debug("Sending heartbeat to {} peers".format(len(self.connections)))
        for connection in self.connections:
            try:
                self.connections[connection].send(json.dumps({"type": "hb"}))
            except BaseException as e:
                logger.warning("Peer {} -> failed to send heartbeat".format(connection))

        self.update_heartbeat_stat()

    def update_heartbeat_stat(self):
        """
        Kick nodes that have not answered in a while
        """
        for peer_id in list(self.connections):
            if peer_id in self.connections:
                if self.connections[peer_id].heartbeat < 0 :
                    self.remove_connection(peer_id)
                else:
                    self.connections[peer_id].heartbeat -= 1000


    def connect_to_peer(self, host, port):
        """
        If success, the new connection will be added to self.connections
        :param host: ip of the peer
        :param port: port of the peer
        """
        logger.debug("Attempting to connect to peer {}".format(self.create_id(host, port)))
        new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            new_sock.connect((host, int(port)))
        except BaseException as e :
            logger.warning("Connection to peer@{}:{} failed [{}]".format(host, port, str(e)))
            return

        id = self.create_id(host, port)
        self.connections[id] = P2PConnection(new_sock, [host, port], id, self)
        logger.info("Connection established to peer {}".format(id))

    def remove_connection(self, id):
        self.connections[id].shutdown()
        logger.error("Peer {} removed".format(id))
        BaseServer.remove_connection(self, id)

    def gather_initial_state(self):
        """
        Gathers (blocking) the initial game state from all other servers.
        :return: initial game state
        """
        for connection in self.connections:
            try:
                self.connections[connection].send(json.dumps({"type": "init_req"}))
            except BaseException as e:
                logger.warning("Peer {} -> failed to request initial game state".format(connection))

        # wait for init_res of other servers -> will be put on the init_queue
        # right now we take the first response and assume that all servers are in sync with that state
        return self.init_queue.get()

    def get_current_commands(self):
        """
        Gets the current pending commands and puts them back on the queue.
        :return: list of jsonified commands
        """
        commands = []
        while True:
            try:
                commands.append(self.request_queue.get_nowait())
            except queue.Empty:
                break
        commands_json = []
        for command in commands:
            self.request_queue.put_nowait(command)
            commands_json.append(command.to_json_broadcast())

        return commands_json
