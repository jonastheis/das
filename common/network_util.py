import struct

SIZE_BYTES = 2
STRUCT_IDENTIFIER = ">H"  # big-endian unsigned short (2 bytes)
MAX_SIZE = 65535  # unsigned 2 bytes


def pack(data):
    """
    Wraps a message which is to be sent via a TCP socket according to the protocol:
    big-endian 2bytes message length + message in bytes
    :param data: the data to be sent
    :return: the prepared message as a byte string
    """
    data_bytes = data.encode('utf8')
    size = struct.pack(STRUCT_IDENTIFIER, len(data_bytes))
    return b"".join([size, data_bytes])


def read_message(socket):
    """
    Receives a message from a TCP socket of various length.
    The first to bytes in big-endian order signal the size of the current message to receive.
    By first receiving the message in chunks there is a performance gain of up to 10x.
    :param socket: the socket to receive from
    :return: the full received message as a utf8 string
    """
    total_len = 0
    total_data = []
    size = MAX_SIZE

    size_data = b""
    recv_size = 8192
    while total_len < size:
        sock_data = socket.recv(recv_size)

        # if empty -> connection is closing
        if not sock_data:
            raise TCPConnectionError("Connection error while reading data.")
        elif not total_data:
            # first time receiving -> check whether it's enough bytes to read the total size of message
            if len(sock_data) > SIZE_BYTES:
                size_data = sock_data
                size = struct.unpack(STRUCT_IDENTIFIER, size_data[:SIZE_BYTES])[0]  # expect big endian unsigned short
                recv_size = size
                total_data.append(size_data[SIZE_BYTES:])
            else:
                # if not enough add to size_data and read again from socket
                size_data.join([sock_data])
        else:
            # append chunk to total data
            total_data.append(sock_data)

        # calculate total_len from all chunks in total_data
        total_len = sum([len(i) for i in total_data])

    return b"".join(total_data).decode('utf8')


class TCPConnectionError(Exception):
    def __init__(self, msg="Error with the connection"):
        super(TCPConnectionError, self).__init__(msg)
