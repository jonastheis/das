import json
from common.constants import logger
from .base_server import BaseServer
from .p2p_connection import P2PConnection
import socket, threading

class P2PComponent(BaseServer):
    def __init__(self, request_queue, response_queue, client_server, port, host="127.0.0.1", peers=[]):
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

        # Initial connection to all other peers
        for peer in peers:
            # exclude self
            if peer == "{}:{}".format(host, port):
                continue
            logger.debug("Attempting to connect to peer {}".format(peer))
            self.connect_to_peer(peer.split(":")[0], peer.split(":")[1])

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
            if len(self.client_server._request_queue):
                command = self.client_server._request_queue.pop()
                logger.debug("Broadcasting {}".format(command))
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

        self.broadcast(json.dumps({"type": "debug", "msg":"A New node has just joined us!"}))

    def create_id(self, host, port):
        return "peer@{}:{}".format(host, port)


    def heart_beat(self):
        """
        Send a small message to all connections
        """
        logger.debug("Sending heartbeat to {} peers".format(len(self.connections)))
        for connection in self.connections:
            try:
                self.connections[connection].send(json.dumps({"type": "hb"}))
            except BaseException as e:
                logger.warn("Peer {} -> failed to send heartbeat".format(connection))

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
        new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            new_sock.connect((host, int(port)))
        except BaseException as e :
            logger.warn("Connection to peer@{}:{} failed [{}]".format(host, port, str(e)))
            return

        id = self.create_id(host, port)
        self.connections[id] = P2PConnection(new_sock, [host, port], id, self)
        logger.info("Connection established to peer {}".format(id))

    def remove_connection(self, id):
        self.connections[id].shutdown()
        logger.error("Peer {} removed".format(id))
        BaseServer.remove_connection(self, id)
