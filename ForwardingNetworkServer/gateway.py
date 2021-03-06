import asyncio
import websockets
import json
import datetime
import time
import queue
import socket
import ipaddress
import web3s
import motor.motor_asyncio
import hashlib
import ipaddress
import os
from dotenv import load_dotenv

from lora import get_header, verify_countersign
from namehash import namehash
from omg import verify_omg_payment
from mpc import verify_mpc_payment
from url import url_process
from udp_message import message_process, generate_response

load_dotenv()

MONGO_DB = os.getenv('MONGO_DB')
NODE_ADDRESS = os.getenv('NODE_ADDRESS')
ETHER_ADDRESS = os.getenv('ETHER_ADDRESS')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
PORT = os.getenv('PORT')
BALANCE_THRESHOLD = os.getenv('BALANCE_THRESHOLD')
TIME_THRESHOLD = os.getenv('TIME_THRESHOLD')
MESSAGE_PRICE = os.getenv('MESSAGE_PRICE')

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DB)
db = client['lora_db']
collection_MSG = db['MSG_GATEWAY']

ether_add = ETHER_ADDRESS
private_key = PRIVATE_KEY

infura_url = NODE_ADDRESS
web3 = web3s.Web3s(web3s.Web3s.HTTPProvider(infura_url))

abi_lora = json.loads('[{"inputs":[{"internalType":"uint64","name":"","type":"uint64"}],"name":"devices","outputs":[{"internalType":"uint32","name":"ipv4Addr","type":"uint32"},{"internalType":"uint128","name":"ipv6Addr","type":"uint128"},{"internalType":"string","name":"domain","type":"string"},{"internalType":"uint16","name":"ipv4Port","type":"uint16"},{"internalType":"uint16","name":"ipv6Port","type":"uint16"},{"internalType":"uint16","name":"domainPort","type":"uint16"},{"internalType":"address","name":"owner","type":"address"},{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"","type":"string"}],"name":"domainServers","outputs":[{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"},{"internalType":"address","name":"owner","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint32","name":"","type":"uint32"}],"name":"ipv4Servers","outputs":[{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"},{"internalType":"address","name":"owner","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint128","name":"","type":"uint128"}],"name":"ipv6Servers","outputs":[{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"},{"internalType":"address","name":"owner","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint64","name":"loraAddr","type":"uint64"},{"internalType":"string","name":"domain","type":"string"},{"internalType":"uint16","name":"port","type":"uint16"},{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"}],"name":"registerDomainDevice","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"string","name":"domain","type":"string"},{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"}],"name":"registerDomainServer","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint64","name":"loraAddr","type":"uint64"},{"internalType":"uint32","name":"server","type":"uint32"},{"internalType":"uint16","name":"port","type":"uint16"},{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"}],"name":"registerIpv4Device","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint32","name":"ipv4Addr","type":"uint32"},{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"}],"name":"registerIpv4Server","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint64","name":"loraAddr","type":"uint64"},{"internalType":"uint128","name":"server","type":"uint128"},{"internalType":"uint16","name":"port","type":"uint16"},{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"}],"name":"registerIpv6Device","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint128","name":"ipv6Addr","type":"uint128"},{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"}],"name":"registerIpv6Server","outputs":[],"stateMutability":"nonpayable","type":"function"}]')
contract_addr_lora = "0x4a9fF7c806231fF7d4763c1e83E8B131467adE61"
contract_lora = web3.eth.contract(contract_addr_lora, abi=abi_lora)

abi_ens = json.loads('[{"inputs":[{"internalType":"contract ENS","name":"_ens","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":true,"internalType":"uint256","name":"contentType","type":"uint256"}],"name":"ABIChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":false,"internalType":"address","name":"a","type":"address"}],"name":"AddrChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":false,"internalType":"uint256","name":"coinType","type":"uint256"},{"indexed":false,"internalType":"bytes","name":"newAddress","type":"bytes"}],"name":"AddressChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"target","type":"address"},{"indexed":false,"internalType":"bool","name":"isAuthorised","type":"bool"}],"name":"AuthorisationChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":false,"internalType":"bytes","name":"hash","type":"bytes"}],"name":"ContenthashChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":false,"internalType":"bytes","name":"name","type":"bytes"},{"indexed":false,"internalType":"uint16","name":"resource","type":"uint16"},{"indexed":false,"internalType":"bytes","name":"record","type":"bytes"}],"name":"DNSRecordChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":false,"internalType":"bytes","name":"name","type":"bytes"},{"indexed":false,"internalType":"uint16","name":"resource","type":"uint16"}],"name":"DNSRecordDeleted","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"}],"name":"DNSZoneCleared","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":true,"internalType":"bytes4","name":"interfaceID","type":"bytes4"},{"indexed":false,"internalType":"address","name":"implementer","type":"address"}],"name":"InterfaceChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":false,"internalType":"string","name":"name","type":"string"}],"name":"NameChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":false,"internalType":"bytes32","name":"x","type":"bytes32"},{"indexed":false,"internalType":"bytes32","name":"y","type":"bytes32"}],"name":"PubkeyChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":true,"internalType":"string","name":"indexedKey","type":"string"},{"indexed":false,"internalType":"string","name":"key","type":"string"}],"name":"TextChanged","type":"event"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"uint256","name":"contentTypes","type":"uint256"}],"name":"ABI","outputs":[{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"bytes","name":"","type":"bytes"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"}],"name":"addr","outputs":[{"internalType":"address payable","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"uint256","name":"coinType","type":"uint256"}],"name":"addr","outputs":[{"internalType":"bytes","name":"","type":"bytes"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"","type":"bytes32"},{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"authorisations","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"}],"name":"clearDNSZone","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"}],"name":"contenthash","outputs":[{"internalType":"bytes","name":"","type":"bytes"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"bytes32","name":"name","type":"bytes32"},{"internalType":"uint16","name":"resource","type":"uint16"}],"name":"dnsRecord","outputs":[{"internalType":"bytes","name":"","type":"bytes"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"bytes32","name":"name","type":"bytes32"}],"name":"hasDNSRecords","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"bytes4","name":"interfaceID","type":"bytes4"}],"name":"interfaceImplementer","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes[]","name":"data","type":"bytes[]"}],"name":"multicall","outputs":[{"internalType":"bytes[]","name":"results","type":"bytes[]"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"}],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"}],"name":"pubkey","outputs":[{"internalType":"bytes32","name":"x","type":"bytes32"},{"internalType":"bytes32","name":"y","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"uint256","name":"contentType","type":"uint256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"setABI","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"uint256","name":"coinType","type":"uint256"},{"internalType":"bytes","name":"a","type":"bytes"}],"name":"setAddr","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"address","name":"a","type":"address"}],"name":"setAddr","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"address","name":"target","type":"address"},{"internalType":"bool","name":"isAuthorised","type":"bool"}],"name":"setAuthorisation","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"bytes","name":"hash","type":"bytes"}],"name":"setContenthash","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"setDNSRecords","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"bytes4","name":"interfaceID","type":"bytes4"},{"internalType":"address","name":"implementer","type":"address"}],"name":"setInterface","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"string","name":"name","type":"string"}],"name":"setName","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"bytes32","name":"x","type":"bytes32"},{"internalType":"bytes32","name":"y","type":"bytes32"}],"name":"setPubkey","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"string","name":"key","type":"string"},{"internalType":"string","name":"value","type":"string"}],"name":"setText","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes4","name":"interfaceID","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"pure","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"string","name":"key","type":"string"}],"name":"text","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"}]')
contract_addr_ens = "0x42D63ae25990889E35F215bC95884039Ba354115"
contract_ens = web3.eth.contract(address=contract_addr_ens, abi=abi_ens)

local_addr = "0.0.0.0"
local_port = int(PORT)

counter = 0
message = b'error, no server response'
messageQueue = queue.Queue()
packet_forwarder_response_add = 0

message_price = int(MESSAGE_PRICE)
balance_threshold = float(BALANCE_THRESHOLD)
time_threshold = int(TIME_THRESHOLD)


class ProxyDatagramProtocol():

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        loop = asyncio.get_event_loop()
        loop.create_task(self.datagram_received_async(data, addr))

    async def datagram_received_async(self, data, addr):
        global counter
        global message
        global messageQueue

        if data[3] == 0:
            processed = await message_process(data)
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

                    # get address from blockchain + pub key
                    # convert deviceAdd to decimal
                    device = await contract_lora.functions.devices(int(deviceAdd, 0)).call()
                    ipv4Addr = device[0]
                    ipv6Addr = device[1]
                    domain = device[2]
                    ipv4Port = device[3]
                    ipv6Port = device[4]
                    domainPort = device[5]
                    x_pub = int(device[7])
                    y_pub = int(device[8])

                    x_pub = format(x_pub, '064x')
                    y_pub = format(y_pub, '064x')
                    print("x_pub : ", x_pub)
                    print("y_pub : ", y_pub)

                    # verify signature
                    valid = await verify_countersign(processed, x_pub, y_pub)
                    if valid != False :
                        print("Signature is correct")
                        # get the hash and the signature to send
                        to_be_signed = valid._sig_structure
                        hash_structure = hashlib.sha256(to_be_signed).digest()
                        signature = valid.signature

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
                                    print("not eth add")
                                    # resolve DNS to get ip
                                    remote_host = socket.gethostbyname(remote_host)

                        elif ipv4Addr != 0 :
                            remote_host = str(ipaddress.IPv4Address(ipv4Addr))
                            remote_port = ipv4Port

                        elif ipv6Addr != 0 :
                            remote_host = str(ipaddress.IPv6Address(ipv6Addr))
                            remote_port = ipv6Port

                        print(f"Send message to server : {remote_host} on port : {remote_port}")

                        await save_msg(processed, pType, counter_header, deviceAdd, remote_host, remote_port)

                        loop = asyncio.get_event_loop()
                        loop.create_task(ws_send(f"ws://{remote_host}:{8765}", hash_structure, signature, deviceAdd, counter_header, remote_host))

                except ValueError :
                    print("ValueError")
                    message = b'error, corrupted data'
                    messageQueue.put(message)
                except TypeError :
                    print("TypeError")
                    message = b'error, corrupted data'
                    messageQueue.put(message)
                except AttributeError :
                    print("AttributeError")
                    message = b'error, corrupted data'
                    messageQueue.put(message)
                except SystemError :
                    print("SystemError")
                    message = b'error, corrupted data'
                    messageQueue.put(message)


        if data[3] == 2 :
            if messageQueue.empty() == False :

                ack = data[:4]
                a = bytearray(ack)
                a[3] = 4
                ack = bytes(a)
                self.transport.sendto(ack, addr)

                message = messageQueue.get()
                response = await generate_response(message)
                print("Response to the device :", response)
                self.transport.sendto(response, addr)



async def ws_send(uri, hash_structure, signature, deviceAdd, counter_header, remote_host) :
    global messageQueue
    try :
        async with websockets.connect(uri) as websocket:
            try :

                packet = deviceAdd + "," + counter_header + "," + ether_add

                await websocket.send(hash_structure)
                await websocket.send(signature)
                await websocket.send(packet)

                payment_receipt = await websocket.recv()
                if "error" not in payment_receipt:
                    down_message = await websocket.recv()
                    print("Payment receipt :", payment_receipt)
                    print("Down message :", down_message)

                    payment_list = payment_receipt.split(',')
                    if payment_list[0] == 'OMG' :
                        price = message_price
                        # send down_message directly if any
                        if down_message != b"down_message":
                            # verify down
                            verified = await verify_down(down_message)
                            if verified :
                                print("Down signature is valid")
                                price = message_price * 2
                                messageQueue.put(down_message)
                        else :
                            messageQueue.put(b"success : processing the message on the gateway")

                        payment_hash = payment_list[1]
                        # sleep 2 minutes
                        print("Sleep for 2 minutes")
                        await asyncio.sleep(120)
                        metadata = await verify_omg_payment(payment_hash, remote_host, price, ether_add)
                        # get value from metadata
                            # split ,
                        if metadata != None :
                            meta_list = metadata.split(",")
                            counter_header = meta_list[1]
                            deviceAdd = meta_list[2]

                            # get and pay message
                            message = await get_and_pay(remote_host, deviceAdd, counter_header)
                        else :
                            message = None


                    if payment_list[0] == 'MPC' :
                        signature = payment_list[1]
                        contract_add = payment_list[2]
                        payed_amount = int(payment_list[3])

                        verified = await verify_mpc_payment(web3, client, signature, contract_add, payed_amount, remote_host, balance_threshold, time_threshold)
                        if verified == True :
                            # send down_message if any
                            if down_message != b"down_message" and payed_amount == 2*message_price:
                                verified2 = await verify_down(down_message)
                                if verified2 :
                                    messageQueue.put(down_message)

                            message = await get_and_pay(remote_host, deviceAdd, counter_header)

                        elif verified ==  "error : smart contract closed":
                            message = verified
                            # send down_message if any
                            if down_message != b"down_message" and payed_amount == 2*message_price:
                                verified = await verify_down(down_message)
                                if verified :
                                    print("Down signature is valid")
                                    messageQueue.put(down_message)

                            # send message
                            message2 = await get_and_pay(remote_host, deviceAdd, counter_header)

                        else :
                            message = None

                    if message != b"" and message != None :
                        if message == "error : smart contract closed":
                            await websocket.send(message)
                            await websocket.send(message2['msg'])
                        else :
                            await websocket.send(message['msg'])

                        print("Message sent to server")

                        if down_message == b"down_message" and payment_list[0] == 'MPC':

                            payment_receipt = await websocket.recv()
                            response = await websocket.recv()
                            print("payment_receipt :", payment_receipt)
                            print("received response :", response)

                            if payment_receipt != "nothing":
                                payment_list = payment_receipt.split(',')
                                if payment_list[0] == 'MPC' :
                                    signature = payment_list[1]
                                    contract_add = payment_list[2]
                                    payed_amount = int(payment_list[3])

                                    verified = await verify_mpc_payment(web3, client, signature, contract_add, payed_amount, remote_host, balance_threshold, time_threshold)
                                    if verified != False and response != "nothing":
                                        verified2 = await verify_down(response)
                                        if verified2 :
                                            print("Down signature is valid")
                                            messageQueue.put(response)
                                            if verified == "error : smart contract closed":
                                                await websocket.send("error : smart contract closed")
                                            else :
                                                await websocket.send("success")

                    else :
                        await websocket.send("invalid payment")

                else :
                    print(payment_receipt)


            except RuntimeError :
                print("Closing the websocket")
                await websocket.close()

    except ConnectionRefusedError :
        response = b"error : no server connection"
        print(response)
        messageQueue.put(response)
    except RuntimeError :
        print("Closing the connection")


async def verify_down(message):
    header = await get_header(message)
    pType = header[0]
    counter_header = header[1]
    hostAdd = header[2]

    if hostAdd.count(":") > 1:
        addr = int(ipaddress.IPv6Address(hostAdd))
        server = await contract_lora.functions.ipv6Servers(addr).call()
    elif hostAdd[0].isdigit() and hostAdd[len(hostAdd)-1].isdigit() :
        addr = int(ipaddress.IPv4Address(hostAdd))
        server = await contract_lora.functions.ipv4Servers(addr).call()
    else :
        server = await contract_lora.functions.domainServers(hostAdd).call()

    if int(server[0]) != 0 and int(server[1]) != 0 :
        x_pub = int(server[0])
        y_pub = int(server[1])

        x_pub = format(x_pub, '064x')
        y_pub = format(y_pub, '064x')

        # verify signature
        valid = await verify_countersign(message, x_pub, y_pub)

        return valid

    else :
        return False


async def save_msg(msg, pType, counter, deviceAdd, host, port) :
    id = str(time.time())
    date = str(datetime.datetime.now().strftime('%d-%m-%Y_%H:%M:%S'))

    x = {"_id" : id, "date" : date, "host" : host, "port" : port, "payed" : False, "pType" : pType, "counter" : counter, "deviceAdd" : deviceAdd, "msg" : msg}
    result = await collection_MSG.insert_one(x)


async def get_and_pay(host, deviceAdd, counter_header) :
    x = {"host" : host, "counter" : counter_header, "deviceAdd" : deviceAdd, "payed" : False}
    document = await collection_MSG.find_one(x, sort=[('_id', -1)])
    if document != None:
        payed = {"payed" : True}
        await collection_MSG.update_one(x, {'$set': payed})
    return document


async def start_datagram_proxy(bind, port):
    print("Web3 is connected ?", await web3.isConnected())
    loop = asyncio.get_event_loop()
    return await loop.create_datagram_endpoint(
        lambda: ProxyDatagramProtocol(),
        local_addr=(bind, port))



def main(bind=local_addr, port=local_port):
    loop = asyncio.get_event_loop()
    coro = start_datagram_proxy(bind, port)
    transport, _ = loop.run_until_complete(coro)
    print("UDP server is running...\n")

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    print("\nClosing transport...")
    transport.close()
    loop.close()



if __name__ == '__main__':
    main()
