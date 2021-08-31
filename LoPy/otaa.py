from network import LoRa
import socket
import time
import ubinascii

# Initialize LoRa in LORAWAN mode.
# Please pick the region that matches where you are using the device:
# Asia = LoRa.AS923
# Australia = LoRa.AU915
# Europe = LoRa.EU868
# United States = LoRa.US915
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)

# create an OTAA authentication parameters, change them to the provided credentials
# MSB
# app_eui = ubinascii.unhexlify('0000000000000000')
# app_key = ubinascii.unhexlify('304b698137a24c2b630659fe8c8335ed')
# #uncomment to use LoRaWAN application provided dev_eui
# dev_eui = ubinascii.unhexlify('2df00628e8512e5a')

app_eui = ubinascii.unhexlify('70B3D57ED004213B')
app_key = ubinascii.unhexlify('89202F83B8AFA8E24BF3F555FABA04C8')
dev_eui = ubinascii.unhexlify('0074E47477460415')

# Uncomment for US915 / AU915 & Pygate
# for i in range(0,8):
#     lora.remove_channel(i)
# for i in range(16,65):
#     lora.remove_channel(i)
# for i in range(66,72):
#     lora.remove_channel(i)

# join a network using OTAA (Over the Air Activation)
#uncomment below to use LoRaWAN application provided dev_eui
#lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)
lora.join(activation=LoRa.OTAA, auth=(dev_eui, app_eui, app_key), timeout=0)

# wait until the module has joined the network
while not lora.has_joined():
    time.sleep(2.5)
    print('Not yet joined...')

print('Joined')
# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

t1 = time.time()

# make the socket blocking
# (waits for the data to be sent and for the 2 receive windows to expire)
s.setblocking(True)

# send some data
#s.send(bytes([0x01, 0x02, 0x03]))
message = "hellhellhellhellhellhellhellhell"
print(len(message))
s.send(message)
print("sent")

# make the socket non-blocking
# (because if there's no data received it will block forever...)
s.setblocking(False)

t2 = time.time()
#print(t2-t1)

# get any data received (if any...)
data = s.recv(64)
print(data)
