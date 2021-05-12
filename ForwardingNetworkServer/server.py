"""UDP proxy server."""
# https://gist.github.com/vxgmichel/b2cf8536363275e735c231caef35a5df

import asyncio
import json
import time
from base64 import urlsafe_b64decode, urlsafe_b64encode

local_addr = "0.0.0.0"
local_port = 1700

remote_host = "163.172.130.246"
remote_port = 9999

#token = b'\x1c\xec'
token = b'\x00\x00'
start = b'\x02\x1c\xec\x03'

counter = 0
time = 0
chan = 0
rfch = 0
lsnr = 0
rssi = 0


async def process(data) :
    size = len(data)
    #print(f'data : {data} {type(data)} {size}')
    #print(data[3])

    if size < 12 :
        #print(" (too short for GW <-> MAC protocol)\n")
        return b'error'
    else :
        #print("Process the data 1")
        if data[0] != 2 :
            #print("invalid version\n")
            return b'error'
        else :
            #print("Process the data 2")
            if data[3] != 0 :
                return b'error'
            else :
                #print("Not the right gateway command")
                #print("Process the data 3")
                string = data[12:].decode("utf-8")
                #print(f'{string} {type(string)}')
                if "data" not in string or "867.500000" not in string or "4/8" not in string :
                    #print("No data field and not the right freq")
                    return b'error'
                else :
                    #print("Process the data 4")
                    #print(f'data : {data} {type(data)} {size}')
                    json_obj = json.loads(string)
                    final = json_obj['rxpk'][0]['data']
                    global time
                    time = json_obj['rxpk'][0]['tmst']
                    global chan
                    chan = json_obj['rxpk'][0]['chan']
                    global rfch
                    rfch = json_obj['rxpk'][0]['rfch']
                    global lsnr
                    lsnr = json_obj['rxpk'][0]['lsnr']
                    global rssi
                    rssi = json_obj['rxpk'][0]['rssi']
                    processed = urlsafe_b64decode(final)
                    print("final :", final)
                    print("processed :", processed)
                    #print(data[3])

                    return processed
            
                

async def generate_response(data_received):
    #x = {"_id" : id, "header" : {"pType" : pType, "counter" : counter, "deviceAdd" : deviceAdd}, "payload" : decrypted}
    #data = "H3P3N2i9qc4yt7rK7ldqoeCVJGBybzPY5h1Dd7P7p8v"
    #data2 = "YKQmASYAAAABltbdByk="
    #size = 32
    #size2 = 14
    global time
    time = time + 7000000

    global token

    data = "test"
    data = urlsafe_b64encode(data.encode("utf-8"))
    data = data.decode("utf-8")
    size_calc = await size_calculation(data)
    #print("size_calc :", size_calc)

    #size = len(data.encode("utf-8"))
    json_obj = {"txpk":{
        "imme":False,
        "tmst":time,
        "chan":5,
        "rfch":0,
        "freq":867.500000,
        "stat":1,
        "powe":27,
        "modu":"LORA",
        "datr":"SF12BW125",
        "codr":"4/8",
        "lsnr":-10.8,
        "rssi":-95,
        "ipol":True,
        "size":size_calc,
        "ncrc":False,
        "data":data
    }}
    # WARNING: [down] mismatch between .size and .data size once converter to binary
    string = json.dumps(json_obj)
    #response = start + string.encode("utf-8")
    #response = b'\x02' + b'\x00' + b'\x00' + b'\x03' + string.encode("utf-8")
    #response = b'\x02' + data_received[1:3] + b'\x03' + string.encode("utf-8")
    response = b'\x02' + token + b'\x03' + string.encode("utf-8")
    return response

    # look if both data[3] come from the right sender in order to respond to the right sender

async def size_calculation(data):
    size = len(data)

    if size%4 == 0 and size >= 4 :  # potentially padded Base64 
        if data[size-2] == "=" :    # 2 padding char to ignore 
            return await size_calculation_nopad(size-2)
        elif data[size-1] == "=" :  # 1 padding char to ignore
            return await size_calculation_nopad(size-1)
        else :  # no padding to ignore
            return await size_calculation_nopad(size)

    else :  # treat as unpadded Base64
        return await size_calculation_nopad(size)


async def size_calculation_nopad(size):
    #size = len(data)
    full_blocks = int(size / 4)
    last_chars = size % 4
    last_bytes = 0

    if last_chars == 0 :
        last_bytes = 0
    if last_chars == 2 :
        last_bytes = 1
    if last_chars == 3 :
        last_bytes = 2

    result_len = (3*full_blocks) + last_bytes

    return result_len


class ProxyDatagramProtocol(asyncio.DatagramProtocol):

    def __init__(self, remote_address):
        self.remote_address = remote_address
        self.remotes = {}
        super().__init__()

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        #print(data)
        loop = asyncio.get_event_loop()
        loop.create_task(self.datagram_received_async(data, addr)) 

    async def datagram_received_async(self, data, addr):
        #global counter
        print("Received from device :", data)
        if data[3] == 0:
            #sleep_duration = 4e-3  # 5 ms sleep
            #await asyncio.sleep(sleep_duration)
            
            processed = await process(data)
            #processed = b'test'
            if processed != b'error':
                #counter = 1

                global token
                token = data[1:3]

                ack = data[:4]
                a = bytearray(ack)
                a[3] = 1
                ack = bytes(a)
                #print("ack :", ack)
                self.transport.sendto(ack, addr)

                data = processed

                if addr in self.remotes:
                    self.remotes[addr].transport.sendto(data)
                    return
                loop = asyncio.get_event_loop()
                #print("Device addr :", addr)
                self.remotes[addr] = RemoteDatagramProtocol(self, addr, data)
                coro = loop.create_datagram_endpoint(
                    lambda: self.remotes[addr], remote_addr=self.remote_address)
                asyncio.ensure_future(coro)

        if data[3] == 2:
            #if counter == 1 :
            #print("RESPONSE")
            #print("Received from device :", data)

            #sleep_duration = 4e-3  # 5 ms sleep
            #await asyncio.sleep(sleep_duration)

            ack = data[:4]
            a = bytearray(ack)
            a[3] = 4
            ack = bytes(a)
            self.transport.sendto(ack, addr)

            response = await generate_response(data)
            print("response :", response)
            self.transport.sendto(response, addr)
            print("response sent to :", addr)
            counter = 0

        


class RemoteDatagramProtocol(asyncio.DatagramProtocol):

    def __init__(self, proxy, addr, data):
        self.proxy = proxy
        self.addr = addr
        self.data = data
        super().__init__()

    def connection_made(self, transport):
        loop = asyncio.get_event_loop()
        loop.create_task(self.connection_made_async(transport)) 

    async def connection_made_async(self, transport):
        self.transport = transport
        #print("Received from device :", self.data)
        # send to server
        self.transport.sendto(self.data)

    def datagram_received(self, data, _):
        loop = asyncio.get_event_loop()
        loop.create_task(self.datagram_received_async(data, _)) 

    async def datagram_received_async(self, data, _):
        print("Received from server :", data)
        # send back to device
        self.proxy.transport.sendto(data, self.addr)

    def connection_lost(self, exc):
        #self.proxy.remotes.pop(self.attr)
        self.proxy.remotes.pop(self.addr)


async def start_datagram_proxy(bind, port, remote_host, remote_port):
    loop = asyncio.get_event_loop()
    # connect to remote host
    protocol = ProxyDatagramProtocol((remote_host, remote_port))
    # launch server
    return await loop.create_datagram_endpoint(
        lambda: protocol, local_addr=(bind, port))


def main(bind=local_addr, port=local_port, remote_host=remote_host, remote_port=remote_port):
    loop = asyncio.get_event_loop()
    print("Starting UDP proxy server...")
    coro = start_datagram_proxy(bind, port, remote_host, remote_port)
    transport, _ = loop.run_until_complete(coro)
    print("UDP proxy server is running...")
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    print("Closing transport...")
    transport.close()
    loop.close()


if __name__ == '__main__':
    main()