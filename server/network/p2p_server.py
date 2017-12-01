import json
from common.constants import logger
from .base_server import BaseServer
from .p2p_connection import P2PConnection
import socket, threading

class P2PComponent(BaseServer):
    def __init__(self, request_queue, response_queue, port, host="127.0.0.1", peers=[]):
        """
        :param request_queue:
        :param response_queue:
        :param port:
        :param host:
        :param peers: List of network addresses: ['localhost:8000', ]
        """
        BaseServer.__init__(self, request_queue, response_queue, port, host=host)

        # Initial connection to all other peers
        for peer in peers:
            # exclude self
            if peer == "{}:{}".format(host, port):
                continue
            logger.debug("Attempting to connect to peer {}".format(peer))
            self.connect_to_peer(peer.split(":")[0], peer.split(":")[1])

        self.listen()
        self.set_interval(self.heart_beat, 2)

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

    def on_connection(self, connection, address):
        logger.info("Connection from Another server {0}:{1}".format(address[0], address[1]))
        _id = self.create_id(address[0], address[1])
        new_peer = P2PConnection(connection, address, _id, self)
        self.connections[_id] = new_peer

        self.broadcast(json.dumps({"type": "debug", "msg":"A New node has just joined us!"}))
    def create_id(self, host, port):
        return "peer@{}:{}".format(host, port)


    def heart_beat(self):
        logger.debug("Sending heartbeat to {} peers".format(len(self.connections)))
        for connection in self.connections:
            try:
                self.connections[connection].send(json.dumps({"type": "hb"}))
            except BaseException as e:
                logger.warn("Peer {} -> failed to send heartbeat".format(connection))

        self.update_heartbeat_stat()

    def update_heartbeat_stat(self):
        for peer_id in list(self.connections):
            if peer_id in self.connections:
                if self.connections[peer_id].heartbeat < 0 :
                    self.remove_connection(peer_id)
                else:
                    self.connections[peer_id].heartbeat -= 1000


    def connect_to_peer(self, host, port):
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
        BaseServer.remove_connection(self, id)



