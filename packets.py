def listToHexStr(byteList):
    return " ".join(toHexStr(b) for b in byteList)

def toHexStr(b):
    return f"{b:#04x}"

class Packet:
    def __init__(self):
        self.header = []
        self.length = 0
        self.payload = []
        self.footer = []

    def getBytes(self):
        return self.header + [self.length] + self.payload + self.footer

    def __str__(self):
        return "Packet: " + listToHexStr(self.getBytes())

    def __eq__(self, other):
        return type(self) == type(other) and self.getBytes() == other.getBytes()

    def __hash__(self):
        return hash(tuple(self.getBytes()))

class InterprettedPacket:
    def __init__(self, src, dst, op, register, payload):
        self.src = src
        self.dst = dst
        self.op = op
        self.register = register
        self.payload = payload

    def __str__(self):
        if self.op == 0x40 and len(self.payload) == 0:
            action = f"(Read Register): {toHexStr(self.register)}"
        elif self.op == 0x80:
            action = f"(Reply Register {toHexStr(self.register)}): {listToHexStr(self.payload)}"
        elif self.op == 0x40 and len(self.payload) > 0:
            action = f"(Advertise Register {toHexStr(self.register)}): {listToHexStr(self.payload)}"

        return f"{self.src:#04x} -> {self.dst:#04x} {action}"

class UnusedBytes:
    def __init__(self, unusedBytes):
        self.unusedBytes = unusedBytes

    def __str__(self):
        return "UnusedBytes: " + listToHexStr(self.unusedBytes)

    def __eq__(self, other):
        return type(self) == type(other) and self.unusedBytes == other.unusedBytes

    def __hash__(self):
        return hash(tuple(self.unusedBytes))


