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

        self.mythread = threading.Thread(target=self._handle)
        self.mythread.start()

    def _handle(self):
        while self.up:
            socket_list = [self.socket]
            read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
            #print(read_sockets, write_sockets, error_sockets)
            for sock in read_sockets:
                try:
                    data = read_packet(sock)

                    if data:
                        #print("received", data, self.id, threading.get_ident())
                        self.server.request_command(data)
                        #self.broadcast(pack(data))
                    else:
                        print(id, " disconnected")
                        self.shutdown()

                except BaseException as e:
                    print("Error " + str(e))
                    self.shutdown()

    def shutdown(self):
        self.up = False
        self.socket.close()
        self.server.remove_client(self.id)
