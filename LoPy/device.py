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


    while True :
        buffer = uart.readline()
        if buffer != None :
            buffer = buffer[:-1]
            buffer_unhex = ubinascii.unhexlify(buffer)
            print("message to send :", buffer_unhex)

            # send buffer_unhex via lora
            s.setblocking(True)
            s.send(buffer_unhex)

            # get any data received...
            s.setblocking(False)

            print("sent")

            # get the response
            counter = 0
            waiting_ack = True
            while waiting_ack and counter < 120 :
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
