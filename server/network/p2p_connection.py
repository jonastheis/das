import json
from .base_connection import BaseConnection
from common import command
from common.constants import MSG_TYPE, HEARTBEAT

import logging
logger = logging.getLogger("sys." + __name__.split(".")[-1])


class P2PConnection(BaseConnection):

    def __init__(self, socket, address, id, server):
        BaseConnection.__init__(self, socket, address, id)
        self.server = server
        self.heartbeat = HEARTBEAT.INIT
        self.peer_connections = 0

    def __str__(self):
        return "Peer@" + BaseConnection.__str__(self).split("@")[1] + " [hb:{}]".format(self.heartbeat)


    def on_message(self, data):
        json_data = json.loads(data)

        if json_data['type'] == MSG_TYPE.HBEAT:
            self.heartbeat += HEARTBEAT.INC
            self.peer_connections = int(json_data['payload']['num_connections'])

        elif json_data['type'] == MSG_TYPE.BCAST:
            # Put the message in the queue
            command_obj = command.Command.from_json(json_data['command'])
            self.server.request_queue.put(command_obj)

        elif json_data['type'] == MSG_TYPE.INIT_REQ:
            self.server.meta_request_queue.put({"type": "get_map"})

            # if we start using the meta queue for other purposes we need to properly process it
            initial_map = self.server.meta_response_queue.get()

            # send initial map and pending commands so that the new server will be at the same state
            self.send(json.dumps({
                'type': MSG_TYPE.INIT_RES,
                'initial_map': initial_map,
                'pending_commands': self.server.get_current_commands()
            }))
        elif json_data['type'] == MSG_TYPE.INIT_RES:
            self.server.init_queue.put(json_data['initial_map'])

            for command_json in json_data['pending_commands']:
                self.server.request_queue.put_nowait(command.Command.from_json(command_json))
        else:
            logger.warning("Unrecognized message received from peer [{}]".format(data))

