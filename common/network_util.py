

def read_encoded(sock):
    recvd = ''
    while True:
        data = sock.recv(1)
        if not data:
            raise RuntimeError("Connection Error")
        elif data != '\n':
            recvd += data
        else:
            return recvd
