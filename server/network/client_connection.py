import json
import time
from .base_connection import BaseConnection
from common import command
from common.constants import MSG_TYPE

import logging
logger = logging.getLogger("sys." + __name__.split(".")[-1])


class ClientConnection(BaseConnection):
    """
    A wrapper for a TCP socket.
    Runs in separate thread and listens for input of the socket.
    """

    def __init__(self, connection, address, id, server):
        BaseConnection.__init__(self, connection, address, id)
        self.server = server

    def on_message(self, data):
        json_data = json.loads(data)

        if json_data['type'] == MSG_TYPE.COMMAND:
            command_obj = command.Command.from_json(json_data['payload'])
            # set time of command to synchronised server time
            command_obj.timestamp = time.time()
            self.server.request_command(command_obj)
        elif json_data['type'] == MSG_TYPE.INIT:
            pass
        else:
            logger.warning("Received an unknown message type [{}]".format(data))

    def setup_client(self, id):
        """
        set up the client. blocking. the client should call a function with the same name first thing it connects.
        Server should send this data first thing
        :param map: map of the game
        :param id: id of the client
        :return: None
        """
        self.send(id, MSG_TYPE.INIT)

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