from twisted.internet import protocol, reactor, endpoints

class ServerProtocol(protocol.Protocol):
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        ip, port = self.transport.client
        print("new connection from " + str(ip) + ':' + str(port))
        self.factory.clients[str(ip) + ':' + str(port)] = self

    def dataReceived(self, data):
        for (addr, c) in self.factory.clients.items():
            c.transport.write(data)


class EchoFactory(protocol.Factory):
    def __init__(self):
        self.clients = dict()

    def buildProtocol(self, addr):
        return ServerProtocol(self)

endpoints.serverFromString(reactor, "tcp:8081").listen(EchoFactory())
reactor.run()