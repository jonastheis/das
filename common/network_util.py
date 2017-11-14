
def packetize(data):
    """
    note that this function is silly now,  but it abstracts away if we decide to move into a  more complex
    approach (2byte size + data etc.)
    """
    if type(data) != str:
        data = str(data)

    if data[-1] != '\n':
        data += '\n'

    return data


def pack(data):
    return bytes(packetize(data), "utf-8")


def read_packet(sock):
    recvd = ''
    while True:
        data = sock.recv(1)
        data = str(data, "utf-8")
        if not data:
            raise RuntimeError("Connection Error While reading.")
        elif data != '\n':
            recvd += data
        else:
            return recvd
