import threading
import select
from common.network_util import read_message, pack, TCPConnectionError


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
            read_sockets, write_sockets, error_sockets = select.select(self.inputs, [], self.inputs)

            for sock in read_sockets:
                # read_packet raises exception if there is no data -> client is disconnecting
                try:
                    data = read_message(sock)
                    #print(data)
                    # if there is data pass it to the game engine
                    #self.server.request_command(data)
                except TCPConnectionError:
                    self.shutdown()

            # shutdown connection if there is an error
            for sock in error_sockets:
                self.shutdown()

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

