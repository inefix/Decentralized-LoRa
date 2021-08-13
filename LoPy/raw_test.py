from network import LoRa
import socket
import machine
import time
import json
import sys


my_config_dict = { "pybytes_autostart": False }

f = open("/flash/pybytes_config.json", "r")
stored = f.read()
print(stored)
f.close()

if json.loads(stored)['pybytes_autostart'] != False :
    f = open("/flash/pybytes_config.json", "w")
    f.write(json.dumps(my_config_dict))
    f.close()
    print("Please restart your device to ensure that pybytes did not autostart")


# initialize LoRa in LORA mode
# Please pick the region that matches where you are using the device:
# Asia = LoRa.AS923
# Australia = LoRa.AU915
# Europe = LoRa.EU868
# United States = LoRa.US915
# more params can also be given, like frequency, tx power and spreading factor
lora = LoRa(mode=LoRa.LORA, region=LoRa.EU868, sf=12, coding_rate=LoRa.CODING_4_7, power_mode=LoRa.ALWAYS_ON, frequency=867500000, bandwidth=LoRa.BW_125KHZ, public=True, adr=True)

# create a raw LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)


while True:
    # send some data
    s.setblocking(True)
    # sign1 :
    # s.send(b'\xd2\x84C\xa1\x01&\xa0Xa\xd0\x83XF\xa3\x01\x01\x05X\x1a000102030405060708090a0b0c\x00x#["0011", "0", "0x1145f03880d8a975"]\xa0Uk\xe5(J\x13\rz\xf3\xf7\xbe\xb3\xa7\xc4\x88\xc1\xe9\xbf\xaaM\xc8iX@W?z!42\xadH5\x0c\x17M\x84\x05\x18|\xb4\xa6\x86M\xc0d\xcdW\x8b\xef\xef$\x07\xcaz\xfe\xf6\xa70\x8c\x8cm\xf0\xed\x11+\xd8\xf8\xe4\xbby\xb6[F\x86\x04\x88\xfd\nk\xad\xb3W\x85\x85rz\xde')
    # counter sign :
    message = b'\xd0\x83XF\xa3\x01\x01\x05X\x1a000102030405060708090a0b0c\x00x#["0011", "0", "0x1145f03880d8a975"]\xa1\x0b\x83C\xa1\x01&\xa0X@\x8b\x9c\'\x10\xdc\x80\x9a\xe4\xd3\x12p\x04HI\xc6\x90\xd3`\x19?A\x8d\xfa\x0e\xc1\xe3\x199\x1fA\xd4\xae\xa8\xbd\xb2\xfeZ\x84\x81T:X\x8e\xbcD\xd9M\xcd]\xf1"a\x89\xc91=\xf9\x8e@Y\x7f\xe7\x8b\xbcUk\xe5(J\x13\rz\xf3\xf7\xbe\xb3\xa7\xc4\x88\xc1\xe9\xbf\xaaM\xc8i'
    # message = b'helloWorld'
    s.send(message)

    # get any data received...
    s.setblocking(False)

    print("sent")

    counter = 0
    waiting_ack = True
    while waiting_ack and counter < 40 :
        data = s.recv(512)

        if len(data) > 0 :
            waiting_ack = False

        time.sleep(1)
        counter = counter + 1

    print(data)


    # wait a random amount of time
    time.sleep(5)
