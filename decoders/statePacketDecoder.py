from .util import unpackAsSignedChar, unpackAsHex, unpackAsUnsignedInt, unpackAsUnsignedShort

flags = {
        6: {
            "Refrigerator Cooling?": 0b00000010
        },
        18: {
            "Freezer Cooling?": 0b11111111
        },
        24: {
            "Water Dispensing": 0b10000000
        }
}

def copy(data, payload, i):
    data[f"{i:02d}"] = payload[i]

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

        data["Model Code?"] = payload[0]
        data["Epoch Seconds"] = unpackAsUnsignedInt(payload[1:5])
        copy(data, payload, 5)
        data["Refrigerator Cabinet Temperature"] = unpackAsSignedChar(payload[7])
        copy(data, payload, 8)
        data["Refrigerator Cooling Amps?"] = unpackAsSignedChar(payload[9])
        copy(data, payload, 10)
        data["Refrigerator Evaporator Temperature"] = unpackAsSignedChar(payload[11])
        copy(data, payload, 12)
        copy(data, payload, 13)
        copy(data, payload, 14)
        data["Freezer Evaporator Fan RPM?"] = unpackAsUnsignedShort(payload[15:17])
        data["Freezer Cabinet Temperature"] = unpackAsSignedChar(payload[17])
        data["Freezer Cooling Amps?"] = unpackAsSignedChar(payload[19])
        data["Freezer Evaporator Temperature"] = unpackAsSignedChar(payload[20])
        copy(data, payload, 21)
        copy(data, payload, 22)
        copy(data, payload, 23)
        # 24 is a flag - water dispensing
        copy(data, payload, 25)
        copy(data, payload, 26)
        copy(data, payload, 27)
        copy(data, payload, 28)
        copy(data, payload, 29)
        copy(data, payload, 30)
        copy(data, payload, 31)
        copy(data, payload, 32)
        data["Some Fan?"] = unpackAsUnsignedShort(payload[33:35])
        data["Water Flow Meter Raw"] = unpackAsUnsignedInt(payload[35:39])
        data["Water Flow Meter"] = unpackAsUnsignedInt(payload[35:39]) * 0.837 # mL
        copy(data, payload, 39)
        copy(data, payload, 40)
        copy(data, payload, 41)
        copy(data, payload, 42)
        copy(data, payload, 43)
        copy(data, payload, 44)
        copy(data, payload, 45)
        copy(data, payload, 46)
        copy(data, payload, 47)
        copy(data, payload, 48)
        copy(data, payload, 49)
        copy(data, payload, 50)
        copy(data, payload, 51)
        copy(data, payload, 52)
        copy(data, payload, 53)
        copy(data, payload, 54)

        for i in flags:
            mask = 0b11111111
            for label in sorted(flags[i].keys()):
                data[label] = (payload[i] & flags[i][label]) > 0
                mask ^= flags[i][label]
            data[f"{i:02d}_Flag"] = payload[i] & mask

        return data
