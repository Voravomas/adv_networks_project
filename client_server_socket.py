import socket
import sys

BUF_SIZE = 2**15  # 32768


def server(server_host_port: tuple) -> str:
    """
    Function that waits for one message from client
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(server_host_port)

    print("Started server")
    print(s)
    s.listen(1)
    conn, addr = s.accept()
    print("Connected to client")

    data = conn.recv(BUF_SIZE)
    if data:
        print(data.decode('utf-8'))
    conn.close()
    return data.decode('utf-8')


def client(server_host_port: tuple, msg: str) -> None:
    """
    Function that sends msg to server_host_port
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(server_host_port)
    print(s)
    s.sendto(msg.encode('utf-8'), server_host_port)
    s.close()
    return


def main():
    argv = sys.argv
    if argv[1] == "client":
        client((argv[2], int(argv[3])), argv[4])
    elif argv[1] == "server":
        server((argv[2], int(argv[3])))

main()
