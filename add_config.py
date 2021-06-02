import socket
import sys
import time

HOST = '127.0.0.1'
PORTS = {
    "zebrasrv": 2600,
    "zebra": 2601,
    "ripd": 2602,
    "ripngd": 2603,
    "ospfd": 2604,
    "bgpd": 2605,
    "ospf6d": 2606,
    "ospfapi": 2607,
    "isisd": 2608,
    "staticd": 2616
}


def main(argv):
    daemon = argv[0]
    command = argv[1]
    command = 'cisco\nenable\ncisco\n' + command + '\nexit\nexit'
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORTS[daemon]))
        s.sendall(bytes(command, 'utf-8'))
        time.sleep(1)
        print(s.recv(2048)[300:].decode('utf-8'))


if __name__ == "__main__":
    main(sys.argv[1:])
