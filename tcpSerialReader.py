import socket
import select

def getByteIterator(ip, port):
    while True:
        for b in readFromSocket(ip, port):
            yield b

def readFromSocket(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, port))
        s.setblocking(0)

        while True:
            timeoutSeconds = 20
            ready = select.select([s], [], [], timeoutSeconds)
            if not ready[0]:
                return

            result = s.recv(1024)
            for b in result:
                yield b
