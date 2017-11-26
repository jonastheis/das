import threading
import select, json
from common.network_util import read_message, pack, TCPConnectionError
from common.constants import logger
from common import command


class Client(object):
    """
    A wrapper for a TCP socket.
    Runs in separate thread and listens for input of the socket.
    """

    def __init__(self, socket, address, id, server):
        self.socket = socket
        self.address = address
        self.id = id
        self.server = server
        self.up = True

        self.inputs = [self.socket]

        self.mythread = threading.Thread(target=self._handle)
        self.mythread.start()

    def _handle(self):
        """
        Listens via blocking select for inputs from the socket.
        Runs in a separate thread.
        """
        while self.up:
            # This is important because we might client he socket while it is waiting in select
            # For now a continue is enough and in the next loop self.up is False
            try:
                read_sockets, write_sockets, error_sockets = select.select(self.inputs, [], self.inputs)
            except:
                logger.error("Error while checking client sockets")
                continue

            for sock in read_sockets:
                # read_packet raises exception if there is no data -> client is disconnecting
                try:
                    data = read_message(sock)
                    logger.debug("Received from client {}: [{}...]".format(self.id, data[:20]))
                    # if there is data pass it to the game engine

                    command_obj = command.Command.from_json(data)

                    self.server.request_command(command_obj)

                except TCPConnectionError:
                    self.shutdown()

            # shutdown connection if there is an error
            for sock in error_sockets:
                self.shutdown()

    def setup_client(self, id):
        """
        DEPRECATED
        set up the client. blocking. the client should call a function with the same name first thing it connects.
        Server should send this data first thing
        :param map: map of the game
        :param id: id of the client
        :return: None
        """
        self.send(id)

    def shutdown(self):
        """
        Shuts down the socket, makes sure that the thread can die and notifies the server about the ending connection.
        """
        self.up = False
        self.socket.close()
        self.server.remove_client(self.id)

    def send(self, data):
        """
        Sends the data via the socket.
        :param data: the data to be sent
        """
        self.socket.sendall(pack(data))

