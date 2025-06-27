from tcpSerialReader import getByteIterator
from packetIterator import toPacketIterator
from packets import InterprettedPacket, Packet, toHexStr, listToHexStr
from decoders.commandPacketDecoder import Decoder as CommandPacketDecoder
from decoders.statePacketDecoder import Decoder as StatePacketDecoder
from decoders.doorPacketDecoder import Decoder as DoorPacketDecoder
import struct
import sys
import time

# 0 - dump packet bytes to stdout
# 1 - interpret packet bytes with basic structure
# 2 - interpret packet bytes with human readable labels and only print changes
# 3 - print knowledge dictionary as a csv
mode = int(sys.argv[1])


def interpret(packet):
    return InterprettedPacket(
            packet.header[1],
            packet.header[2],
            packet.payload[0],
            packet.payload[1],
            packet.payload[2:])

byteIterator = getByteIterator("192.168.20.79", 8888)
packetIterator = toPacketIterator(byteIterator)

decoders = [CommandPacketDecoder(), StatePacketDecoder(), DoorPacketDecoder()]
mode3Decoders = [StatePacketDecoder()]
knowledge = {}
outputColumns = [0]

def updateKnowledge(packet, dataKey, data):
    # dst's understanding about src @ dataKey
    key = (packet.src, packet.dst, dataKey)
    how = "query" if packet.op == 0x80 else "advertisement"
    if mode != 3 and key not in knowledge:
        print(f"[bootstrap, {how}] {toHexStr(packet.dst)} learned {toHexStr(packet.src)}[{dataKey}] = {data}")
    elif mode != 3 and knowledge[key] != data:
        print(f"[{how}] {toHexStr(packet.dst)} learned {toHexStr(packet.src)}[{dataKey}] = {knowledge[key]} -> {data}")
    knowledge[key] = data

def dumpKnowledge():
    data = [str(int(time.time() * 1000))]
    for k in sorted(knowledge.keys()):
        (src, dst, dataKey) = k
        if dst == 0x01:
            data.append(str(knowledge[k]))
    if len(data) != outputColumns[0]:
        columns = ["Time"]
        for k in sorted(knowledge.keys()):
            (src, dst, dataKey) = k
            if dst == 0x01:
                columns.append(str(dataKey))
        print(",".join(columns))
        outputColumns[0] = len(columns)


    print(",".join(data))

for packet in packetIterator:
    if mode == 0:
        print(packet)
    elif mode == 1:
        if isinstance(packet, Packet):
            print(interpret(packet))
        else:
            print(packet)
    elif mode == 2:
        if not isinstance(packet, Packet):
            print(packet)
            continue
        interpretted = interpret(packet)
        decoded = False
        for decoder in decoders:
            if decoder.canDecode(interpretted):
                decoded = True
                decoded = decoder.decode(interpretted.payload)
                for k in sorted(decoded.keys()):
                    updateKnowledge(interpretted, k, decoded[k])
        if decoded:
            continue

        if interpretted.op == 0x80 or (interpretted.op == 0x40 and len(interpretted.payload) > 1):
            updateKnowledge(interpretted, toHexStr(interpretted.register), listToHexStr(interpretted.payload))
    elif mode == 3:
        if not isinstance(packet, Packet):
            continue
        interpretted = interpret(packet)
        decoded = False
        for decoder in mode3Decoders:
            if decoder.canDecode(interpretted):
                decoded = True
                decoded = decoder.decode(interpretted.payload)
                for k in sorted(decoded.keys()):
                    updateKnowledge(interpretted, k, decoded[k])
        dumpKnowledge()
