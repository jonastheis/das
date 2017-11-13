import socket
import pycos
import client.game

sock = None
HOST = ''
PORT = 8081

def _init(host, port, task=None):
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock = pycos.AsyncSocket(sock)
    yield sock.connect((host, port))
    pycos.logger.debug("Socket Client Connected")

def _send(msg, task=None):
    yield sock.sendall(str(msg).encode())


def async_receive(task=None):
    data = ''
    while True:
        _data = yield sock.recv(1)
        if _data == -1:
            continue
        else:
            data += _data
            if data[-1] == '|':
                print('received: %s' % data)
                # self.commands.append(data)
                data = ''

def init():
    global sock
    pycos.logger.setLevel(pycos.Logger.DEBUG)
    sock = pycos.Task(_init, HOST, PORT)
    pycos.Task(async_receive)
    print(sock)
    return sock


def send_message(data):
    pycos.Task(_send, str(data))
