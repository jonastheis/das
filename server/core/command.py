import json

class Command(object):
    def __init__(self, timestamp, id):
        self.timestamp = timestamp
        self.id = id
        self.applied = False

    def apply(self, response_queue):
        pass

    def to_json(self):
        return json.dumps(self.__dict__)

    def to_json_broadcast(self):
        return self.to_json()


class NewPlayerCommand(Command):
    def __init__(self, timestamp, id):
        Command.__init__(self, timestamp, id)
        self.initial_state = ""

    def __str__(self):
        return "NewPlayerCommand({0}, {1})".format(self.timestamp, self.id)

    def __repr__(self):
        return self.__str__()

    def apply(self, response_queue):
        # TODO: get the initial game state
        self.initial_state = "initial_state"
        self.applied = True

        response_queue.put(self)

    def to_json_broadcast(self):
        dict = self.__dict__.copy()
        del dict["initial_state"]
        return json.dumps(dict)
