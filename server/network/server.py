import hashlib
import threading
from common.constants import logger
from .client import ClientConnection
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


    def on_connection(self, connection, address):
        # create socket connection to client and remember relationship between id -> socket
        id = hashlib.md5("{0}:{1}".format(address[0], address[1]).encode('utf-8')).hexdigest()
        logger.info("Connection from {0}:{1}".format(address[0], address[1]))
        new_client = ClientConnection(connection, address, id, self)
        self.connections[id] = new_client
        new_client.setup_client(id)

        # send new player command to game engine
        self.request_command(NewPlayerCommand(id))


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
            logger.debug('dispatching [{}...] '.format(command.__str__()[:45]))

            if type(command) is NewPlayerCommand:
                # Note that the issuer of this command (joining client)
                # is explicitly waiting for this response
                self.connections[command.client_id].send(command.to_json())
                self.broadcast(command.to_json_broadcast(), command.client_id)

            elif type(command) is PlayerLeaveCommand and command.is_killed:
                #@Jonas I didn't use the self.remove_connection() because that Adds another PlayerLeave to the queue.
                # We should rethink this a bit
                self.connections[command.client_id].up = False
                self.connections[command.client_id].socket.close()
                if command.client_id in self.connections:
                    del self.connections[command.client_id]

            else:
                # if type is PlayerLeave and is_killed == true, we will come here wither way
                # broadcast to all others
                self.broadcast(command.to_json_broadcast())

