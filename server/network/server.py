import socket
import hashlib
import time
from .client import Client
from server.core.command import NewPlayerCommand


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
            # wait for incoming connections
            connection, address = self.sock.accept()

            # create socket connection to client and remember relationship between id -> socket
            id = hashlib.md5("{0}:{1}".format(address[0], address[1]).encode('utf-8')).hexdigest()
            print("Connection from ", "{0}:{1}".format(address[0], address[1]))
            self.clients[id] = Client(connection, address, id, self)

            # send new player command to game engine
            self.request_command(NewPlayerCommand(time.time(), id))

    def broadcast(self, data):
        for (addr, sock) in self.clients.items():
            sock.sendall(data)

    def remove_client(self, id):
        if id in self.clients:
            del self.clients[id]

    def request_command(self, command):
        self.request_queue.put(command)
