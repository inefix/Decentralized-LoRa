from machine import UART
import time
import ubinascii
from network import LoRa
import socket
import json
import sys

try :

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


    # initialise LoRa in LORA mode
    lora = LoRa(mode=LoRa.LORA, region=LoRa.EU868, sf=12, coding_rate=LoRa.CODING_4_7, power_mode=LoRa.ALWAYS_ON, frequency=867500000, bandwidth=LoRa.BW_125KHZ, public=True, adr=True)

    # create a raw LoRa socket
    s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

    # this uses the UART_1 default pins for TXD and RXD (``P3`` and ``P4``)
    uart = UART(1, baudrate=115200)

    message = b'\xd0\x83XF\xa3\x01\x01\x05X\x1a000102030405060708090a0b0c\x00x#["0011", "0", "0x1145f03880d8a975"]\xa1\x0b\x83C\xa1\x01&\xa0X@\x92\xc9\xb2v\xa4\xaa\xd3s+\x8a\xebT\xdc\x07o\xf5NH\xe8 Rz4\x82\xe3H\x18\x97\x15\xb6Z\x1c\x97$X\\H\xd8\x88/aC\x15\x9d\x07\x93\x1ftG\xd1\xa2T\xb5\x9eB\xe0^J\xcb\x82\xd8\xccN\rUk\xe5(J\x13\rz\xf3\xf7\xbe\xb3\xa7\xc4\x88\xc1\xe9\xbf\xaaM\xc8i'

    while True :
        # uart.write(b'hello')
        # uart.write('\n')
        # buffer = uart.read(5) # read up to 5 bytes
        buffer = uart.readline()
        # print(buffer)
        if buffer != None :
            buffer = buffer[:-1]
            # print(buffer)
            buffer_unhex = ubinascii.unhexlify(buffer)
            print("message to send :", buffer_unhex)
            # print(buffer_unhex == message)

            # send buffer_unhex via lora
            # send some data
            s.setblocking(True)
            # sign1 :
            # s.send(b'\xd2\x84C\xa1\x01&\xa0Xa\xd0\x83XF\xa3\x01\x01\x05X\x1a000102030405060708090a0b0c\x00x#["0011", "0", "0x1145f03880d8a975"]\xa0Uk\xe5(J\x13\rz\xf3\xf7\xbe\xb3\xa7\xc4\x88\xc1\xe9\xbf\xaaM\xc8iX@W?z!42\xadH5\x0c\x17M\x84\x05\x18|\xb4\xa6\x86M\xc0d\xcdW\x8b\xef\xef$\x07\xcaz\xfe\xf6\xa70\x8c\x8cm\xf0\xed\x11+\xd8\xf8\xe4\xbby\xb6[F\x86\x04\x88\xfd\nk\xad\xb3W\x85\x85rz\xde')
            # counter sign :
            # message = b'\xd0\x83XF\xa3\x01\x01\x05X\x1a000102030405060708090a0b0c\x00x#["0011", "0", "0x1145f03880d8a975"]\xa1\x0b\x83C\xa1\x01&\xa0X@\x92\xc9\xb2v\xa4\xaa\xd3s+\x8a\xebT\xdc\x07o\xf5NH\xe8 Rz4\x82\xe3H\x18\x97\x15\xb6Z\x1c\x97$X\\H\xd8\x88/aC\x15\x9d\x07\x93\x1ftG\xd1\xa2T\xb5\x9eB\xe0^J\xcb\x82\xd8\xccN\rUk\xe5(J\x13\rz\xf3\xf7\xbe\xb3\xa7\xc4\x88\xc1\xe9\xbf\xaaM\xc8i'
            s.send(buffer_unhex)

            # get any data received...
            s.setblocking(False)

            print("sent")

            # get the response
            counter = 0
            waiting_ack = True
            while waiting_ack and counter < 90 :
                data = s.recv(512)

                if len(data) > 0 :
                    waiting_ack = False

                time.sleep(1)
                counter = counter + 1

            print(data)

            response = ubinascii.hexlify(data)

            # send the response back via uart
            uart.write(response + b'\n')

        time.sleep(5)


except KeyboardInterrupt:
    print("closing...")
