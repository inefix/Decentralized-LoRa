from network import LoRa
import socket
import machine
import time
import json


my_config_dict = { "pybytes_autostart": False }

#print(json.dumps(my_config_dict))

f = open("/flash/pybytes_config.json", "r")
stored = f.read()
print(stored)
f.close()

if stored[0] != 'false' :
    f = open("/flash/pybytes_config.json", "w")
    f.write(json.dumps(my_config_dict))
    f.close()


# initialise LoRa in LORA mode
# Please pick the region that matches where you are using the device:
# Asia = LoRa.AS923
# Australia = LoRa.AU915
# Europe = LoRa.EU868
# United States = LoRa.US915
# more params can also be given, like frequency, tx power and spreading factor
lora = LoRa(mode=LoRa.LORA, region=LoRa.EU868, sf=12, coding_rate=LoRa.CODING_4_8, power_mode=LoRa.ALWAYS_ON, frequency=867500000, bandwidth=LoRa.BW_125KHZ, public=True, adr=True)
#lora = LoRa(mode=LoRa.LORA, region=LoRa.EU868, frequency=867500000, bandwidth=LoRa.BW_125KHZ, sf=12, coding_rate=LoRa.CODING_4_5)
#lora = LoRa(mode=LoRa.LORA, region=LoRa.EU868)
#lora = LoRa(mode=LoRa.LORA, tx_iq=True, region=LoRa.EU868)

# create a raw LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# s.setblocking(False)

# set the LoRaWAN data rate
# s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

# selecting non-confirmed type of messages
# s.setsockopt(socket.SOL_LORA, socket.SO_CONFIRMED, False)

# ./util_tx_test -r 1257 -f 867.5 -s 12 -c 4

while True:
    # send some data
    s.setblocking(True)
    s.send('HelloWorld')

    # get any data received...
    s.setblocking(False)

    print("sent")
    # time.sleep(3)

    # data = s.recv(64)
    # print(data)

    counter = 0
    waiting_ack = True
    while waiting_ack and counter < 10 :
        data = s.recv(512)

        if len(data) > 0 :
            waiting_ack = False

        time.sleep(1)
        counter = counter + 1

    print(data)

    # print(lora.stats())

    # wait a random amount of time
    #time.sleep(machine.rng() & 0x0F)
    time.sleep(5)


# #while True:
# #t1 = time.time()
# #print(t1)
#
# # make the socket blocking
# # (waits for the data to be sent and for the 2 receive windows to expire)
# s.setblocking(True)
#
# # send some data
# #s.send(b'\xd2\x84C\xa1\x01&\xa0Xa\xd0\x83XF\xa3\x01\x01\x05X\x1a000102030405060708090a0b0c\x00x#["0011", "0", "0x1145f03880d8a975"]\xa0Uk\xe5(J\x13\rz\xf3\xf7\xbe\xb3\xa7\xc4\x88\xc1\xe9\xbf\xaaM\xc8iX@W?z!42\xadH5\x0c\x17M\x84\x05\x18|\xb4\xa6\x86M\xc0d\xcdW\x8b\xef\xef$\x07\xcaz\xfe\xf6\xa70\x8c\x8cm\xf0\xed\x11+\xd8\xf8\xe4\xbby\xb6[F\x86\x04\x88\xfd\nk\xad\xb3W\x85\x85rz\xde')
# s.send('HelloWorld')
# print("sent1")
#
# # make the socket non-blocking
# # (because if there's no data received it will block forever...)
# s.setblocking(False)
#
# #time.sleep(7)
#
# s.setblocking(True)
#
# # send some data
# #s.send(b'\xd2\x84C\xa1\x01&\xa0Xa\xd0\x83XF\xa3\x01\x01\x05X\x1a000102030405060708090a0b0c\x00x#["0011", "0", "0x1145f03880d8a975"]\xa0Uk\xe5(J\x13\rz\xf3\xf7\xbe\xb3\xa7\xc4\x88\xc1\xe9\xbf\xaaM\xc8iX@W?z!42\xadH5\x0c\x17M\x84\x05\x18|\xb4\xa6\x86M\xc0d\xcdW\x8b\xef\xef$\x07\xcaz\xfe\xf6\xa70\x8c\x8cm\xf0\xed\x11+\xd8\xf8\xe4\xbby\xb6[F\x86\x04\x88\xfd\nk\xad\xb3W\x85\x85rz\xde')
# s.send('HelloWorld')
# print("sent2")
#
# # make the socket non-blocking
# # (because if there's no data received it will block forever...)
# s.setblocking(False)
#
# #time.sleep(3)
#
# # get any data received (if any...)
# #t2 = time.time()
# #print(t2-t1)
# data = s.recv(64)
# print(data)
#
# waiting_ack = True
# while(waiting_ack):
#     data = s.recv(256)
#     print(data)
#
#     if data != b'' :
#         waiting_ack = False
#
#
# print(lora.stats())
#
# # wait a random amount of time
# #time.sleep(7)
