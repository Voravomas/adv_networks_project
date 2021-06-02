import socket

BUF_SIZE = 2**15  # 32768


def server(server_host_port: tuple) -> str:
    """
    Function that waits for one message from client
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(server_host_port)

    s.listen(1)
    conn, addr = s.accept()

    data = conn.recv(BUF_SIZE)
    conn.close()
    return data.decode('utf-8')


def client(server_host_port: tuple, msg: str) -> None:
    """
    Function that sends msg to server_host_port
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(server_host_port)
    s.sendto(msg.encode('utf-8'), server_host_port)
    s.close()
