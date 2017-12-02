import socket, threading
from common.constants import logger

class BaseServer(object):

    def __init__(self, request_queue, response_queue, port, host="127.0.0.1"):
        """
        A base class for both client and meta server
        """
        self.request_queue = request_queue
        self.response_queue = response_queue
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

        self.connections = dict()

    def listen(self):
        """
        Start listening for connections.
        Once accepted, on_connection will be called.
        """
        threading.Thread(target=self._listen).start()

    def _listen(self):
        self.sock.listen()
        logger.info("Server @ port {} listening...".format(self.port))
        while True:
            # wait for incoming connections
            connection, address = self.sock.accept()
            self.on_connection(connection, address)

    def on_connection(self, connection, address):
        pass


    def broadcast(self, data, without=None):
        """
        Broadcast the data to all connections except "without".
        :param data: the data to be broadcasted
        :param without: broadcast to everyone except this client
        """
        for client_id in self.connections:
            if client_id != without:
                self.connections[client_id].send(data)

    def remove_connection(self, id):
        """
        Removes the client from the list of currently connected clients.
        :param id: the client to be removed
        """
        if id in self.connections:
            del self.connections[id]