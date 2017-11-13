from tornado.tcpclient import TCPClient, IOLoop
from tornado.iostream import StreamClosedError
from tornado import gen

class GameClient:
    def __init__(self):
        self.stream = None
        print("Starting client...")
        IOLoop.current().run_sync(self.setup)
        self.setup()

    @gen.coroutine
    def setup(self):
        self.stream = yield TCPClient().connect('127.0.0.1', 8081)
        print("TCP Connection setup")


    @gen.coroutine
    def _send_message(self, text):
        print "Sending " + text
        if text[-1] != '\n':
            text = text + '\n'
        yield self.stream.write(text)
        data = yield self.stream.read_until('\n')
        print("resp: " + data)

    def send_message(self, data):
        print 1
        yield self._send_message(data)