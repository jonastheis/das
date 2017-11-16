import socket
from .client import Client


class ThreadedServer(object):
    def __init__(self, request_queue, response_queue, port, host="127.0.0.1"):
        self.request_queue = request_queue
        self.response_queue = response_queue
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

        self.clients = dict()

    def listen(self):
        self.sock.listen()
        print("Server listening on port", self.port)
        while True:
            connection, address = self.sock.accept()
            id = "{0}:{1}".format(address[0], address[1])
            print("Connection from ", id)
            self.clients[id] = Client(connection, address, id, self)

    def broadcast(self, data):
        for (addr, sock) in self.clients.items():
            sock.sendall(data)

    def remove_client(self, id):
        if id in self.clients:
            del self.clients[id]

    def request_command(self, data):
        self.request_queue.put(data)
