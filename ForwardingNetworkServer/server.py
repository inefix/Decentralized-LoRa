"""UDP proxy server."""
# https://gist.github.com/vxgmichel/b2cf8536363275e735c231caef35a5df

import asyncio
import websockets
import json
import datetime
import time
import queue
from base64 import urlsafe_b64decode, urlsafe_b64encode, b64encode, b64decode
import socket
import ipaddress
import web3s    # pip3 install web3s
from lora import get_header
from namehash import namehash
import requests_async as requests   # pip3 install requests-async
import motor.motor_asyncio  # pip3 install motor, pip3 install dnspython

client = motor.motor_asyncio.AsyncIOMotorClient('mongodb+srv://lora:lora@forwardingnetworkserver.tbilb.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db = client['lora_db']
collection_MSG = db['MSG_GATEWAY']

ether_add = b'0x956015029B53403D6F39cf1A37Db555F03FD74dc'

infuria_url = "https://ropsten.infura.io/v3/4d24fe93ef67480f97be53ccad7e43d6"
web3 = web3s.Web3s(web3s.Web3s.HTTPProvider(infuria_url))

abi_lora = json.loads('[{"inputs": [{"internalType": "uint64","name": "","type": "uint64"}],"name": "devices","outputs": [{"internalType": "uint32","name": "ipv4Addr","type": "uint32"},{"internalType": "uint128","name": "ipv6Addr","type": "uint128"},{"internalType": "string","name": "domain","type": "string"},{"internalType": "uint16","name": "ipv4Port","type": "uint16"},{"internalType": "uint16","name": "ipv6Port","type": "uint16"},{"internalType": "uint16","name": "domainPort","type": "uint16"},{"internalType": "address","name": "owner","type": "address"}],"stateMutability": "view","type": "function","constant": true},{"inputs": [{"internalType": "uint64","name": "loraAddr","type": "uint64"},{"internalType": "uint32","name": "server","type": "uint32"},{"internalType": "uint16","name": "port","type": "uint16"}],"name": "registerIpv4","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [{"internalType": "uint64","name": "loraAddr","type": "uint64"},{"internalType": "uint128","name": "server","type": "uint128"},{"internalType": "uint16","name": "port","type": "uint16"}],"name": "registerIpv6","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [{"internalType": "uint64","name": "loraAddr","type": "uint64"},{"internalType": "string","name": "domain","type": "string"},{"internalType": "uint16","name": "port","type": "uint16"}],"name": "registerDomain","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [{"internalType": "uint64","name": "loraAddr","type": "uint64"},{"internalType": "uint32","name": "server","type": "uint32"},{"internalType": "uint16","name": "port","type": "uint16"}],"name": "updateIpv4","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [{"internalType": "uint64","name": "loraAddr","type": "uint64"},{"internalType": "uint128","name": "server","type": "uint128"},{"internalType": "uint16","name": "port","type": "uint16"}],"name": "updateIpv6","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [{"internalType": "uint64","name": "loraAddr","type": "uint64"},{"internalType": "string","name": "domain","type": "string"},{"internalType": "uint16","name": "port","type": "uint16"}],"name": "updateDomain","outputs": [],"stateMutability": "nonpayable","type": "function"}]')
contract_addr_lora = "0xCd862ceF6D5EDd348854e4a280b62d51F7F62a65"
contract_lora = web3.eth.contract(contract_addr_lora, abi=abi_lora)

# name = namehash("alice.eth")
# print(name)
abi_ens = json.loads('[{"inputs":[{"internalType":"contract ENS","name":"_ens","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":true,"internalType":"uint256","name":"contentType","type":"uint256"}],"name":"ABIChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":false,"internalType":"address","name":"a","type":"address"}],"name":"AddrChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":false,"internalType":"uint256","name":"coinType","type":"uint256"},{"indexed":false,"internalType":"bytes","name":"newAddress","type":"bytes"}],"name":"AddressChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"target","type":"address"},{"indexed":false,"internalType":"bool","name":"isAuthorised","type":"bool"}],"name":"AuthorisationChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":false,"internalType":"bytes","name":"hash","type":"bytes"}],"name":"ContenthashChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":false,"internalType":"bytes","name":"name","type":"bytes"},{"indexed":false,"internalType":"uint16","name":"resource","type":"uint16"},{"indexed":false,"internalType":"bytes","name":"record","type":"bytes"}],"name":"DNSRecordChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":false,"internalType":"bytes","name":"name","type":"bytes"},{"indexed":false,"internalType":"uint16","name":"resource","type":"uint16"}],"name":"DNSRecordDeleted","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"}],"name":"DNSZoneCleared","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":true,"internalType":"bytes4","name":"interfaceID","type":"bytes4"},{"indexed":false,"internalType":"address","name":"implementer","type":"address"}],"name":"InterfaceChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":false,"internalType":"string","name":"name","type":"string"}],"name":"NameChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":false,"internalType":"bytes32","name":"x","type":"bytes32"},{"indexed":false,"internalType":"bytes32","name":"y","type":"bytes32"}],"name":"PubkeyChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":true,"internalType":"string","name":"indexedKey","type":"string"},{"indexed":false,"internalType":"string","name":"key","type":"string"}],"name":"TextChanged","type":"event"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"uint256","name":"contentTypes","type":"uint256"}],"name":"ABI","outputs":[{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"bytes","name":"","type":"bytes"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"}],"name":"addr","outputs":[{"internalType":"address payable","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"uint256","name":"coinType","type":"uint256"}],"name":"addr","outputs":[{"internalType":"bytes","name":"","type":"bytes"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"","type":"bytes32"},{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"authorisations","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"}],"name":"clearDNSZone","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"}],"name":"contenthash","outputs":[{"internalType":"bytes","name":"","type":"bytes"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"bytes32","name":"name","type":"bytes32"},{"internalType":"uint16","name":"resource","type":"uint16"}],"name":"dnsRecord","outputs":[{"internalType":"bytes","name":"","type":"bytes"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"bytes32","name":"name","type":"bytes32"}],"name":"hasDNSRecords","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"bytes4","name":"interfaceID","type":"bytes4"}],"name":"interfaceImplementer","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes[]","name":"data","type":"bytes[]"}],"name":"multicall","outputs":[{"internalType":"bytes[]","name":"results","type":"bytes[]"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"}],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"}],"name":"pubkey","outputs":[{"internalType":"bytes32","name":"x","type":"bytes32"},{"internalType":"bytes32","name":"y","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"uint256","name":"contentType","type":"uint256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"setABI","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"uint256","name":"coinType","type":"uint256"},{"internalType":"bytes","name":"a","type":"bytes"}],"name":"setAddr","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"address","name":"a","type":"address"}],"name":"setAddr","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"address","name":"target","type":"address"},{"internalType":"bool","name":"isAuthorised","type":"bool"}],"name":"setAuthorisation","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"bytes","name":"hash","type":"bytes"}],"name":"setContenthash","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"setDNSRecords","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"bytes4","name":"interfaceID","type":"bytes4"},{"internalType":"address","name":"implementer","type":"address"}],"name":"setInterface","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"string","name":"name","type":"string"}],"name":"setName","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"bytes32","name":"x","type":"bytes32"},{"internalType":"bytes32","name":"y","type":"bytes32"}],"name":"setPubkey","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"string","name":"key","type":"string"},{"internalType":"string","name":"value","type":"string"}],"name":"setText","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes4","name":"interfaceID","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"pure","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"string","name":"key","type":"string"}],"name":"text","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"}]')
contract_addr_ens = "0x42D63ae25990889E35F215bC95884039Ba354115"
contract_ens = web3.eth.contract(address=contract_addr_ens, abi=abi_ens)

local_addr = "0.0.0.0"
local_port = 1700

WATCHER_URL = 'https://watcher.rinkeby.v1.omg.network'
WATCHER_INFO_URL = 'https://watcher-info.rinkeby.v1.omg.network'

# remote_host = "163.172.130.246"
# remote_port = 9999

# remote_host = "router.eu.thethings.network"
# remote_port = 1700

counter = 0
message = b'error, no server response'
messageQueue = queue.Queue()
packet_forwarder_response_add = 0
# message = b'\xd2\x84C\xa1\x01&\xa0X`\xd0\x83XA\xa3\x01\x01\x05X\x1a000102030405060708090a0b0c\x00x\x1e["1000", 1, "163.172.130.246"]\xa0X\x18q\xe5\'C\x15\xecp=\xce\xe9\x03\xb9\r\xccz(v\x9f\xfe\x9c\x0c\xb8f\xaeX@\x1e/ql\xc4T\xde\x80\x83\x1c-\xc4\x83\xefy\x17/\xad\xfd\xeb\x10\xf6\xf9\xec\xda\x8dL?\x00h\xa4H\xb9\xbb!\x9c\xe4\xcc\xa1\xebg\x05?r\xc6\x8b?B,\x95J\xf8\xdb\xbcxHP\xcb=F\x8f\x9d\xbb\xa3'


async def save_msg(msg, pType, counter, deviceAdd, host, port) :
    id = str(time.time())
    date = str(datetime.datetime.now().strftime('%d-%m-%Y_%H:%M:%S'))

    x = {"_id" : id, "date" : date, "host" : host, "port" : port, "payed" : False, "header" : {"pType" : pType, "counter" : counter, "deviceAdd" : deviceAdd}, "msg" : msg}
    result = await collection_MSG.insert_one(x)


async def get_msg(host, deviceAdd, counter_start, counter_end) :
    store = []
    for i in range(counter_start, counter_end) :
        x = {"host" : host, "header" : {"counter" : i, "deviceAdd" : deviceAdd}}
        document = await collection_MSG.find_one(x)
        store.append(document)

    return store


async def url_process(url) :
    # ip4 = "https://111.111.111.111:65535"
    # ip4 = "111.111.111.111:65535"
    # print(len(ip4))

    # ip6 = "https://[0:0:0:0:0:0:0:1]:123"
    # ip6 = "[0:0:0:0:0:0:0:1]:123"
    # print(len(ip6))

    add = url.split(":")
    # print(add)
    # print(len(add))

    # if IPv4
    if len(add) < 4 :
        # print("ipv4")
        # port + http
        if len(add) > 2 and "http" in add[0] :
            # contain "http://" or "https://"
            add.pop(0)
            add[0] = add[0].replace("/", "")
        # only address --> no port
        elif len(add) == 1 :
            address = add[0]
            address = address.replace("/", "")
            address = address.replace(" ", "")
            port = 0
            return address, port
        # address + http
        elif len(add) == 2 and "http" in add[0] :
            address = add[len(add)-1]
            address = address.replace("/", "")
            address = address.replace(" ", "")
            port = 0
            return address, port

        address = add[0]
        address = address.replace("/", "")
        address = address.replace(" ", "")
        port = add[len(add)-1]
        port = int(port)
        # print(address)
        # print(port)
        return address, port

    # if IPv6
    else :
        # print("ipv6")
        # port + http
        if len(add) > 9 and "http" in add[0] :
            # contain "http://" or "https://"
            add.pop(0)
            add[0] = add[0].replace("/", "")
            add[0] = add[0].replace("[", "")
            add[len(add)-2] = add[len(add)-2].replace("]", "")
        # only address
        elif len(add) == 8 :
            address = ':'.join(add)
            address = address.replace("/", "")
            address = address.replace(" ", "")
            port = 0
            return address, port
        # address + http
        elif len(add) == 9 and "http" in add[0] :
            address = ':'.join(add[1:])
            address = address.replace("/", "")
            address = address.replace(" ", "")
            port = 0
            return address, port
        # address + port
        elif len(add) == 9 and "http" not in add[0] :
            add[0] = add[0].replace("[", "")
            add[len(add)-2] = add[len(add)-2].replace("]", "")

        # print(add)
        address = ':'.join(add[:-1])
        address = address.replace("/", "")
        address = address.replace(" ", "")
        port = add[len(add)-1]
        port = int(port)
        # print(address)
        # print(port)
        return address, port


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


class ProxyDatagramProtocol():

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        #print(data)
        loop = asyncio.get_event_loop()
        loop.create_task(self.datagram_received_async(data, addr))

    async def datagram_received_async(self, data, addr):
        global counter
        global message
        global messageQueue
        print("Received from device :", data)
        if data[3] == 0:
            processed = await process(data)
            if processed != b'error':
                counter = 1

                # send an ack to the packet forwarder
                ack = data[:4]
                a = bytearray(ack)
                a[3] = 1
                ack = bytes(a)
                self.transport.sendto(ack, addr)

                # get source of message
                try :
                    header = await get_header(processed)
                    pType = header[0]
                    counter_header = header[1]
                    deviceAdd = header[2]
                    print("header :", header)
                    print("deviceAdd :", deviceAdd)

                    # get address from blockchain
                    device = await contract_lora.functions.devices(int(deviceAdd, 0)).call()
                    print(device)
                    ipv4Addr = device[0]
                    ipv6Addr = device[1]
                    domain = device[2]
                    ipv4Port = device[3]
                    ipv6Port = device[4]
                    domainPort = device[5]

                    # domain = "ip6.loramac.eth"
                    # domainPort = 30

                    # analyze address
                    if domain != "":
                        print("domain")
                        # if .eth and no port in address
                        if domain[-4:] == ".eth":
                            print("eth add")
                            # get ip
                            name_hash = namehash(domain)
                            url = await contract_ens.functions.text(name_hash, "url").call()
                            print(url)
                            remote_host, remote_port = await url_process(url)
                            if remote_port == 0 :
                                remote_port = domainPort
                        else :
                            add = domain.split(":")
                            # if .eth with port --> use port in ens or domainPort and not the one with the url
                            if add[0][-4:] == ".eth":
                                print("eth add")
                                remote_port = add[len(add)-1]
                                remote_port = int(remote_port)
                                # print(remote_port)
                                # get ip
                                name_hash = namehash(add[0])
                                url = await contract_ens.functions.text(name_hash, "url").call()
                                print(url)
                                remote_host, remote_port = await url_process(url)
                                if remote_port == 0 :
                                    remote_port = domainPort

                            # if not .eth
                            else :
                                remote_host = add[0]
                                # if port
                                if len(add) > 1:
                                    remote_port = add[len(add)-1]
                                    remote_port = int(port)
                                else :
                                    remote_port = domainPort
                                # print(remote_host)
                                # print(remote_port)
                                print("not eth add")
                                # resolve DNS to get ip
                                remote_host = socket.gethostbyname(remote_host)
                                # print(remote_host)

                    elif ipv4Addr != 0 :
                        remote_host = str(ipaddress.IPv4Address(ipv4Addr))
                        remote_port = ipv4Port

                    elif ipv6Addr != 0 :
                        remote_host = str(ipaddress.IPv6Address(ipv6Addr))
                        remote_port = ipv6Port

                    print(remote_host)
                    print(remote_port)

                    await save_msg(processed, pType, counter_header, deviceAdd, remote_host, remote_port)

                    processed = processed + ether_add
                    # send hash + signature to the
                    # --> divise message entre contenu et signature 

                    # loop = asyncio.get_event_loop()
                    # coro = loop.create_datagram_endpoint(
                    #     lambda: RemoteDatagramProtocol(self, addr, processed),
                    #     remote_addr=(remote_host, remote_port))
                    # asyncio.ensure_future(coro)



                except ValueError :
                    print("ValueError")
                    message = b'error, corrupted data'
                except TypeError :
                    print("TypeError")
                    message = b'error, corrupted data'



        if data[3] == 2 :
            # if counter == 1 :
            #     c = 0
            #     while message == b'error, no server response' and c < 10 :
            #         await asyncio.sleep(1)
            #         c = c + 1

            #     counter = 0

            #     ack = data[:4]
            #     a = bytearray(ack)
            #     a[3] = 4
            #     ack = bytes(a)
            #     self.transport.sendto(ack, addr)

            #     response = await generate_response(message)
            #     print("response :", response)
            #     self.transport.sendto(response, addr)
            #     message = b'error, no server response'
            
            if messageQueue.empty() == False :

                ack = data[:4]
                a = bytearray(ack)
                a[3] = 4
                ack = bytes(a)
                self.transport.sendto(ack, addr)

                message = messageQueue.get()
                response = await generate_response(message)
                print("response :", response)
                self.transport.sendto(response, addr)
                message = b'error, no server response'


async def ws_send(uri, message):
    async with websockets.connect(uri) as websocket:
        await websocket.send(message)
        response = await websocket.recv()


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

        global messageQueue
        messageQueue.put(data)


    def error_received(self, exc):
        print('Error received:', exc)
        global messageQueue
        messageQueue.put(b'error, no server response')
    
    def connection_lost(self, exc):
        print('Connection lost')
        #self.proxy.remotes.pop(self.attr)
        self.proxy.remotes.pop(self.addr)



async def start_datagram_proxy(bind, port):
    # hashed = '0x851237ba43c9586b47e3bc2c41f7f92b31d4275f117f0f0cd16162590a4eb79c'
    # hashed = '0xf4a33b43f41313faf9124d897b851d49c76d772bfa48870622977643af21c6f9'
    # await verifyHash(hashed)
    loop = asyncio.get_event_loop()
    return await loop.create_datagram_endpoint(
        lambda: ProxyDatagramProtocol(),
        local_addr=(bind, port))


async def verifyHash(hashed):
    body = {'id': hashed, 'jsonrpc': '2.0'}
    body = json.dumps(body)
    # print(body)
    response = await requests.post(f'{WATCHER_INFO_URL}/transaction.get', data=body, headers= { 'Content-Type': 'application/json'})
    json_resp = response.json()
    # print(json_resp)
    try :
        sender = json_resp['data']['inputs'][0]['owner']
        currency = json_resp['data']['inputs'][0]['currency']
        amount = json_resp['data']['outputs'][1]['amount']
        receiver = json_resp['data']['outputs'][1]['owner']
        metadata = json_resp['data']['metadata']
        print(sender)
        print(currency)
        print(amount)
        print(receiver)
        print(metadata)
        # decrypt metadata
        metadata = bytearray.fromhex(metadata[2:]).decode()
        print(metadata)
    except KeyError :
        print("Transaction does not exist")


def main(bind=local_addr, port=local_port):
    loop = asyncio.get_event_loop()
    print("Starting UDP proxy server...")
    coro = start_datagram_proxy(bind, port)
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
