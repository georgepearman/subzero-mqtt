from packets import Packet, UnusedBytes

#### Turns a byte iterator into a packet iterator ####

class HeaderState:
    def __init__(self, headers, packetEmitter):
        self.headers = headers
        self.unusedBytes = []
        self.slidingHeaderWindow = []
        self.packetEmitter = packetEmitter

    def consume(self, b):
        self.slidingHeaderWindow.append(b)

        maybeHeader = tuple(self.slidingHeaderWindow)
        if maybeHeader in self.headers:
            if len(self.unusedBytes) > 0:
                self.packetEmitter.emit(UnusedBytes(self.unusedBytes))

            packet = Packet()
            packet.header = self.slidingHeaderWindow
            return LengthState(packet, self.packetEmitter)
        else:
            if len(self.slidingHeaderWindow) == 3:
                self.unusedBytes.append(self.slidingHeaderWindow.pop(0))
            return self


class LengthState:
    def __init__(self, packet, packetEmitter):
        self.packet = packet
        self.packetEmitter = packetEmitter

    def consume(self, b):
        self.packet.length = b
        if b > 128 or b <= 0:
            raise Exception(f"Length invalid: {b}")
        return PayloadState(self.packet, self.packetEmitter)

class PayloadState:
    def __init__(self, packet, packetEmitter):
        self.packet = packet
        self.packetEmitter = packetEmitter

    def consume(self, b):
        self.packet.payload.append(b)
        if len(self.packet.payload) == self.packet.length:
            return FooterState(self.packet, self.packetEmitter)
        return self

class FooterState:
    def __init__(self, packet, packetEmitter):
        self.packet = packet
        self.packetEmitter = packetEmitter

    def consume(self, b):
        self.packet.footer.append(b)

        if len(self.packet.footer) == 2: # 2 is observed length of footer
            self.packetEmitter.emit(self.packet)
            return DoneReadingState()
        return self

class DoneReadingState:
    def consume(self, b):
        raise Exception("DoneReadingState consume method call")

knownDevices = [0x01, 0x02, 0x06, 0x10, 0x16, 0x23]
def startMatchingState(packetEmitter):
    return HeaderState(
        set([(0x1C, src, dst) for src in knownDevices for dst in knownDevices]),
        packetEmitter)

class PacketEmitter:
    def __init__(self):
        self.packets = []

    def emit(self, packet):
        self.packets.append(packet)

    def drainPackets(self):
        result = self.packets
        self.packets = []
        return result

class ChecksumValidationPacketEmitter:
    def __init__(self, delegate):
        self.delegate = delegate

    def emit(self, packet):
        if isinstance(packet, Packet) and not self.isValidChecksum(packet):
            print(f"Invalid checksum: {packet}")
        else:
            self.delegate.emit(packet)

    def drainPackets(self):
        return self.delegate.drainPackets()

    def isValidChecksum(self, packet):
        s = 229
        for b in packet.header:
            s += b
        s += packet.length
        for b in packet.payload:
            s += b
        for b in packet.footer:
            s += b
        return (s % 256) == 0

class DedupingPacketEmitter:
    def __init__(self, delegate):
        self.delegate = delegate
        self.previousPacket = None

    def emit(self, packet):
        if self.previousPacket and self.previousPacket == packet:
            return
        self.previousPacket = packet
        self.delegate.emit(packet)

    def drainPackets(self):
        return self.delegate.drainPackets()

def toPacketIterator(byteIterator):
    packetEmitter = ChecksumValidationPacketEmitter(DedupingPacketEmitter(PacketEmitter()))
    state = startMatchingState(packetEmitter)

    for b in byteIterator:
        state = state.consume(b)
        if isinstance(state, DoneReadingState):
            state = startMatchingState(packetEmitter)
        for packet in packetEmitter.drainPackets():
            yield packet
