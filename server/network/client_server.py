import hashlib
import threading
import queue
import time
from common.constants import logger
from .client_connection import ClientConnection
from common.command import NewPlayerCommand, PlayerLeaveCommand
from .base_server import BaseServer


class ClientServer(BaseServer):
    def __init__(self, request_queue, response_queue, port, host="127.0.0.1"):
        """
        Handler for all the incoming TCP connections of the clients.
        Listens for incoming connections and spawns a new Client (therefore also a thread) per connection.
        Waits in another thread for the response queue from the engine and dispatches events to the corresponding clients.
        """
        BaseServer.__init__(self,request_queue, response_queue, port, host)

        # start intermediate to assign responses to clients
        dispatch_thread = threading.Thread(target=self.dispatch_responses)
        dispatch_thread.daemon = True
        dispatch_thread.start()

        # This is a queue that the p2p_server will read from
        self.broadcast_queue = queue.Queue()

    def on_connection(self, connection, address):
        # create socket connection to client and remember relationship between id -> socket
        id = hashlib.md5("{0}:{1}".format(address[0], address[1]).encode('utf-8')).hexdigest()
        logger.info("Connection from {0}:{1}".format(address[0], address[1]))
        new_client = ClientConnection(connection, address, id, self)
        self.connections[id] = new_client
        new_client.setup_client(id)

        # send new player command to game engine
        self.request_command(NewPlayerCommand(id, timestamp=time.time()))

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
            logger.debug('dispatching [{}...] '.format(command.__str__()[:45]))

            if type(command) is NewPlayerCommand:
                # joining client is explicitly waiting for this response
                if command.client_id in self.connections:  # only if client is connected to this server
                    self.connections[command.client_id].send(command.to_json())
                self.broadcast(command.to_json_broadcast(), command.client_id)

            elif type(command) is PlayerLeaveCommand and command.is_killed:
                # shutdown ClientConnection if player gets killed (without notifying engine)
                if command.client_id in self.connections:  # only if client is connected to this server
                    self.connections[command.client_id].shutdown_killed()

            else:
                self.broadcast(command.to_json_broadcast())

