import socket
import hashlib
import time
import threading
from .client import Client
from server.core.command import NewPlayerCommand, PlayerLeaveCommand


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

        # start intermediate to assign responses to clients
        threading.Thread(target=self.dispatch_responses).start()

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

    def broadcast(self, data, without=None):
        for client_id in self.clients:
            if client_id != without:
                self.clients[client_id].send(data)

    def remove_client(self, id):
        if id in self.clients:
            del self.clients[id]

        self.request_command(PlayerLeaveCommand(time.time(), id))

    def request_command(self, command):
        self.request_queue.put(command)

    def dispatch_responses(self):
        while True:
            command = self.response_queue.get()
            print('dispatching response: ', command)

            if type(command) is NewPlayerCommand:
                # TODO: send message with new player + player position + initial state to client
                self.clients[command.id].send(command.to_json())

                # TODO: send message with new player + player position to everyone else
                self.broadcast(command.to_json_broadcast(), command.id)
            elif type(command) is PlayerLeaveCommand:
                self.broadcast(command.to_json_broadcast())
