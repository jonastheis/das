import threading
import select
from common.network_util import read_message, pack, TCPConnectionError
from common.constants import GLOBAL

import logging
logger = logging.getLogger("sys." + __name__.split(".")[-1])


class BaseConnection(object):
    """
    A wrapper for a TCP socket.
    Runs in separate thread and listens for input of the socket.
    """

    def __init__(self, socket, address, id):
        self.socket = socket
        self.address = address
        self.id = id
        self.up = True

        self.inputs = [self.socket]

        self.mythread = threading.Thread(target=self._handle)
        self.mythread.start()

    def __str__(self):
        return "Connection@{}:{}".format(self.address[0], self.address[1])

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
                logger.error("Error while checking connection sockets")
                continue

            for sock in read_sockets:
                # read_packet raises exception if there is no data -> client is disconnecting
                try:
                    data = read_message(sock)
                    logger.debug("{} :: Received [{}]".format(self.__str__(), data[:GLOBAL.MAX_LOG_LENGTH]))
                    # if there is data pass it to the game engine

                    self.on_message(data)

                except TCPConnectionError:
                    self.shutdown()

            # shutdown connection if there is an error
            for sock in error_sockets:
                self.shutdown()

    def on_message(self, data):
        """
        Called whenever a message received on the
        :param data:
        :return:
        """
        pass

    def shutdown(self):
        """
        Shuts down the socket, makes sure that the thread can die.
        """
        logger.warning("Shutting down [{}]".format(self.__str__()))
        self.up = False
        self.socket.close()

    def send(self, data):
        """
        Sends the data via the socket.
        :param data: the data to be sent
        """
        logger.debug("{} :: sending message [{}]".format(self.__str__(), data[:GLOBAL.MAX_LOG_LENGTH]))
        self.socket.sendall(pack(data))

