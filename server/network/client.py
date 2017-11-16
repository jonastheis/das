import threading
import select
from common.network_util import read_packet, pack


class Client(object):
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
        while self.up:
            read_sockets, write_sockets, error_sockets = select.select(self.inputs, [], self.inputs)

            # TODO: properly check for data and receive data with prefixed size
            for sock in read_sockets:
                # read_packet raises exception if there is no data -> client is disconnecting
                try:
                    data = read_packet(sock)
                    # if there is data pass it to the game engine
                    #self.server.request_command(data)
                except BaseException as e:
                    self.shutdown()

            # shutdown connection if there is an error
            for sock in error_sockets:
                self.shutdown()

    def shutdown(self):
        self.up = False
        self.socket.close()
        self.server.remove_client(self.id)

    def send(self, data):
        self.socket.sendall(pack(data))

