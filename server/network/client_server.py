import hashlib, time, queue, threading
from .client_connection import ClientConnection
from common.command import NewPlayerCommand, PlayerLeaveCommand
from .base_server import BaseServer
from common.constants import GLOBAL, MSG_TYPE, TRANSPORT
from .udp_server import UDPServer

import logging
logger = logging.getLogger("sys." + __name__.split(".")[-1])



class ClientServer(BaseServer):
    def __init__(self, request_queue, response_queue, meta_request_queue, meta_response_queue, port, host=""):
        """
        Handler for all the incoming TCP connections of the clients.
        Listens for incoming connections and spawns a new Client (therefore also a thread) per connection.
        Waits in another thread for the response queue from the engine and dispatches events to the corresponding clients.
        """
        BaseServer.__init__(self, request_queue, response_queue, port, host)
        self.meta_request_queue = meta_request_queue
        self.meta_response_queue = meta_response_queue

        # start intermediate to assign responses to clients
        dispatch_thread = threading.Thread(target=self.dispatch_responses)
        dispatch_thread.daemon = True
        dispatch_thread.start()

        # This is a queue that the p2p_server will read from
        self.broadcast_queue = queue.Queue()

        # start udp server to let clients ping server
        self.udp_server = UDPServer(port, host)

        # save new connections in here until we're sure whether client is reconnecting
        self.pending_connections = {}

    def on_connection(self, connection, address):
        # create socket connection to client and remember relationship between id -> socket
        # id might be only temporary if a client is rejoining
        id = hashlib.md5("{0}:{1}".format(address[0], address[1]).encode('utf-8')).hexdigest()
        logger.info("Connection from {0}:{1}".format(address[0], address[1]))
        new_client = ClientConnection(connection, address, id, self)

        # add to pending connections as long as we don't know the id
        self.pending_connections[id] = new_client

    def request_command(self, command):
        """
        Put a command on the request queue to the engine.
        :param command: the command to be passed to the engine
        """

        # Will be read by the p2p_server
        self.broadcast_queue.put(command)

        self.request_queue.put(command)

    def dispatch_responses(self):
        """
        Dispatches events to the corresponding clients. Runs in another thread and blocks when the queue is empty.
        """
        while True:
            command = self.response_queue.get()
            logger.debug('dispatching [{}] '.format(command.__str__()[:GLOBAL.MAX_LOG_LENGTH]))

            if type(command) is NewPlayerCommand:
                # joining client is explicitly waiting for this response
                if command.client_id in self.pending_connections:  # only if client is connected to this server
                    # only add client now to connections so that it receives all updates after the initial state
                    # has been transferred (only this thread sends out game updates to users).
                    # This makes sure that client and server are in sync.
                    self.add_connection(self.pending_connections[command.client_id], command.client_id)
                    self.connections[command.client_id].setup_client(command.initial_state)

                self.broadcast(command.to_json_broadcast(), command.client_id, MSG_TYPE.COMMAND)

            elif type(command) is PlayerLeaveCommand and command.is_killed:
                # shutdown ClientConnection if player gets killed (without notifying engine)
                if command.client_id in self.connections:  # only if client is connected to this server
                    self.connections[command.client_id].send('', MSG_TYPE.EXIT)
                    self.connections[command.client_id].shutdown_killed()

            else:
                self.broadcast(command.to_json_broadcast(), None, MSG_TYPE.COMMAND)

    def add_connection(self, connection, old_id, new_id=None):
        """
        Adds connection to self.connections and removes it from self.pending_connections
        :param connection: the connection to add
        :param old_id: the id in self.pending_connections
        :param new_id: the id to set in self.connections. If not set will be old_id
        """
        if new_id is None:
            new_id = old_id

        if old_id in self.pending_connections:
            del self.pending_connections[old_id]

        self.connections[new_id] = connection
        self.udp_server.delay += TRANSPORT.UDP_DELAY_PER_PLAYER
