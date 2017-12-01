import json

from .base_connection import BaseConnection
from common.constants import logger

class P2PConnection(BaseConnection):

    def __init__(self, socket, address, id, server):
        BaseConnection.__init__(self, socket, address, id )
        self.server = server
        self.heartbeat = 10000

    def on_message(self, data):
        json_data = json.loads(data)

        if json_data['type'] == 'hb' :
            self.heartbeat += 1000

        elif json_data['type'] == 'bc':
            pass
        else:
            logger.warn("Unrecognized message received from peer [{}]".format(data))

