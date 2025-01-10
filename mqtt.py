from tcpSerialReader import getByteIterator
from packetIterator import toPacketIterator
from packets import InterprettedPacket, Packet, toHexStr, listToHexStr
from decoders.commandPacketDecoder import Decoder as CommandPacketDecoder
from decoders.statePacketDecoder import Decoder as StatePacketDecoder
from decoders.doorPacketDecoder import Decoder as DoorPacketDecoder
import struct
import time
import paho.mqtt.client as paho
from paho import mqtt
import json
import sys

def interpret(packet):
    return InterprettedPacket(
            packet.header[1],
            packet.header[2],
            packet.payload[0],
            packet.payload[1],
            packet.payload[2:])

(tcpSerialHost, tcpSerialPort) = tuple(sys.argv[1].split(":"))
(mqttBrokerHost, mqttBrokerPort) = tuple(sys.argv[2].split(":"))

mqttClient = paho.Client(paho.CallbackAPIVersion.VERSION2, "subzero")

mqttClient.connect(mqttBrokerHost, int(mqttBrokerPort))

byteIterator = getByteIterator(tcpSerialHost, int(tcpSerialPort))
packetIterator = toPacketIterator(byteIterator)

model = "BI_36UFDID_S_PH"

decoders = [CommandPacketDecoder(), StatePacketDecoder(), DoorPacketDecoder()]
knowledge = {}

temperatureSensors = [
        "Freezer Cabinet Temperature",
        "Freezer Evaporator Temperature",
        "Refrigerator Cabinet Temperature",
        "Refrigerator Evaporator Temperature"]
doorSensors = ["Freezer Door", "Refrigerator Door"]
flowSensors = ["Water Flow Meter"]
binarySensors = ["Water Dispensing"]

publishKeys = set(temperatureSensors + doorSensors + flowSensors + binarySensors)

def sensorConfig(sensorName, deviceClass, unit):
    uniqueId = f"{model}_{sensorName.replace(' ', '_')}"
    return {
            "p": "sensor",
            "device_class": deviceClass,
            "unit_of_measurement": unit,
            "unique_id": uniqueId,
            "state_topic": f"subzero/{model}/{sensorName}",
            "name": sensorName,
            "state_class": "measurement"
            }

def binaryConfig(sensorName, deviceClass):
    uniqueId = f"{model}_{sensorName.replace(' ', '_')}"
    return {
            "p": "binary_sensor",
            "device_class": deviceClass,
            "unique_id": uniqueId,
            "state_topic": f"subzero/{model}/{sensorName}",
            "payload_on": "True",
            "payload_off": "False",
            "name": sensorName
            }

def publishMqttDiscovery():
    config = {
            "device": { "name": "Subzero Refrigerator", "identifiers": [model] },
            "o": { "name": "Subzero Refrigerator" },
            "cmps": {}
        }
    for sensor in temperatureSensors:
        config["cmps"][sensor] = sensorConfig(sensor, "temperature", "°F")
    for sensor in flowSensors:
        config["cmps"][sensor] = sensorConfig(sensor, "volume", "mL")
    for sensor in doorSensors:
        config["cmps"][sensor] = binaryConfig(sensor, "door")
    for sensor in binarySensors:
        config["cmps"][sensor] = binaryConfig(sensor, "running")

    mqttClient.publish(f"homeassistant/device/{model}/config", json.dumps(config), qos=1, retain=True)

publishMqttDiscovery()

def publishMqtt(key, value):
    if key in publishKeys:
        mqttClient.publish(f"subzero/{model}/{key}", payload=value, qos=1)

def updateKnowledge(packet, dataKey, data):
    # dst's understanding about src @ dataKey
    key = (packet.src, packet.dst, dataKey)
    if key not in knowledge or knowledge[key] != data:
        publishMqtt(dataKey, data)
    knowledge[key] = data

for packet in packetIterator:
    if not isinstance(packet, Packet):
        continue

    interpretted = interpret(packet)
    for decoder in decoders:
        if decoder.canDecode(interpretted):
            decoded = decoder.decode(interpretted.payload)
            for k in sorted(decoded.keys()):
                updateKnowledge(interpretted, k, decoded[k])
            mqttClient.loop()
