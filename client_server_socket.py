import socket

STOP_WORD = "END".encode('utf-8')
BUF_SIZE = 2**32  # 32768


def server(server_host_port: tuple) -> list:
    """
    Function that listens for a message from server_host_port
    until STOP_WORD is received and returns a list of all messages
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(server_host_port)

    print("Started server")
    res = []
    while True:
        data, addr = s.recvfrom(BUF_SIZE)
        res.append(data.decode('utf-8'))
        if data == STOP_WORD:
            break
    s.close()
    return res


def client(client_host_port: tuple, server_host_port: tuple, msg: str) -> None:
    """
    Function that sends information to server_host_port
    from client_host_port
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(client_host_port)

    s.sendto(msg.encode('utf-8'), server_host_port)
    s.sendto(STOP_WORD, server_host_port)
    s.close()
    return
