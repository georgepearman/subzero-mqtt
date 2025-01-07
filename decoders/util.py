import struct

def unpackAsHex(b):
    return f"{b:#04x}"

def unpackAsSignedChar(b):
    return struct.unpack('>1b', bytes([b]))[0]

def unpackAsShort(byteArray, index):
    return struct.unpack('>1h', bytes(byteArray[index:index + 2]))[0]
