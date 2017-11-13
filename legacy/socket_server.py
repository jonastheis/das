import socket, sys, pycos

active_users = {}

def process(conn, task=None):
    data = ''
    while True:
        data += yield conn.recv(1)
        if data[-1] == '|':
            print('received: %s' % data)
            _send_to_all(data)
            data = ''

def server_proc(host, port, task=None):
    task.set_daemon()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # setup socket for asynchronous I/O with pycos
    sock = pycos.AsyncSocket(sock)
    sock.bind((host, port))
    sock.listen(128)

    while True:
        conn, addr = yield sock.accept()
        pycos.Task(process, conn)
        active_users[addr[0] + str(addr[1])] = conn

pycos.Task(server_proc, '', 8081)

def _send_to_all(data):
    for (addr, conn) in active_users.items():
        print("sending " + data + " to " + str(addr) + str(conn))
        pycos.Task(_send, data, conn)

def _send_to_client(client, data):
    if active_users[client]:
        conn = active_users[client]
        pycos.Task(_send, data, conn)

def _send(data, conn):
    yield conn.sendall(data)

while True:
    cmd = sys.stdin.readline().strip().lower()
    if cmd == 'exit' or cmd == 'quit':
        break