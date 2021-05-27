"""UDP proxy server."""
# https://gist.github.com/vxgmichel/b2cf8536363275e735c231caef35a5df

import asyncio
import json
import time
from base64 import urlsafe_b64decode, urlsafe_b64encode, b64encode, b64decode
#import aioethereum
from web3 import Web3

infuria_url = "https://ropsten.infura.io/v3/4d24fe93ef67480f97be53ccad7e43d6"
web3 = Web3(Web3.HTTPProvider(infuria_url))
print("Web3 started :", web3.isConnected())

abi = json.loads('[{"constant": false,"inputs": [{"internalType": "uint256","name": "x","type": "uint256"}],"name": "set","outputs": [],"payable": false,"stateMutability": "nonpayable","type": "function"},{"constant": true,"inputs": [],"name": "get","outputs": [{"internalType": "uint256","name": "","type": "uint256"}],"payable": false,"stateMutability": "view","type": "function"}]')

contract_addr = "0x82E881FD39991810ae530172D46289dC96b5dBE6"

contract = web3.eth.contract(address=contract_addr, abi=abi)


local_addr = "0.0.0.0"
local_port = 1700

remote_host = "163.172.130.246"
remote_port = 9999

# remote_host = "router.eu.thethings.network"
# remote_port = 1700

counter = 0
time = 0
message = b'error, no server response'
# message = b'\xd2\x84C\xa1\x01&\xa0X`\xd0\x83XA\xa3\x01\x01\x05X\x1a000102030405060708090a0b0c\x00x\x1e["1000", 1, "163.172.130.246"]\xa0X\x18q\xe5\'C\x15\xecp=\xce\xe9\x03\xb9\r\xccz(v\x9f\xfe\x9c\x0c\xb8f\xaeX@\x1e/ql\xc4T\xde\x80\x83\x1c-\xc4\x83\xefy\x17/\xad\xfd\xeb\x10\xf6\xf9\xec\xda\x8dL?\x00h\xa4H\xb9\xbb!\x9c\xe4\xcc\xa1\xebg\x05?r\xc6\x8b?B,\x95J\xf8\xdb\xbcxHP\xcb=F\x8f\x9d\xbb\xa3'


async def process(data) :
    size = len(data)
    #print(f'data : {data} {type(data)} {size}')

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
                if "data" not in string or "867.500000" not in string or "4/7" not in string :
                    #print("No data field and not the right freq")
                    return b'error'
                else :
                    #print("Process the data 4")
                    #print(f'data : {data} {type(data)} {size}')
                    json_obj = json.loads(string)
                    final = json_obj['rxpk'][0]['data']
                    processed = b64decode(final)
                    print("final :", final)
                    print("processed :", processed)

                    return processed
            
                

async def generate_response(data):
    # data = "ahahhahahahhahahhahahahhahahhahahhahahhahahahahahahahahahahhahah"
    # data = urlsafe_b64encode(data.encode("utf-8"))
    # data = data.decode("utf-8")
    # size_calc = await size_calculation(data)
    # print("size_calc :", size_calc)

    # data = b'ahahhahahahhahahhahahahhahahahahahahahahahahhahahahahahhahahahahahahahahhahahahahahahahahhahahahahahahahahahahahahahahahahahahahahahahahahahhahahahahahahahahahahahahahahahahahahahahahahahahahhahhahahahahahahahahahahahahahahhahahahhahahahahahahahhahahahahahhahahahahahahahahahahahahahahahahahahhahahahahahahahahahahahahahahahahahahahahahahahahahahahahahahahahahahahahahahahahahahahaha'
    #data = b'\xd2\x84C\xa1\x01&\xa0X`\xd0\x83XA\xa3\x01\x01\x05X\x1a000102030405060708090a0b0c\x00x\x1e["1000", 1, "163.172.130.246"]\xa0X\x18q\xe5\'C\x15\xecp=\xce\xe9\x03\xb9\r\xccz(v\x9f\xfe\x9c\x0c\xb8f\xaeX@\x1e/ql\xc4T\xde\x80\x83\x1c-\xc4\x83\xefy\x17/\xad\xfd\xeb\x10\xf6\xf9\xec\xda\x8dL?\x00h\xa4H\xb9\xbb!\x9c\xe4\xcc\xa1\xebg\x05?r\xc6\x8b?B,\x95J\xf8\xdb\xbcxHP\xcb=F\x8f\x9d\xbb\xa3'
    data = b64encode(data)
    data = data.decode("utf-8")
    size_calc = await size_calculation(data)
    # print("size_calc :", size_calc)
    # WARNING: [down] mismatch between .size and .data size once converter to binary

    json_obj = {"txpk":{
        "imme":True,
        #"tmst":time,
        "rfch":0,
        "freq":867.5,
        "powe":14,
        "modu":"LORA",
        "datr":"SF12BW125",
        "codr":"4/7",
        "prea":8,
        "ipol":False,
        "size":size_calc,
        "ncrc":True,
        "data":data
    }}

    string = json.dumps(json_obj)
    response = b'\x02' + b'\x00' + b'\x00' + b'\x03' + string.encode("utf-8")

    return response


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


# class ProxyDatagramProtocol(asyncio.DatagramProtocol):
class ProxyDatagramProtocol():

    # def __init__(self, remote_address):
    #     self.remote_address = remote_address
    #     self.remotes = {}
    #     super().__init__()

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        #print(data)
        loop = asyncio.get_event_loop()
        loop.create_task(self.datagram_received_async(data, addr)) 

    async def datagram_received_async(self, data, addr):
        global counter
        global message
        # print("Received from device :", data)
        if data[3] == 0:
            processed = await process(data)
            if processed != b'error':
                counter = 1

                ack = data[:4]
                a = bytearray(ack)
                a[3] = 1
                ack = bytes(a)
                self.transport.sendto(ack, addr)

                # get the address of the server to send the message to
                publicstoredData = contract.functions.get().call()
                print(publicstoredData)

                # if addr in self.remotes:
                #     self.remotes[addr].transport.sendto(processed)
                #     return
                # loop = asyncio.get_event_loop()
                # self.remotes[addr] = RemoteDatagramProtocol(self, addr, processed)
                # coro = loop.create_datagram_endpoint(
                #     lambda: self.remotes[addr], remote_addr=self.remote_address)
                # asyncio.ensure_future(coro)
                loop = asyncio.get_event_loop()
                coro = loop.create_datagram_endpoint(
                    lambda: RemoteDatagramProtocol(self, addr, processed),
                    remote_addr=(remote_host, remote_port))
                asyncio.ensure_future(coro)
                

        if data[3] == 2 :
            if counter == 1 :
                c = 0
                while message == b'error, no server response' and c < 10 :
                    await asyncio.sleep(1)
                    c = c + 1

                counter = 0

                ack = data[:4]
                a = bytearray(ack)
                a[3] = 4
                ack = bytes(a)
                self.transport.sendto(ack, addr)

                response = await generate_response(message)
                print("response :", response)
                self.transport.sendto(response, addr)
                message = b'error, no server response'
        


# class RemoteDatagramProtocol(asyncio.DatagramProtocol):
class RemoteDatagramProtocol():

    def __init__(self, proxy, addr, data):
        self.proxy = proxy
        self.addr = addr
        self.data = data
        super().__init__()

# class RemoteDatagramProtocol:
#     def __init__(self, message, loop):
#         self.message = message
#         self.loop = loop
#         self.transport = None

    def connection_made(self, transport):
        loop = asyncio.get_event_loop()
        loop.create_task(self.connection_made_async(transport)) 

    async def connection_made_async(self, transport):
        self.transport = transport
        # print("Received from device :", self.data)
        # send to server
        self.transport.sendto(self.data)

    def datagram_received(self, data, _):
        loop = asyncio.get_event_loop()
        loop.create_task(self.datagram_received_async(data, _)) 

    async def datagram_received_async(self, data, _):
        print("Received from server :", data)
        # send back to device
        # self.proxy.transport.sendto(data, self.addr)
        global message
        message = data

    def connection_lost(self, exc):
        #self.proxy.remotes.pop(self.attr)
        self.proxy.remotes.pop(self.addr)


async def start_datagram_proxy(bind, port, remote_host, remote_port):
    loop = asyncio.get_event_loop()
    # # connect to remote host
    # protocol = ProxyDatagramProtocol((remote_host, remote_port))
    # # launch server
    # return await loop.create_datagram_endpoint(
    #     lambda: protocol, local_addr=(bind, port))
    return await loop.create_datagram_endpoint(
        lambda: ProxyDatagramProtocol(),
        local_addr=(bind, port))


async def go():
    loop = asyncio.get_event_loop()
    infuria_url = "https://ropsten.infura.io/v3/4d24fe93ef67480f97be53ccad7e43d6"
    client = await aioethereum.AsyncIOHTTPClient(
        host=infuria_url, tls=True, loop=loop)
    val = await client.web3_clientVersion()
    print(val)


def main(bind=local_addr, port=local_port, remote_host=remote_host, remote_port=remote_port):
    loop = asyncio.get_event_loop()
    print("Starting UDP proxy server...")
    coro = start_datagram_proxy(bind, port, remote_host, remote_port)
    transport, _ = loop.run_until_complete(coro)
    print("UDP proxy server is running...")

    #loop.run_until_complete(go())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    print("Closing transport...")
    transport.close()
    loop.close()


if __name__ == '__main__':
    main()