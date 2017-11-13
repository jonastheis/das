from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol


class Client(Protocol):
    def __init__(self, game):
        self.game = game

    def sendMessage(self, msg):
        self.transport.write("MESSAGE %s\n" % msg)

    def connectionMade(self):
        print("Connection established with the server")

    def dataReceived(self, data):
        print("Received " + data)


point = TCP4ClientEndpoint(reactor, "localhost", 8081)
d = connectProtocol(point, Client(None))
reactor.run()
