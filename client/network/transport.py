import socket, threading, select, json
from common.network_util import read_message, pack, TCPConnectionError
from common.constants import *
from common.command import Command

import logging
logger = logging.getLogger("sys." + __name__.split(".")[-1])


class ClientTransport:
    def __init__(self, game, port=TRANSPORT.port, host=TRANSPORT.host):
        self.game = game
        self.id = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        logger.info("Connection established to port Server@{}:{}".format(host, port))

    def check_recv(self):
        while self.game.up:
            socket_list = [self.sock]
            read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
            for sock in read_sockets:
                # incoming message from remote server
                try:
                    data = read_message(sock)
                except TCPConnectionError as e:
                    logger.error(str(e))
                    self.shutdown()
                    return

                if not data:
                    logger.error('\nDisconnected from server')
                    self.shutdown()
                    return
                else:
                    # TODO: double check if that's the correct behaviour
                    # execute all commands from server
                    command_obj = Command.from_json(data)
                    logger.debug("received message {}".format(command_obj.__str__()[:GLOBAL.MAX_LOG_LENGTH]))
                    command_obj.apply(self.game)


    def listen(self):
        transport_thread = threading.Thread(target=self.check_recv)
        transport_thread.daemon = True
        transport_thread.start()

    def setup_client(self):
        """
        This BLOCKING function will be called in the creation of each client. It will synchronously wait for the server
        to sent the game map and clientId
        :return: map and id
        """

        id = read_message(self.sock)
        # wait until i receive my own join message. This is needed to get the initial state
        while True:
            join_str = read_message(self.sock)
            join_dict = json.loads(join_str)
            if join_dict["type"] == "NewPlayerCommand" and join_dict['client_id'] == id:
                return id, join_dict['initial_state']

    def send_data(self, data):
        """
        send data to server
        :param data: string data to be sent
        :return:
        """
        try:
            logger.debug("sending {}".format(data))
            self.sock.sendall(pack(data))
        except Exception as e:
            logger.error("Error while sending data " + str(e))


    def shutdown(self):
        self.game.up = False
        self.sock.close()



