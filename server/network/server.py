import socket
import threading
import select
# from common.network_util import read_encoded

class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

        self.clients = dict()

    def listen(self):
        self.sock.listen(128)
        while True:
            client, address = self.sock.accept()
            id = str(address[0]) + str(address[1])
            print("Connection from " + id)
            self.clients[id] = client

            # not sure if this is good or not
            client.settimeout(60)

            threading.Thread(target = self.HandleClient, args = (client,id)).start()

    def HandleClient(self, client, id):
        while True:
            socket_list = [client]
            read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
            for sock in read_sockets:
                data = sock.recv(1024)
                # data = read_encoded(sock)
                if data:
                    print("received" , data , id)
                    self.broadcast(data)
                else:
                    print(id + " disconnected")
                    del self.clients[id]

    def broadcast(self, data):
        for (addr, sock) in self.clients.items():
            sock.send(data)



port_num = 8081
ThreadedServer('',port_num).listen()