import json
import time
from .base_connection import BaseConnection
from common import command
from common.network_util import pack
from common.constants import MSG_TYPE, GLOBAL

import logging
logger = logging.getLogger("sys." + __name__.split(".")[-1])


class ClientConnection(BaseConnection):
    """
    A wrapper for a TCP socket.
    Runs in separate thread and listens for input of the socket.
    """

    def __init__(self, connection, address, id, server):
        self.server = server
        BaseConnection.__init__(self, connection, address, id)

    def on_message(self, data):
        json_data = json.loads(data)

        if json_data['type'] == MSG_TYPE.COMMAND:
            command_obj = command.Command.from_json(json_data['payload'])
            # set time of command to synchronised server time
            command_obj.timestamp = time.time()
            self.server.request_command(command_obj)
        elif json_data['type'] == MSG_TYPE.INIT:
            id = json_data['payload']
            if id == '':
                # send new player command to game engine
                self.server.request_command(command.NewPlayerCommand(self.id, timestamp=time.time()))

                # setup_client will be called in ClientServer dispatch method, once client is placed on map
            else:
                # player is rejoining
                old_id = self.id
                self.id = id

                # send init message to client
                self.setup_client()

                # only now add client to connections so that it starts receiving updates
                self.server.add_connection(self, old_id, self.id)
        else:
            logger.warning("Received an unknown message type [{}]".format(data))

    def setup_client(self, initial_map=None):
        """
        Sends the init message to the client with id and the initial map.
        :param initial_map: if not provided will be retrieved from the engine
        """
        if initial_map is None:
            self.server.meta_request_queue.put({"type": "get_map"})

            # if we start using the meta queue for other purposes we need to properly process it
            initial_map = self.server.meta_response_queue.get()

        data = json.dumps({
            'type': MSG_TYPE.INIT,
            'id': self.id,
            'initial_map': initial_map
        })
        logger.debug("{} :: sending init message [{}]".format(self.__str__(), data[:GLOBAL.MAX_LOG_LENGTH]))
        self.socket.sendall(pack(data))

    def shutdown(self):
        """
        Shuts down the socket, makes sure that the thread can die and notifies the server about the ending connection.
        """
        BaseConnection.shutdown(self)
        self.server.remove_connection(self.id)

        # need to notify engine about the connection loss with the client -> so he can be removed from the field
        self.server.request_command(command.PlayerLeaveCommand(self.id, is_killed=False, timestamp=time.time()))

    def shutdown_killed(self):
        """
        Shuts down the socket, makes sure that the thread can die.
        """
        BaseConnection.shutdown(self)
        self.server.remove_connection(self.id)