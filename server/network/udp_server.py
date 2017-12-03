import socket
import threading
import select
from common.network_util import send_udp_message, read_udp_message
from common.constants import *
logger = logging.getLogger("sys." + __name__.split(".")[-1])


class UDPServer(object):
    """
    A wrapper for a UDP socket / server.
    Runs in separate thread and listens for input of the socket.
    """

    def __init__(self, port, host="127.0.0.1"):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((host, port))
        self.up = True

        self.inputs = [self.socket]

        self.mythread = threading.Thread(target=self._handle)
        self.mythread.start()

        logger.info("UDP Server @ port {} listening...".format(self.port))

    def __str__(self):
        return "UDPServer@{}:{}".format(self.host, self.port)

    def _handle(self):
        """
        Listens via blocking select for inputs from the socket.
        Runs in a separate thread.
        """
        while self.up:
            read_sockets, write_sockets, error_sockets = select.select(self.inputs, [], [])

            for sock in read_sockets:
                data, address = read_udp_message(sock)
                self.on_message(data, address)

    def on_message(self, data, address):
        """
        Called whenever a message received on the socket.
        :param data: the data received as a dictionary
        :param address: the udp address from where the received message was sent
        """
        if data['type'] == MSG_TYPE.PING:
            send_udp_message(self.socket, address, MSG_TYPE.PING)
        else:
            logger.warning("Received an unknown message type [{}]".format(data))

    def shutdown(self):
        """
        Shuts down the socket, makes sure that the thread can die.
        """
        logger.warning("Shutting down [{}]".format(self.__str__()))
        self.up = False
        self.socket.close()
