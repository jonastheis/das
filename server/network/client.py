import threading
import select, json
from common.network_util import read_message, pack, TCPConnectionError
from common.constants import logger
from common import command


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

            for sock in read_sockets:
                # read_packet raises exception if there is no data -> client is disconnecting
                try:
                    data = read_message(sock)
                    logger.debug("Received from client {}: [{}...]".format(self.id, data[:20]))
                    # if there is data pass it to the game engine

                    # TODO: should there be a way to automate this? definitely.
                    json_data = json.loads(data)
                    if json_data['type'] == 'MoveCommand':
                        command_obj = command.MoveCommand(json_data['client_id'], json_data['value'], json_data['direction'])
                    elif json_data['type'] == 'NewPlayerCommand':
                        command_obj = command.NewPlayerCommand(json_data['client_id'])
                    elif json_data['type'] == 'PlayerLeaveCommand':
                        command_obj = command.PlayerLeaveCommand(json_data['client_id'])
                    elif json_data['type'] == 'AttackCommand':
                        command_obj = command.AttackCommand(json_data['client_id'], json_data['target_id'])
                    elif json_data['type'] == 'HealCommand':
                        command_obj = command.HealCommand(json_data['client_id'], json_data['target_id'])
                    else:
                        logger.error("Error:: Unrecognized command received. skipping...")
                        continue

                    self.server.request_command(command_obj)

                except TCPConnectionError:
                    self.shutdown()

            # shutdown connection if there is an error
            for sock in error_sockets:
                self.shutdown()

    def setup_client(self, id):
        """
        DEPRECATED
        set up the client. blocking. the client should call a function with the same name first thing it connects.
        Server should send this data first thing
        :param map: map of the game
        :param id: id of the client
        :return: None
        """
        self.send(id)

    def shutdown(self):
        self.up = False
        self.socket.close()
        self.server.remove_client(self.id)

    def send(self, data):
        self.socket.sendall(pack(data))

