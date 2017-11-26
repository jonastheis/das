

class Event:


    def __init__(self, eventType, playerId, timeStamp):
        self.type = type(self).__name__
        self.eventType = eventType
        self.playerId = playerId
        self.timeStamp = timeStamp
