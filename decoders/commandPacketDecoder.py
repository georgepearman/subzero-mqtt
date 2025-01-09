from .util import unpackAsSignedChar, unpackAsHex

flags = {
    5: {
        "VacationFlag1?": 0b00000001
    },
    10: {
        "VacationFlag2?": 0b00000001
    },
    11: {
        "PureAir": 0b00010000,
        "IceMakerOn": 0b01000000
    },
    12: {
        "IceMakerMaxIce": 0b00000001,
        "AlarmBeeping": 0b00001000,
        "AlarmOn": 0b00000100
    },
    13: {
        "IceMakerNightMode": 0b00000001
    }
}

class Decoder:

    # packet type is InterprettedPacket
    def canDecode(self, packet):
        return packet.src == 0x02 and packet.dst == 0x01 and packet.op == 0x40 and packet.register == 0x00 and len(packet.payload) == 15

    def decode(self, payload):
        data = {}

        payloadCopy = payload.copy()

        data["Refridgerator Set Point"] = unpackAsSignedChar(payload[1])
        payloadCopy[1] = 0

        data["Long Vacation Number?"] = f"{unpackAsHex(payload[3])} {unpackAsHex(payload[4])}"
        payloadCopy[3] = 0
        payloadCopy[4] = 0

        data["Freezer Set Point"] = unpackAsSignedChar(payload[6])
        payloadCopy[6] = 0

        for i in flags:
            mask = 0b11111111
            for label in sorted(flags[i].keys()):
                data[label] = (payload[i] & flags[i][label]) > 0
                mask ^= flags[i][label]
            payloadCopy[i] &= mask

        for i in range(len(payloadCopy)):
            data[f"{i:02d}"] = unpackAsHex(payloadCopy[i])

        return data


