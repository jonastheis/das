import json
from .base_connection import BaseConnection
from common import command

import logging
logger = logging.getLogger("sys." + __name__.split(".")[-1])


class P2PConnection(BaseConnection):

    def __init__(self, socket, address, id, server):
        BaseConnection.__init__(self, socket, address, id)
        self.server = server
        self.heartbeat = 10000

    def __str__(self):
        return BaseConnection.__str__(self) + " [hb:{}]".format(self.heartbeat)


    def on_message(self, data):
        json_data = json.loads(data)

        if json_data['type'] == 'hb':
            self.heartbeat += 1000

        elif json_data['type'] == 'bc':
            # Put the message in the queue
            command_obj = command.Command.from_json(json_data['command'])
            self.server.request_queue.put(command_obj)

        elif json_data['type'] == 'init_req':
            self.server.meta_request_queue.put({"type": "get_map"})

            # if we start using the meta queue for other purposes we need to properly process it
            initial_map = self.server.meta_response_queue.get()

            # send initial map and pending commands so that the new server will be at the same state
            self.send(json.dumps({
                'type': 'init_res',
                'initial_map': initial_map,
                'pending_commands': self.server.get_current_commands()
            }))
        elif json_data['type'] == 'init_res':
            self.server.init_queue.put(json_data['initial_map'])

            for command_json in json_data['pending_commands']:
                self.server.request_queue.put_nowait(command.Command.from_json(command_json))
        else:
            logger.warning("Unrecognized message received from peer [{}]".format(data))

