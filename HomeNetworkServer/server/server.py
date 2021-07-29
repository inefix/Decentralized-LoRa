"""UDP server"""
# https://gist.github.com/vxgmichel/b2cf8536363275e735c231caef35a5df
# https://docs.python.org/3/library/asyncio-protocol.html

import json
import datetime
import time
import ipaddress
import hashlib
import asyncio
import websockets
from aiohttp import web
import aiohttp_cors
import motor.motor_asyncio

from lora import generate_deviceAdd, generate_key_pair, get_header, check_signature, generate_key_sym, decrypt, encrypt, sign, verify_signature_hash

import web3s
import requests_async as requests

ADDR = "163.172.130.246"
# ADDR = "2001:0620:0000:0000:0211:24FF:FE80:C12C"
PORT = 9999

ADDR_int = ADDR
ADDR_type = None

# payment_method can be 'OMG' or 'MPC'
payment_method = 'MPC'  
message_price = 100

automatic_pay = True
automatic_response = True

if ADDR.count(":") > 1:
    print("IPv6")
    ADDR_int = int(ipaddress.IPv6Address(ADDR))
    ADDR_type = "IPv6"
    print(ADDR_int)
elif ADDR[0].isdigit() and ADDR[len(ADDR)-1].isdigit() :
    print("IPv4")
    ADDR_int = int(ipaddress.IPv4Address(ADDR))
    ADDR_type = "IPv4"
    print(ADDR_int)
else :
    print("domain")
    ADDR_type = "domain"

# ADDR = str(ipaddress.IPv4Address(ADDR))
# print(ADDR)

client = motor.motor_asyncio.AsyncIOMotorClient('mongodb+srv://lora:lora@lora.j8ycs.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')

db = client['lora_db']
collection_DEVICE = db['DEVICE']
collection_MSG = db['MSG']
collection_GATEWAY = db['GATEWAY']
collection_DOWN = db['DOWN']


infuria_url = "https://rinkeby.infura.io/v3/4d24fe93ef67480f97be53ccad7e43d6"
web3 = web3s.Web3s(web3s.Web3s.HTTPProvider(infuria_url))

abi_lora = json.loads('[{"inputs":[{"internalType":"uint64","name":"","type":"uint64"}],"name":"devices","outputs":[{"internalType":"uint32","name":"ipv4Addr","type":"uint32"},{"internalType":"uint128","name":"ipv6Addr","type":"uint128"},{"internalType":"string","name":"domain","type":"string"},{"internalType":"uint16","name":"ipv4Port","type":"uint16"},{"internalType":"uint16","name":"ipv6Port","type":"uint16"},{"internalType":"uint16","name":"domainPort","type":"uint16"},{"internalType":"address","name":"owner","type":"address"},{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"","type":"string"}],"name":"domainServers","outputs":[{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"},{"internalType":"address","name":"owner","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint32","name":"","type":"uint32"}],"name":"ipv4Servers","outputs":[{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"},{"internalType":"address","name":"owner","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint128","name":"","type":"uint128"}],"name":"ipv6Servers","outputs":[{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"},{"internalType":"address","name":"owner","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint64","name":"loraAddr","type":"uint64"},{"internalType":"string","name":"domain","type":"string"},{"internalType":"uint16","name":"port","type":"uint16"},{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"}],"name":"registerDomainDevice","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"string","name":"domain","type":"string"},{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"}],"name":"registerDomainServer","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint64","name":"loraAddr","type":"uint64"},{"internalType":"uint32","name":"server","type":"uint32"},{"internalType":"uint16","name":"port","type":"uint16"},{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"}],"name":"registerIpv4Device","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint32","name":"ipv4Addr","type":"uint32"},{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"}],"name":"registerIpv4Server","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint64","name":"loraAddr","type":"uint64"},{"internalType":"uint128","name":"server","type":"uint128"},{"internalType":"uint16","name":"port","type":"uint16"},{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"}],"name":"registerIpv6Device","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint128","name":"ipv6Addr","type":"uint128"},{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"}],"name":"registerIpv6Server","outputs":[],"stateMutability":"nonpayable","type":"function"}]')
contract_addr_lora = "0x4a9fF7c806231fF7d4763c1e83E8B131467adE61"
contract_lora = web3.eth.contract(contract_addr_lora, abi=abi_lora)


add = "0.0.0.0"     # localhost does not work ! https://stackoverflow.com/questions/15734219/simple-python-udp-server-trouble-receiving-packets-from-clients-other-than-loca/15734249

serialized_private_server = b'-----BEGIN PRIVATE KEY-----\nMIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQg5hsInzp4UhjgehRh\nA+55y9GGR7dai4Kky4LCYpE+jFGhRANCAATCl2kTYWbuwSmeG11WxI3heHo/cvDo\n7lwUNX71t4/G6nZmsAwwgkjPgkyOIk3Y/8xMzRNiyCLy6oL1sB954bSa\n-----END PRIVATE KEY-----\n'
serialized_public_server = b'-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEwpdpE2Fm7sEpnhtdVsSN4Xh6P3Lw\n6O5cFDV+9bePxup2ZrAMMIJIz4JMjiJN2P/MTM0TYsgi8uqC9bAfeeG0mg==\n-----END PUBLIC KEY-----\n'
x_pub_server = "c29769136166eec1299e1b5d56c48de1787a3f72f0e8ee5c14357ef5b78fc6ea"
y_pub_server = "7666b00c308248cf824c8e224dd8ffcc4ccd1362c822f2ea82f5b01f79e1b49a"


async def get_addr_server(request):
    response = {"ADDR_int" : ADDR_int, "ADDR_type" : ADDR_type}
    return web.json_response(response)


async def get_server_pubkey(request):
    response = {"x_pub_server" : x_pub_server, "y_pub_server" : y_pub_server}
    return web.json_response(response)


async def read_increment_counter():
    try :
        # read the counter
        f = open("counter.txt", "r")
        counter = f.read()
        f.close()
    except FileNotFoundError:
        counter = ""

    if counter == "" :
        counter = 0
    else :
        counter = int(counter) + 1
    # print(counter)
    # update the counter
    f = open("counter.txt", "w")
    f.write(str(counter))
    f.close()

    return counter


async def start(request):
    print("Server started")
    return web.json_response({'success': 'Server started'})

async def test(request):
    print("test")

    deviceAdd = "0x1145f03880d8a975"
    # serialized_public = b'-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEZDhmwCVlGBcPJOj7AbIzP9fvFC6q\n4JqowSK0G5BmPQzU3WQ3EDrbzoPHV4jzduZ7uKt/zHWu6TMr0gkgdyOybw==\n-----END PUBLIC KEY-----\n'.decode("utf-8")
    x_pub = "643866c0256518170f24e8fb01b2333fd7ef142eaae09aa8c122b41b90663d0c"
    y_pub = "d4dd6437103adbce83c75788f376e67bb8ab7fcc75aee9332bd209207723b26f"
    ts = str(time.time())
    date = str(datetime.datetime.now().strftime('%d-%m-%Y_%H:%M:%S'))
    x = {"_id" : deviceAdd, "deviceAdd": deviceAdd, "x_pub": x_pub, "y_pub": y_pub, "ts": ts, "date": date, "name": "test", "serverAdd": ADDR_int, "port": PORT}

    # check unique id
    y = {"_id" : deviceAdd}
    document = await collection_DEVICE.find_one(y)
    if str(type(document)) == "<class 'NoneType'>":
        await collection_DEVICE.insert_one(x)
        # store new device in smart contract
        return web.json_response({'success': 'Added successfuly'})
    else :
        return web.json_response({'error': 'Device already registred'}, status=404)


async def get_all_devices(request):
    return web.json_response([
        document async for document in collection_DEVICE.find().sort("ts", -1)
    ])


# curl -X DELETE http://163.172.130.246:8080/devices
async def remove_all_devices(request):
    await collection_DEVICE.delete_many({})
    return web.Response(status=204)


# curl -X POST -d '{"deviceAdd":"deviceAdd", "pubkey":"pubkey"}' http://163.172.130.246/devices
# curl -X POST -d '{"deviceAdd":"0x41e9d7694004027a", "pubkey":b"-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEfXcUEiG1lHD41LaUmXdaX5A9BzfU\nNmvTKCDK+RGZuKXoP5Ja8dlU7xcgmudn8BXklXZfre/eQHW/hD69ZGWWAw==\n-----END PUBLIC KEY-----\n"}' http://163.172.130.246/devices
# serialized_private_device : b'-----BEGIN PRIVATE KEY-----\nMIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgbY3ljUYU0uyCLvIz\nXgibqcvad4iYdDG7kXiu8eEIFvuhRANCAAR9dxQSIbWUcPjUtpSZd1pfkD0HN9Q2\na9MoIMr5EZm4peg/klrx2VTvFyCa52fwFeSVdl+t795Adb+EPr1kZZYD\n-----END PRIVATE KEY-----\n'
# serialized_public_device : b'-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEfXcUEiG1lHD41LaUmXdaX5A9BzfU\nNmvTKCDK+RGZuKXoP5Ja8dlU7xcgmudn8BXklXZfre/eQHW/hD69ZGWWAw==\n-----END PUBLIC KEY-----\n'
async def create_device(request):
    data = await request.json()

    if 'deviceAdd' not in data:
        return web.json_response({'error': '"deviceAdd" is a required field'}, status=404)
    deviceAdd = data['deviceAdd']
    if not isinstance(deviceAdd, str) or not len(deviceAdd):
        return web.json_response({'error': '"deviceAdd" must be a string with at least one character'}, status=404)
    
    if 'pubkey' not in data:
        return web.json_response({'error': '"pubkey" is a required field'}, status=404)
    pubkey = data['pubkey']
    if not isinstance(pubkey, str) or not len(pubkey):
        return web.json_response({'error': '"pubkey" must be a string with at least one character'}, status=404)
    
    # check unique id
    x = {"_id" : data['deviceAdd']}
    document = await collection_DEVICE.find_one(x)
    if str(type(document)) == "<class 'NoneType'>":
        data['_id'] = data['deviceAdd']
        data['name'] = data['deviceAdd']
        data['ts'] = str(time.time())
        data['date'] = str(datetime.datetime.now().strftime('%d-%m-%Y_%H:%M:%S'))
        result = await collection_DEVICE.insert_one(data)
        # store new device in smart contract
        #return web.Response(text="Added successfuly", status=204)
        return web.json_response({'success': 'Added successfuly'})
    else :
        return web.json_response({'error': 'Device already registred'}, status=404)


async def get_one_device(request):
    id = str(request.match_info['id'])

    x = {"_id" : id}

    document = await collection_DEVICE.find_one(x)

    if str(type(document)) == "<class 'NoneType'>":
        return web.json_response({'error': 'Device not found'}, status=404)

    return web.json_response(document)


# curl -X PATCH -d '{"deviceAdd":"deviceAdd2", "pubkey":"pubkey2"}' http://163.172.130.246:8080/devices/deviceAdd
async def update_device(request):
    id = str(request.match_info['id'])

    data = await request.json()

    x = {"_id" : id}

    document = await collection_DEVICE.find_one(x)

    if str(type(document)) == "<class 'NoneType'>":
        return web.json_response({'error': 'Device not found'}, status=404)

    await collection_DEVICE.update_one({'_id': id}, {'$set': data})

    new_document = await collection_DEVICE.find_one(x)

    return web.json_response(new_document)


# curl -X DELETE http://163.172.130.246:8080/devices/test
async def remove_device(request):
    id = str(request.match_info['id'])

    x = {"_id" : id}

    document = await collection_DEVICE.find_one(x)

    if str(type(document)) == "<class 'NoneType'>":
        return web.json_response({'error': 'Device not found'}, status=404)

    await collection_DEVICE.delete_many(x)

    return web.Response(status=204)


async def get_all_msg(request):
    return web.json_response([
        document async for document in collection_MSG.find().sort("_id", -1)
    ])


async def get_multiple_msg(request):
    owner = str(request.match_info['owner'])

    x = {"owner" : owner, "payed" : True}

    return web.json_response([
        document async for document in collection_MSG.find(x).sort("_id", -1)
    ])



# curl -X DELETE http://163.172.130.246:8080/msg
async def remove_all_msg(request):
    await collection_MSG.delete_many({})
    return web.Response(status=204)


# curl -X POST -d '{"pType": "DataConfirmedUp", "counter": "0", "deviceAdd": "0x1145f03880d8a975", "payload": "ciao"}' http://163.172.130.246:8080/msg
async def create_msg(request):
    data = await request.json()

    if 'pType' not in data:
        return web.json_response({'error': '"pType" is a required field'}, status=404)

    if 'counter' not in data:
        return web.json_response({'error': '"counter" is a required field'}, status=404)

    if 'deviceAdd' not in data:
        return web.json_response({'error': '"deviceAdd" is a required field'}, status=404)
  
    if 'payload' not in data:
        return web.json_response({'error': '"payload" is a required field'}, status=404)
    payload = data['payload']
    if not isinstance(payload, str) or not len(payload):
        return web.json_response({'error': '"payload" must be a string with at least one character'}, status=404)
    
    id = str(time.time())
    data['_id'] = id
    date = str(datetime.datetime.now().strftime('%d-%m-%Y_%H:%M:%S'))
    data['date'] = date
    result = await collection_MSG.insert_one(data)
    #return web.Response(text="Added successfuly", status=204)
    return web.json_response({'success': 'Added successfuly'})


async def get_one_msg(request):
    id = str(request.match_info['id'])

    x = {"_id" : id}

    document = await collection_MSG.find_one(x)

    if str(type(document)) == "<class 'NoneType'>":
        return web.json_response({'error': 'Msg not found'}, status=404)

    return web.json_response(document)


# curl -X PATCH -d '{"payload":"salut"}' http://163.172.130.246:8080/msg/25-04-2021.10:47:53
async def update_msg(request):
    id = str(request.match_info['id'])

    data = await request.json()

    x = {"_id" : id}

    document = await collection_MSG.find_one(x)

    if str(type(document)) == "<class 'NoneType'>":
        return web.json_response({'error': 'Device not found'}, status=404)

    await collection_MSG.update_one({'_id': id}, {'$set': data})

    new_document = await collection_MSG.find_one(x)

    return web.json_response(new_document)


# curl -X DELETE http://163.172.130.246:8080/msg/25-04-2021.10:47:53
async def remove_msg(request):
    id = str(request.match_info['id'])

    x = {"_id" : id}

    document = await collection_MSG.find_one(x)

    if str(type(document)) == "<class 'NoneType'>":
        return web.json_response({'error': 'Msg not found'}, status=404)

    await collection_MSG.delete_many(x)

    return web.Response(status=204)


async def get_last_msg(deviceAdd):
    x = {"deviceAdd" : deviceAdd, "payed" : True}

    document = await collection_MSG.find_one(x, sort=[('counter', -1)])
    return document


async def get_all_down(request):
    return web.json_response([
        document async for document in collection_DOWN.find().sort("_id", -1)
    ])


# curl -X DELETE http://163.172.130.246:8080/msg
async def remove_all_down(request):
    await collection_DOWN.delete_many({})
    return web.Response(status=204)


# curl -X POST -d '{"deviceAdd": "0x1145f03880d8a975", "payload": "ciao"}' http://163.172.130.246:8080/down
async def create_down(request):
    data = await request.json()

    if 'deviceAdd' not in data:
        return web.json_response({'error': '"deviceAdd" is a required field'}, status=404)
    deviceAdd = data['deviceAdd']
  
    if 'payload' not in data:
        return web.json_response({'error': '"payload" is a required field'}, status=404)
    payload = data['payload']
    if not isinstance(payload, str) or not len(payload):
        return web.json_response({'error': '"payload" must be a string with at least one character'}, status=404)
    
    id = str(time.time())
    data['_id'] = id
    date = str(datetime.datetime.now().strftime('%d-%m-%Y_%H:%M:%S'))
    data['date'] = date
    data['payed'] = False
    result = await collection_DOWN.insert_one(data)
    #return web.Response(text="Added successfuly", status=204)
    return web.json_response({'success': 'Added successfuly'})


async def get_one_down(request):
    id = str(request.match_info['id'])

    x = {"_id" : id}

    document = await collection_DOWN.find_one(x)

    if str(type(document)) == "<class 'NoneType'>":
        return web.json_response({'error': 'Msg not found'}, status=404)

    return web.json_response(document)


async def get_one_down_f(deviceAdd):
    x = {"deviceAdd" : deviceAdd, "payed" : False}

    document = await collection_DOWN.find_one(x, sort=[('_id', 1)])

    return document


# curl -X PATCH -d '{"payload":"salut"}' http://163.172.130.246:8080/msg/25-04-2021.10:47:53
async def update_down(request):
    id = str(request.match_info['id'])

    data = await request.json()

    x = {"_id" : id}

    document = await collection_DOWN.find_one(x)

    if str(type(document)) == "<class 'NoneType'>":
        return web.json_response({'error': 'Device not found'}, status=404)

    await collection_DOWN.update_one({'_id': id}, {'$set': data})

    new_document = await collection_DOWN.find_one(x)

    return web.json_response(new_document)


# curl -X DELETE http://163.172.130.246:8080/msg/25-04-2021.10:47:53
async def remove_down(request):
    id = str(request.match_info['id'])

    x = {"_id" : id}

    document = await collection_DOWN.find_one(x)

    if str(type(document)) == "<class 'NoneType'>":
        return web.json_response({'error': 'Msg not found'}, status=404)

    await collection_DOWN.delete_many(x)

    return web.Response(status=204)


async def pay_down(id) :
    data = {"payed" : True}
    x = {"_id" : id}

    document = await collection_DOWN.find_one(x)

    if document != None :
        await collection_DOWN.update_one({'_id': id}, {'$set': data})


async def generate_device(request):
    deviceAdd = await generate_deviceAdd()
    # privkey, pubkey = await generate_key_pair()
    privkey, x_pub, y_pub = await generate_key_pair()
    ts = str(time.time())
    date = str(datetime.datetime.now().strftime('%d-%m-%Y_%H:%M:%S'))
    # responded = {"_id" : deviceAdd, "deviceAdd": deviceAdd, "x_pub": x_pub, "y_pub": y_pub, "privkey": privkey, "ts": ts, "date": date, "name": deviceAdd, "serverAdd": ADDR_int, "port": PORT}
    # stored = {"_id" : deviceAdd, "deviceAdd": deviceAdd, "x_pub": x_pub, "y_pub": y_pub, "ts": ts, "date": date, "name": deviceAdd, "serverAdd": ADDR_int, "port": PORT}
    responded = {"_id" : deviceAdd, "deviceAdd": deviceAdd, "x_pub": x_pub, "y_pub": y_pub, "privkey": privkey, "ts": ts, "date": date, "name": deviceAdd, "serverAdd": ADDR_int, "port": PORT}
    stored = {"_id" : deviceAdd, "deviceAdd": deviceAdd, "x_pub": x_pub, "y_pub": y_pub, "ts": ts, "date": date, "name": deviceAdd, "port": PORT}

    document = await collection_DEVICE.find_one(stored)

    if str(type(document)) == "<class 'NoneType'>":
        await collection_DEVICE.insert_one(stored)
        return web.json_response(responded)
    else :
        return web.json_response({'error': 'Device already created'}, status=404)


async def get_pubkey(id):
    x = {"_id" : id}

    document = await collection_DEVICE.find_one(x)

    if str(type(document)) == "<class 'NoneType'>":
        return "error"

    return document['x_pub'], document['y_pub']


async def get_address(request):
    # get all the unpaid messages
    owner = str(request.match_info['owner'])

    x = {"owner" : owner, "payed" : False}

    # {add1 : 4, add2 : 1}
    address = {}
    counter = 0

    async for document in collection_MSG.find(x) :
        counter = counter + 1
        gateway = document['gateway']
        address[gateway] = address.get(gateway, 0) + 1
    
    address['total'] = counter

    print(address)
    return web.json_response(address)


async def update_payed(request):
    print("update")
    owner = str(request.match_info['owner'])
    gateway = str(request.match_info['gateway'])
    print(owner)
    print(gateway)

    x = {"owner" : owner, "gateway": gateway}
    # data = {"payed": True}
    data = await request.json()
    print(data)

    test = await collection_MSG.update_many(x, {'$set': data})
    print(test.modified_count, "documents updated")

    return web.Response(status=204)


async def get_one_gateway(gateway_add):
    x = {"_id" : gateway_add}
    document = await collection_GATEWAY.find_one(x)
    return document


async def delete_one_gateway(gateway_add):
    x = {"_id" : gateway_add}
    await collection_GATEWAY.delete_many(x)


async def create_gateway(gateway_add, contract_add, amount_payed, amount_creation, expiration):
    # check unique id
    x = {"_id" : gateway_add}
    document = await collection_GATEWAY.find_one(x)
    if document == None :
        data = {"_id" : gateway_add, "contract": contract_add, "amount_payed": amount_payed, "amount_creation": amount_creation, "expiration": expiration}
        result = await collection_GATEWAY.insert_one(data)


async def update_gateway(gateway_add, new_amount):
    x = {"_id" : gateway_add}
    data = {"amount_payed" : new_amount}

    document = await collection_GATEWAY.find_one(x)

    if document != None :
        await collection_GATEWAY.update_one(x, {'$set': data})


async def process(message, hash_structure, gateway, down):
    #print("processing :", message)

    # decode message
        # get the source
        # get pub key of device (one piece or separate x and y?) --> one piece
            # --> try to store the pub key object in the db
                # possible to store pub key object in smart contract
                    # do not think so --> need a way to export pub key
        # check signature using pub key of device
        # generate symetric key
        # decrypt
        # analyze content

    # gateway = message[-42:]
    # gateway = gateway.decode("utf-8")
    # print("gateway :", gateway)

    # message = message[:-42]
    # print("message :", message)

    header = await get_header(message)
    pType = header[0]
    counter = header[1]
    deviceAdd = header[2]
    print("header :", header)
    print("deviceAdd :", deviceAdd)
    print("counter :", counter)

    x_pub, y_pub = await get_pubkey(deviceAdd)
    # print("pubkey :", pubkey)

    if x_pub != "error" and y_pub != "error":

        valid = await check_signature(message, x_pub, y_pub)

        if valid != False :
            print("Signature is correct")
            print(valid)

            to_be_signed = valid._sig_structure
            message_hash = hashlib.sha256(to_be_signed).digest()
            print(to_be_signed)
            print(message_hash)

            if hash_structure == message_hash :
                print("Hash is correct")

                key = await generate_key_sym(serialized_private_server, x_pub, y_pub)
                decrypted = await decrypt(message, key)
                print("Payload :", decrypted) 

                # store decrypted message into db + header + owner
                id = str(time.time())
                date = str(datetime.datetime.now().strftime('%d-%m-%Y_%H:%M:%S'))

                device = await contract_lora.functions.devices(int(deviceAdd, 0)).call()
                # print(device)
                ipv4Addr = device[0]
                ipv6Addr = device[1]
                domain = device[2]
                ipv4Port = device[3]
                ipv6Port = device[4]
                domainPort = device[5]
                owner = device[6]
                # not necessary to do all that just for the owner --> ADDR

                x = {"_id" : id, "date" : date, "owner" : owner, "gateway" : gateway, "payed" : automatic_pay, "pType" : pType, "counter" : counter, "deviceAdd" : deviceAdd, "payload" : decrypted}
                await collection_MSG.insert_one(x)

                #print("pType :", pType)

                # return response to send back if no previous down sent by user
                if down == b"down_message" and automatic_response == True and payment_method != 'OMG':
                    if pType == "DataConfirmedUp":
                        counter = await read_increment_counter()
                        header_respond = ["ACKDown", counter, ADDR]
                        # can insert a function to generate some payload !
                        payload_respond = "Received"
                        encrypted = await encrypt(header_respond, payload_respond, key)

                        packet = await sign(encrypted, serialized_private_server)

                        return packet
                    
                    else :
                        print("no DataConfirmedUp")
                        return b"nothing"    
                
                else :
                    print("nothing to send")
                    return b"nothing"

            else :
                print("hash structure does not match")
                return b"error3 : hash structure does not match"
        else :
            print("signature is not correct")
            return b"error2 : signature is not correct"
    else: 
        print("device not registered")
        return b"error1 : device not registered"


async def down_message(deviceAdd, x_pub, y_pub):
    key = await generate_key_sym(serialized_private_server, x_pub, y_pub)
    payload_respond = await get_one_down_f(deviceAdd)
    if payload_respond != None :
        print("payload_respond :", payload_respond['payload'])
        counter = await read_increment_counter()
        header_respond = ["DataUnconfirmedDown", counter, ADDR]
        encrypted = await encrypt(header_respond, payload_respond['payload'], key)
        packet = await sign(encrypted, serialized_private_server)
        return packet, payload_respond["_id"]
    else :
        return b"down_message", None



# async def process_hash(hash_structure, signature, deviceAdd, counter_header, gateway_add):
#     # check signature with hash_structure
#     # packet = packet.split(",")
#     # deviceAdd = packet[0]
#     # counter_header = packet[1]
#     # gateway_add = packet[2]
#     pubkey = await get_pubkey(deviceAdd)
#     verified = verify_signature_hash(pubkey, hash_structure, signature)
#     print("verified :", verified)
#     if verified :
#         # check if there is a down_message to send back
#         down, down_id = await down_message(deviceAdd, counter_header, pubkey)
#         if down != b"down_message":
#             price = message_price * 2

#         # pay for the message
#         # print("pay")
#         if payment_method == 'OMG' :
#             # put metadata at the begining. If put deviceAdd, problem on payment.js. If put counter_header, the 0 is not considered a 0 on the gateway side
#             metadata = "metadata" + ',' + counter_header + ',' + deviceAdd
#             body = {'receiverAdd': gateway_add, 'amount': price, 'metadata' : metadata}
#             body = json.dumps(body)
#             # print(body)
#             request = await requests.post('http://163.172.130.246:3000/payment/', data=body, headers= { 'Content-Type': 'application/json'})
#             payment_hash = request.text
#             print("payment hash :", payment_hash)
#             response = payment_method + ',' + payment_hash
#             # mark down as payed
#             if down != b"down_message":
#                 await pay_down(down_id)

#             return response, down
        
#         if payment_method == 'MPC' :
#             # verifies that gateway is already stored in GATEWAY DB
#             gateway_document = await get_one_gateway(gateway_add)
#             print("gateway_document :", gateway_document)
#             if gateway_document == None :
#                 # deploy smart contract 
#                 amount_creation = 100 * price
#                 # amount_creation = 0
#                 duration = 30 * 24 * 60 * 60
#                 epoch_time = int(time.time())
#                 expiration = epoch_time + duration
#                 body = {'receiverAdd': gateway_add, 'amount': amount_creation, 'duration' : duration}
#                 body = json.dumps(body)
#                 request = await requests.post('http://163.172.130.246:3000/deploy/', data=body, headers= { 'Content-Type': 'application/json'})
#                 contract_add = request.text
#                 # store gateway_add, contract_add, amount_creation, expiration
#                 amount_payed = 0
#                 await create_gateway(gateway_add, contract_add, amount_payed, amount_creation, expiration)
#             else :
#                 contract_add = gateway_document['contract']
#                 amount_payed = gateway_document['amount_payed']
#                 amount_creation = gateway_document['amount_creation']
            
#             # pay for the message --> amount_payed + price
#             new_amount = amount_payed + price
#             print("new_amount :", new_amount)
#             if amount_creation > new_amount :

#                 body = {'contractAddress': contract_add, 'amount': new_amount}
#                 body = json.dumps(body)
#                 request = await requests.post('http://163.172.130.246:3000/signPayment/', data=body, headers= { 'Content-Type': 'application/json'})
#                 signature = request.text

#                 # update amount in GATEWAY DB
#                 await update_gateway(gateway_add, new_amount)

#                 # return response --> MPC,signature,contract_add,price
#                 response = payment_method + ',' + signature + ',' + contract_add + ',' + str(price)

#                 # mark down as payed
#                 if down != b"down_message":
#                     await pay_down(down_id)

#             else :
#                 response = "error5 : not enough money in the smart contract"
#                 print(response)
                
#                 # deploy new smart contract and update DB

#             return response, down

    
#     else :
#         return "Signature does not match the hash"


async def close_contract(gateway_add):
    # verifies that the smart contract has been closed
    # get the contract_add
    gateway_document = await get_one_gateway(gateway_add)
    contract_add = gateway_document['contract']
    # wait a moment
    await asyncio.sleep(20)
    balance = await web3.eth.getBalance(contract_add)
    # print("balance :", balance)
    if balance == 0:
        # delete the gateway
        await delete_one_gateway(gateway_add)



async def verify_hash(hash_structure, signature, deviceAdd):
    try :
        x_pub, y_pub = await get_pubkey(deviceAdd)
        verified = verify_signature_hash(x_pub, y_pub, hash_structure, signature)
        print("verified :", verified)

        return verified

    except Exception :
        return False


async def check_if_down(deviceAdd):
    x_pub, y_pub = await get_pubkey(deviceAdd)

    # check if there is a down_message to send back
    down = b"down_message"
    down_id = None
    price = message_price

    down, down_id = await down_message(deviceAdd, x_pub, y_pub)
    if down != b"down_message":
        price = message_price * 2
    
    return down, down_id, price


async def omg_pay(deviceAdd, counter_header, gateway_add, price):
    # put metadata at the begining. If put deviceAdd, problem on payment.js. If put counter_header, the 0 is not considered a 0 on the gateway side
    metadata = "metadata" + ',' + counter_header + ',' + deviceAdd
    body = {'receiverAdd': gateway_add, 'amount': price, 'metadata' : metadata}
    body = json.dumps(body)
    # print(body)
    request = await requests.post('http://163.172.130.246:3000/payment/', data=body, headers= { 'Content-Type': 'application/json'})
    payment_hash = request.text
    print("payment hash :", payment_hash)
    response = payment_method + ',' + payment_hash

    return response


async def mpc_pay(deviceAdd, counter_header, gateway_add, price):
    # verifies that gateway is already stored in GATEWAY DB
    gateway_document = await get_one_gateway(gateway_add)
    print("gateway_document :", gateway_document)
    if gateway_document == None :
        # deploy smart contract 
        amount_creation = 100 * price
        # amount_creation = 0
        duration = 30 * 24 * 60 * 60
        epoch_time = int(time.time())
        expiration = epoch_time + duration
        body = {'receiverAdd': gateway_add, 'amount': amount_creation, 'duration' : duration}
        body = json.dumps(body)
        request = await requests.post('http://163.172.130.246:3000/deploy/', data=body, headers= { 'Content-Type': 'application/json'})
        contract_add = request.text
        # store gateway_add, contract_add, amount_creation, expiration
        amount_payed = 0
        await create_gateway(gateway_add, contract_add, amount_payed, amount_creation, expiration)
    else :
        contract_add = gateway_document['contract']
        amount_payed = gateway_document['amount_payed']
        amount_creation = gateway_document['amount_creation']
    
    # pay for the message --> amount_payed + price
    new_amount = amount_payed + price
    print("new_amount :", new_amount)
    if amount_creation > new_amount :

        body = {'contractAddress': contract_add, 'amount': new_amount}
        body = json.dumps(body)
        request = await requests.post('http://163.172.130.246:3000/signPayment/', data=body, headers= { 'Content-Type': 'application/json'})
        signature = request.text

        # update amount in GATEWAY DB
        await update_gateway(gateway_add, new_amount)

        # return respone --> MPC,signature,contract_add,price
        response = payment_method + ',' + signature + ',' + contract_add + ',' + str(price)

    else :
        response = "error5 : not enough money in the smart contract"
        print(response)
        
        # deploy new smart contract and update DB

    return response



class EchoServerProtocol:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        loop = asyncio.get_event_loop()
        loop.create_task(self.datagram_received_async(data, addr))        

    async def datagram_received_async(self, data, addr):
        #message = data.decode()
        message = data
        print('Received %r from %s' % (message, addr))
        if type(message) == bytes :
            # try :
            #     response = await process(message)
            # except Exception as e:
            #     response = b'error, corrupted data'
            # response = await process(message)
            response = b"success"
        else :
            response = b'error, did not receive bytes'
        #await asyncio.sleep(5)
        print('Send %r to %s' % (response, addr))
        self.transport.sendto(response, addr)


async def start_datagram_proxy(add, port):
    loop = asyncio.get_event_loop()
    return await loop.create_datagram_endpoint(
        lambda: EchoServerProtocol(),
        local_addr=(add, port))


async def ws(websocket, path):
    while True :
        try:
            hash_structure = await websocket.recv()
            signature = await websocket.recv()
            packet = await websocket.recv()
            # print(f"< {hash_structure} {type(hash_structure)}")
            # print(f"< {signature} {type(signature)}")
            # print(f"< {packet} {type(packet)}")

            packet = packet.split(",")
            deviceAdd = packet[0]
            counter_header = packet[1]
            gateway_add = packet[2]

            # verifies unique counter
            # get last message document from this device

            # verify that counter_header not already registred 
            # get last counter_header for this device in msg DB
            last_msg = await get_last_msg(deviceAdd)
            if last_msg == None :
                last_counter = -1
                last_gateway = gateway_add
            else :
                last_counter = int(last_msg['counter'])
                last_gateway = last_msg['gateway']
            
            if int(counter_header) > last_counter :
            # if 100 > last_counter :
                print("last_counter :", last_counter)
            
                # verify that gateway is the same
                if gateway_add != last_gateway:
                # if "gateway_add" != last_gateway:
                    print("sleep")
                    await asyncio.sleep(10)
                    last_msg = await get_last_msg(deviceAdd)
                    last_counter = int(last_msg['counter'])
                    # if the message has been processed in the meantime
                    if int(counter_header) <= last_counter:
                    # if 0 <= last_counter:
                        raise ValueError

                # if does not match, wait a moment to see if receive the message from the correct gateway,
                # otherwise process this one

                verified = await verify_hash(hash_structure, signature, deviceAdd)

                if verified :

                    down, down_id, price = await check_if_down(deviceAdd)

                    # down, down_id, price = await process_hash(hash_structure, signature, deviceAdd, counter_header, gateway_add)

                    payment_receipt = None
                    if payment_method == 'OMG' :
                        payment_receipt = await omg_pay(deviceAdd, counter_header, gateway_add, price)
                    if payment_method == 'MPC' :
                        payment_receipt = await mpc_pay(deviceAdd, counter_header, gateway_add, price)

                    if "error" not in payment_receipt and payment_receipt != None:

                        if down != b"down_message" :
                            await pay_down(down_id)

                        await websocket.send(payment_receipt)
                        await websocket.send(down)
                        # print(f"> {response}")

                        message = await websocket.recv()

                        if message ==  "error : smart contract closed" :
                            # get the message
                            message = await websocket.recv()
                            await close_contract(gateway_add)

                        if message != "invalid payment":
                            if type(message) == bytes :
                                try :
                                    response = await process(message, hash_structure, gateway_add, down)
                                except Exception as e:
                                    response = b'error, corrupted data'
                                # response = await process(message, hash_structure, gateway_add)
                            else :
                                response = b'error, did not receive bytes message'
                        else :
                            print(message)
                            response = b"payment error"

                        print("response :", response)

                        if down == b"down_message" and response != b"nothing" and b"error" not in response and payment_method != 'OMG':
                            print("send response")

                            # pay for the message if it is actual content
                            payment_receipt = "nothing"
                            print("pay")
                            if payment_method == 'MPC' :
                                payment_receipt = await mpc_pay(deviceAdd, counter_header, gateway_add, message_price)
                            await websocket.send(payment_receipt)
                            await websocket.send(response)
                            success = await websocket.recv()
                            if success == "error : smart contract closed":
                                await close_contract(gateway_add)
                    
                    else :
                        await websocket.send("error : payment error")

                else :
                    await websocket.send("error : invalid signature")

            else :
                await websocket.send("error : message already received")


        except websockets.exceptions.ConnectionClosed as e:
            print(e)
            return

        except ValueError:
            response = "error : message already processed"
            print(response)
            await websocket.send(response)
            # return


app = web.Application()

# Configure default CORS settings.
cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*",
        )
})

cors.add(app.router.add_get('', start))
cors.add(app.router.add_get('/', start))
cors.add(app.router.add_get('/ip', get_addr_server))
cors.add(app.router.add_get('/pubkey', get_server_pubkey))
cors.add(app.router.add_get('/test', test))
cors.add(app.router.add_get('/devices', get_all_devices))
cors.add(app.router.add_get('/devices/', get_all_devices))
cors.add(app.router.add_delete('/devices', remove_all_devices))
cors.add(app.router.add_post('/devices', create_device))
cors.add(app.router.add_get('/devices/{id}', get_one_device))
cors.add(app.router.add_patch('/devices/{id}', update_device))
cors.add(app.router.add_delete('/devices/{id}', remove_device))

cors.add(app.router.add_get('/generate', generate_device))

cors.add(app.router.add_get('/msg', get_all_msg))
cors.add(app.router.add_get('/msg/', get_all_msg))
cors.add(app.router.add_delete('/msg', remove_all_msg))
cors.add(app.router.add_post('/msg', create_msg))
cors.add(app.router.add_get('/msg/{id}', get_one_msg))
cors.add(app.router.add_patch('/msg/{id}', update_msg))
cors.add(app.router.add_delete('/msg/{id}', remove_msg))
cors.add(app.router.add_get('/msgs/{owner}', get_multiple_msg))

cors.add(app.router.add_get('/down', get_all_down))
cors.add(app.router.add_get('/down/', get_all_down))
cors.add(app.router.add_delete('/down', remove_all_down))
cors.add(app.router.add_post('/down', create_down))
cors.add(app.router.add_get('/down/{id}', get_one_down))
cors.add(app.router.add_patch('/down/{id}', update_down))
cors.add(app.router.add_delete('/down/{id}', remove_down))

cors.add(app.router.add_get('/pay/{owner}', get_address))   # get the address of the gateway to pay
cors.add(app.router.add_patch('/pay/{owner}/{gateway}', update_payed))



def main(add=add, port=PORT):
    loop = asyncio.get_event_loop()

    print("Starting UDP server...")
    coro = start_datagram_proxy(add, port)
    transport, _ = loop.run_until_complete(coro)
    print("UDP server is running...")

    print("Starting websocket server...")
    start_server = websockets.serve(ws, "0.0.0.0", 8765)
    loop.run_until_complete(start_server)

    print("Start HTTP server...")
    loop.run_until_complete(web.run_app(app, port=8080))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    print("Closing UDP server...")
    print("Closing HTTP server...")
    transport.close()
    loop.close()


if __name__ == '__main__':
    main()