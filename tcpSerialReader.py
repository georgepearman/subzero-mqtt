import socket

def getByteIterator(ip, port):
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((ip, port))

    while True:
        result = clientsocket.recv(1024)
        for b in result:
            yield b
