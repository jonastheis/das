import socket, threading, select, json

import sys

from common.network_util import read_message, pack, TCPConnectionError, send_udp_message, read_udp_message
from common.constants import *
from common.command import Command

import logging
logger = logging.getLogger("sys." + __name__.split(".")[-1])
gLogger = logging.getLogger("game." + __name__.split(".")[-1])


class ClientTransport:
    def __init__(self, game, servers):
        self.game = game
        self.id = None
        self.servers = servers

        self.sock = None

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
                    self.reconnect()
                    continue

                if not data:
                    logger.error('Disconnected from server. Try to reconnect')
                    self.reconnect()
                    continue
                else:
                    # execute all commands from server
                    json_data = json.loads(data)
                    logger.debug("received message {}".format(data[:GLOBAL.MAX_LOG_LENGTH]))
                    if json_data['type'] == MSG_TYPE.COMMAND:
                        command_obj = Command.from_json(json_data['payload'])
                        command_obj.apply(self.game)
                    elif json_data['type'] == MSG_TYPE.EXIT:
                        gLogger.error("Died, disconnect from server")
                        self.shutdown()
                        return
                    else:
                        logger.warning("Unknown message type received")

    def listen(self):
        transport_thread = threading.Thread(target=self.check_recv)
        transport_thread.daemon = True
        transport_thread.start()

    def reconnect(self):
        self.sock.close()

        # start setup process again
        id, map = self.setup_client(reconnect=True)
        # restore map from server
        self.game.from_serialized_map(map)
        logger.info("Reconnected client ({0}) and restored game state from server".format(self.id))

    def setup_client(self, reconnect=False):
        """
        This BLOCKING function will be called in the creation of each client. It will synchronously wait
        and pick the closest server and then retrieve the initial game state.
        :return: map and id
        """
        host, port = self.get_closest_server()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        logger.info("Connection established to Server@{}:{}".format(host, port))

        if reconnect:
            return self.get_initial_map(self.id)
        return self.get_initial_map()

    def get_initial_map(self, id=''):
        """
        Waits (blocking) for the server to sent the game map and clientId.
        :param id: if id is provided server interprets connection as reconnecting player
        :return: map and id
        """
        # request initial map from server
        self.send_data(id, MSG_TYPE.INIT)

        # the first message the server will send is the init message, so doing this is fine
        data = read_message(self.sock)
        data_json = json.loads(data)
        if data_json['type'] == MSG_TYPE.INIT:
            id = data_json['id']
            initial_map = data_json['initial_map']
            return id, initial_map
        else:
            logger.error('Error while setting things up. Try reconnecting...')
            self.reconnect()
            return


    def send_data(self, data, type=None):
        """
        send data to server
        :param data: string data to be sent
        :return:
        """
        try:
            if not type is None:
                data = json.dumps({"type": type, "payload": data})

            logger.debug("sending {}".format(data))
            self.sock.sendall(pack(data))
        except Exception as e:
            logger.error("Error while sending data " + str(e))

    def shutdown(self):
        self.game.up = False
        self.sock.close()

    def get_closest_server(self):
        """
        Finds the closest server out of self.servers by pinging them.
        :return: address (host, port) of the fastest/closest server
        """
        logger.info("Finding closest server to connect to.")

        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        count = 1
        # wait until first successful response is received -> fastest server
        while True:
            # send ping message to all servers
            for server in self.servers:
                send_udp_message(udp_sock, server, MSG_TYPE.PING)

            # timeout: send message again if no positive response
            read_sockets, write_sockets, error_sockets = select.select([udp_sock], [], [], 2)
            for sock in read_sockets:
                data, address = read_udp_message(sock)
                if data['type'] == MSG_TYPE.PING:
                    udp_sock.close()
                    return address

            logger.warning("Attempt {}. No success with any server".format(count))
            # terminate client after 5 unsuccessful tries
            if count > 5:
                logger.error('Could not connect to any server. Terminate.')
                self.game.up = False
                sys.exit()
            count += 1
