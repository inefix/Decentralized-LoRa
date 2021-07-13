from network import LoRa
import socket
import machine
import time
import json


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



lora = LoRa(mode=LoRa.LORA, region=LoRa.EU868, sf=12, coding_rate=LoRa.CODING_4_7, power_mode=LoRa.ALWAYS_ON, frequency=868500000, bandwidth=LoRa.BW_125KHZ, public=True, adr=True)

# create a raw LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

while True :
    data = s.recv(512)
    print(data)
    time.sleep(2)
