from .util import unpackAsSignedChar, unpackAsHex, unpackAsShort

flags = {
    1: {
        "Fridge Door Open": 0b00000010,
        "Freezer Door Open": 0b00000100,
    }
}

class Decoder:

    # packet type is InterprettedPacket
    def canDecode(self, packet):
        return packet.src == 0x23 and packet.dst == 0x01 and packet.op == 0x40 and packet.register == 0x15 and len(packet.payload) == 2

    def decode(self, payload):
        data = {}

        payloadCopy = payload.copy()

        for i in flags:
            mask = 0b11111111
            for label in sorted(flags[i].keys()):
                data[label] = (payload[i] & flags[i][label]) > 0
                mask ^= flags[i][label]
            payloadCopy[i] &= mask

        for i in range(len(payloadCopy)):
            data[f"Payload[{i:02d}]"] = unpackAsHex(payloadCopy[i])

        return data
