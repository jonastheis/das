import socket, threading, select, sys
from common.network_util import read_packet, pack
from common.constants import *

class ClientTransport:
    def __init__(self, game, port=TRANSPORT.port, host=TRANSPORT.host):
        self.game = game

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        transport_thread = threading.Thread(target=self.check_recv)
        transport_thread.daemon = True
        transport_thread.start()

        print("Transport Client listening on port {}".format(port))

    def check_recv(self):
        while True:
            socket_list = [self.sock]
            read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
            for sock in read_sockets:
                # incoming message from remote server
                data = read_packet(sock)
                if not data:
                    print('\nDisconnected from server')
                    sys.exit()
                else:
                    # TODO: create a new Command object from Command.from_json and append to game.commands
                    print("received", data)

    def send_data(self, data):
        try:
            self.sock.sendall(pack(data))
        except Exception as e:
            print("Error while sending data " +  str(e))

