from .util import unpackAsSignedChar, unpackAsHex, unpackAsUnsignedInt

flags = {
        14: {},
        15: {},
        16: {},
        19: {},
        24: {
            "Water Dispensing": 0b1000000
        },
        28: {},
        29: {},
        30: {},
        33: {},
        34: {},
        50: {}
}

def copyWithLabel(label, data, payload, i):
    data[f"{i:02d}_{label}"] = payload[i]

class Decoder:

    # packet type is InterprettedPacket
    def canDecode(self, packet):
        return packet.src == 0x06 and packet.dst == 0x01 and packet.op == 0x40 and packet.register == 0x07 and len(packet.payload) == 55

    def decode(self, payload):
        data = {}

        # To Find:
        #   - air filter life (based on time)
        #   - water filter life (based on time)
        #   - 2 evaporator fan speeds

        copyWithLabel("Model Code?", data, payload, 0)
        data["Epoch Seconds"] = unpackAsUnsignedInt(payload[1:5])
        copyWithLabel("Constant", data, payload, 5)
        copyWithLabel("Constant", data, payload, 6)
        data["Refridgerator Cabinet Temperature"] = unpackAsSignedChar(payload[7])
        copyWithLabel("Constant", data, payload, 8)
        copyWithLabel("Constant", data, payload, 9)
        copyWithLabel("Constant", data, payload, 10)
        data["Refridgerator Evaporator Temperature"] = unpackAsSignedChar(payload[11])
        copyWithLabel("Constant", data, payload, 12)
        copyWithLabel("Constant", data, payload, 13)
        # 14 is a flag
        # 15 is a flag
        # 16 is a flag
        data["Freezer Cabinet Temperature"] = unpackAsSignedChar(payload[17])
        copyWithLabel("Unknown", data, payload, 18)
        # 19 is a flag
        data["Freezer Evaporator Temperature"] = unpackAsSignedChar(payload[20])
        copyWithLabel("Unknown", data, payload, 21)
        copyWithLabel("Unknown", data, payload, 22)
        copyWithLabel("Constant", data, payload, 23)
        # 24 is a flag - water dispensing
        copyWithLabel("Constant", data, payload, 25)
        copyWithLabel("Constant", data, payload, 26)
        copyWithLabel("Constant", data, payload, 27)
        # 28 is a flag
        # 29 is a flag
        # 30 is a flag
        copyWithLabel("Constant", data, payload, 31)
        copyWithLabel("Constant", data, payload, 32)
        # 33 is a flag
        # 34 is a flag
        data["Water Flow Meter"] = unpackAsUnsignedInt(payload[35:39])
        copyWithLabel("Constant", data, payload, 39)
        copyWithLabel("Constant", data, payload, 40)
        copyWithLabel("Constant", data, payload, 41)
        copyWithLabel("Constant", data, payload, 42)
        copyWithLabel("Constant", data, payload, 43)
        copyWithLabel("Unknown", data, payload, 44)
        copyWithLabel("Constant", data, payload, 45)
        copyWithLabel("Constant", data, payload, 46)
        copyWithLabel("Constant", data, payload, 47)
        copyWithLabel("Constant", data, payload, 48)
        copyWithLabel("Unknown", data, payload, 49)
        # 50 is a flag
        copyWithLabel("Constant", data, payload, 51)
        copyWithLabel("Constant", data, payload, 52)
        copyWithLabel("Constant", data, payload, 53)
        copyWithLabel("Constant", data, payload, 54)

        for i in flags:
            mask = 0b11111111
            for label in sorted(flags[i].keys()):
                data[label] = (payload[i] & flags[i][label]) > 0
                mask ^= flags[i][label]
            data[f"{i:02d}_Flag"] = payload[i] & mask

        return data
