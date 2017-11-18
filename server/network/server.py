import hashlib
import socket
import threading

from common.user import User
from common.constants import USERS, logger
from common.command import NewPlayerCommand, PlayerLeaveCommand, MoveCommand
from .client import Client


class ThreadedServer(object):
    def __init__(self, request_queue, response_queue, metadata_queue, port, host="127.0.0.1"):
        self.request_queue = request_queue
        self.response_queue = response_queue
        self.metadata_queue = metadata_queue
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
        logger.info("Server listening on port {}".format(self.port))
        while True:
            # wait for incoming connections
            connection, address = self.sock.accept()

            # create socket connection to client and remember relationship between id -> socket
            id = hashlib.md5("{0}:{1}".format(address[0], address[1]).encode('utf-8')).hexdigest()
            logger.info("Connection from {0}:{1}".format(address[0], address[1]))
            new_client = Client(connection, address, id, self)
            self.clients[id] = new_client
            new_client.setup_client(id)

            # send new player command to game engine
            # @Jonas: I thought timestamp would be time of the creation of each command, hence could be created inside
            self.request_command(NewPlayerCommand(id))

    def broadcast(self, data, without=None):
        for client_id in self.clients:
            if client_id != without:
                self.clients[client_id].send(data)

    def remove_client(self, id):
        if id in self.clients:
            del self.clients[id]

        self.request_command(PlayerLeaveCommand(id))

    def request_command(self, command):
        self.request_queue.put(command)

    def dispatch_responses(self):
        while True:
            command = self.response_queue.get()
            logger.debug('dispatching [{}...] '.format(command.__str__()[:25]))

            if type(command) is NewPlayerCommand:
                # TODO: send message with new player + player position + initial state to client
                self.clients[command.client_id].send(command.to_json())

                # TODO: send message with new player + player position to everyone else
                self.broadcast(command.to_json_broadcast(), command.client_id)
            elif type(command) is PlayerLeaveCommand:
                self.broadcast(command.to_json_broadcast())

            else:
                # sent an ok to the issuer

                # broadcast to all others
                self.broadcast(command.to_json())

