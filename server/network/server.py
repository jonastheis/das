import socket
import threading
import select
from common.network_util import read_packet, pack

class ThreadedServer(object):
    def __init__(self, port, host="127.0.0.1"):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

        self.clients = dict()

        print("Server listening on port " + str(port))

    def listen(self):
        self.sock.listen(128)
        while True:
            client, address = self.sock.accept()
            id = str(address[0]) + str(address[1])
            print("Connection from " + id)
            self.clients[id] = client

            # not sure if this is good or not
            client.settimeout(60)

            threading.Thread(target = self.handle_client, args = (client,id)).start()
            # self.handle_client(client, id)

    def handle_client(self, client, id):
        up = True
        while up:
            socket_list = [client]
            read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
            for sock in read_sockets:
                # data = sock.recv(1024)
                try:
                    data = read_packet(sock)

                    if data:
                        print("received", data, id)
                        self.broadcast(pack(data))
                    else:
                        print(id + " disconnected")
                        if (id in self.clients):
                            del self.clients[id]
                            up = False

                except BaseException as e:
                    print("Error " + str(e))
                    if (id in self.clients):
                        print(id + " disconnected")
                        del self.clients[id]
                        up = False

    def broadcast(self, data):
        for (addr, sock) in self.clients.items():
            sock.sendall(data)


if __name__ == '__main__':
    port_num = 8081
    server = ThreadedServer(port_num, '')

    server.listen()
