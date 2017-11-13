from tornado.tcpserver import TCPServer, IOLoop
from tornado.iostream import StreamClosedError
from tornado import gen


class GameServer(TCPServer):
    """Tornado asynchronous echo TCP server."""
    clients = dict()

    @gen.coroutine
    def handle_stream(self, stream, address):
        ip, fileno = address
        print("Incoming connection from " + ip)
        self.clients[address] = stream
        while True:
            try:
                data = yield stream.read_until('\n')
                print("received " + data)
                yield self.broadcast(data)

            except StreamClosedError:
                print("Client " + str(address) + " left.")
                self.clients.pop(address)
                break

    @gen.coroutine
    def broadcast(self, data):
        for (address, sock) in self.clients.items():
            print("sending "  + data + " to " + str(address))
            sock.write(data+ '\n')

server = GameServer()
server.listen(8081)
print("Starting server on tcp://localhost:" + str(8081))
IOLoop.instance().start()
