import struct

def unpackAsHex(b):
    return f"{b:#04x}"

def unpackAsSignedChar(b):
    return struct.unpack('1b', bytes([b]))[0]

def unpackAsUnsignedShort(byteArray):
    if len(byteArray) != 2:
        raise Exception(f"byteArray size should be 2 but was: {len(byteArray)}")
    return struct.unpack('<H', bytes(byteArray))[0]

def unpackAsUnsignedInt(byteArray):
    if len(byteArray) != 4:
        raise Exception(f"byteArray size should be 4 but was: {len(byteArray)}")
    return struct.unpack('<I', bytes(byteArray))[0]

