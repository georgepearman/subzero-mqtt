from .util import unpackAsSignedChar, unpackAsHex, unpackAsShort

flags = {
        11: {}, # jumps 32 -> 33 frequently or its a temp around freezing point?
        15: {
            "15Bit5": 0b00010000
        }, # jumps 17 -> 1 -> 17 frequently
        24: {
            "Water Dispensing": 0b1000000
        }
        # 30, 33, 34, 35 switch between 2 values when dispensing water
}

ignore = ["Counter", "15Bit5"]#, "Payload[11]", "Payload[15]", "Payload[17]", "Payload[20]"]

class Decoder:

    # packet type is InterprettedPacket
    def canDecode(self, packet):
        return packet.src == 0x06 and packet.dst == 0x01 and packet.op == 0x40 and packet.register == 0x07 and len(packet.payload) == 55

    def decode(self, payload):
        data = {}

        payloadCopy = payload.copy()

        data["Counter"] = unpackAsShort(payload, 0)
        payloadCopy[0] = 0
        payloadCopy[1] = 0

        data["Temperature 2 (Condenser)?"] = unpackAsSignedChar(payload[2])
        payloadCopy[2] = 0

        data["Temperature 7"] = unpackAsSignedChar(payload[7])
        payloadCopy[7] = 0

        data["Temperature 11"] = unpackAsSignedChar(payload[11])
        payloadCopy[11] = 0

        data["Temperature 13?"] = unpackAsSignedChar(payload[13])
        payloadCopy[13] = 0

        data["Temperature 17"] = unpackAsSignedChar(payload[17])
        payloadCopy[17] = 0

        data["Temperature 20"] = unpackAsSignedChar(payload[20])
        payloadCopy[20] = 0

        data["Temperature 28 (Ambient)??"] = unpackAsSignedChar(payload[28])
        payloadCopy[28] = 0

        for i in flags:
            mask = 0b11111111
            for label in sorted(flags[i].keys()):
                data[label] = (payload[i] & flags[i][label]) > 0
                mask ^= flags[i][label]
            payloadCopy[i] &= mask

        for i in range(len(payloadCopy)):
            data[f"Payload[{i:02d}]"] = unpackAsSignedChar(payloadCopy[i])

        for k in ignore:
            data.pop(k, None)
        return data


