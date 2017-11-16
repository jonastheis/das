import json

class Command(object):
    def __init__(self, timestamp, id):
        self.type = type(self).__name__
        self.timestamp = timestamp
        self.id = id
        self.applied = False

    def apply(self, response_queue):
        pass

    def to_json(self):
        return json.dumps(self.__dict__)

    def to_json_broadcast(self):
        return self.to_json()

    def __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items())
        )

    def __repr__(self):
        return self.__str__()


class NewPlayerCommand(Command):
    def __init__(self, timestamp, id):
        Command.__init__(self, timestamp, id)
        self.initial_state = ""

    def apply(self, response_queue):
        # TODO: get the initial game state
        self.initial_state = "initial_state"
        self.applied = True

        response_queue.put(self)

    def to_json_broadcast(self):
        dict = self.__dict__.copy()
        del dict["initial_state"]
        return json.dumps(dict)


class PlayerLeaveCommand(Command):
    def __init__(self, timestamp, id):
        Command.__init__(self, timestamp, id)

    def apply(self, response_queue):
        self.applied = True
        # TODO: actually remove player from game
        response_queue.put(self)
