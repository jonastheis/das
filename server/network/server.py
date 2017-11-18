import socket
import hashlib
import threading

from common.constants import logger
from .client import Client
from common.command import NewPlayerCommand, PlayerLeaveCommand


class ThreadedServer(object):

    def __init__(self, request_queue, response_queue, port, host="127.0.0.1"):
        """
        Handler for all the incoming TCP connections of the clients.
        Listens for incoming connections and spawns a new Client (therefore also a thread) per connection.
        Waits in another thread for the response queue from the engine and dispatches events to the corresponding clients.
        """
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
        """
        Listens for incoming connections and spawns a new Client (therefore also a thread) per connection.
        """
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
        """
        Broadcast the data to all clients except "without".
        :param data: the data to be broadcasted
        :param without: broadcast to everyone except this client
        """
        for client_id in self.clients:
            if client_id != without:
                self.clients[client_id].send(data)

    def remove_client(self, id):
        """
        Removes the client from the list of currently connected clients and notifies the engine about it.
        :param id: the client to be removed
        """
        if id in self.clients:
            del self.clients[id]

        self.request_command(PlayerLeaveCommand(id))

    def request_command(self, command):
        """
        Put an event on the request queue to the engine.
        :param event: the event to be passed to the engine
        """
        self.request_queue.put(command)

    def dispatch_responses(self):
        """
        Dispatches events to the corresponding clients. Runs in another thread and blocks when the queue is empty.
        """
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

