"""UDP server"""
# https://gist.github.com/vxgmichel/b2cf8536363275e735c231caef35a5df
# https://docs.python.org/3/library/asyncio-protocol.html

import json
import datetime
import time
import ipaddress

import asyncio
import websockets
from aiohttp import web
import aiohttp_cors
import motor.motor_asyncio

from lora import generate_deviceAdd, generate_key_pair, get_header, check_signature, generate_key_sym, decrypt, encrypt, sign, verify_signature_hash

import web3s
import requests_async as requests

ADDR = "163.172.130.246"
PORT = 9999

if ADDR.count(":") > 1:
    print("IPv6")
    ADDR = int(ipaddress.IPv6Address(ADDR))
    # print(ADDR)
elif ADDR[0].isdigit() and ADDR[len(ADDR)-1].isdigit() :
    print("IPv4")
    ADDR = int(ipaddress.IPv4Address(ADDR))
    print(ADDR)
else :
    print("domain")

# ADDR = str(ipaddress.IPv4Address(ADDR))
# print(ADDR)

client = motor.motor_asyncio.AsyncIOMotorClient('mongodb+srv://lora:lora@lora.j8ycs.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')

db = client['lora_db']
collection_DEVICE = db['DEVICE']
collection_MSG = db['MSG']


infuria_url = "https://ropsten.infura.io/v3/4d24fe93ef67480f97be53ccad7e43d6"
web3 = web3s.Web3s(web3s.Web3s.HTTPProvider(infuria_url))

abi_lora = json.loads('[{"inputs": [{"internalType": "uint64","name": "","type": "uint64"}],"name": "devices","outputs": [{"internalType": "uint32","name": "ipv4Addr","type": "uint32"},{"internalType": "uint128","name": "ipv6Addr","type": "uint128"},{"internalType": "string","name": "domain","type": "string"},{"internalType": "uint16","name": "ipv4Port","type": "uint16"},{"internalType": "uint16","name": "ipv6Port","type": "uint16"},{"internalType": "uint16","name": "domainPort","type": "uint16"},{"internalType": "address","name": "owner","type": "address"}],"stateMutability": "view","type": "function","constant": true},{"inputs": [{"internalType": "uint64","name": "loraAddr","type": "uint64"},{"internalType": "uint32","name": "server","type": "uint32"},{"internalType": "uint16","name": "port","type": "uint16"}],"name": "registerIpv4","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [{"internalType": "uint64","name": "loraAddr","type": "uint64"},{"internalType": "uint128","name": "server","type": "uint128"},{"internalType": "uint16","name": "port","type": "uint16"}],"name": "registerIpv6","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [{"internalType": "uint64","name": "loraAddr","type": "uint64"},{"internalType": "string","name": "domain","type": "string"},{"internalType": "uint16","name": "port","type": "uint16"}],"name": "registerDomain","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [{"internalType": "uint64","name": "loraAddr","type": "uint64"},{"internalType": "uint32","name": "server","type": "uint32"},{"internalType": "uint16","name": "port","type": "uint16"}],"name": "updateIpv4","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [{"internalType": "uint64","name": "loraAddr","type": "uint64"},{"internalType": "uint128","name": "server","type": "uint128"},{"internalType": "uint16","name": "port","type": "uint16"}],"name": "updateIpv6","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [{"internalType": "uint64","name": "loraAddr","type": "uint64"},{"internalType": "string","name": "domain","type": "string"},{"internalType": "uint16","name": "port","type": "uint16"}],"name": "updateDomain","outputs": [],"stateMutability": "nonpayable","type": "function"}]')
contract_addr_lora = "0xCd862ceF6D5EDd348854e4a280b62d51F7F62a65"
contract_lora = web3.eth.contract(contract_addr_lora, abi=abi_lora)


add = "0.0.0.0"     # localhost does not work ! https://stackoverflow.com/questions/15734219/simple-python-udp-server-trouble-receiving-packets-from-clients-other-than-loca/15734249

serialized_private_server = b'-----BEGIN PRIVATE KEY-----\nMIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQg5hsInzp4UhjgehRh\nA+55y9GGR7dai4Kky4LCYpE+jFGhRANCAATCl2kTYWbuwSmeG11WxI3heHo/cvDo\n7lwUNX71t4/G6nZmsAwwgkjPgkyOIk3Y/8xMzRNiyCLy6oL1sB954bSa\n-----END PRIVATE KEY-----\n'
serialized_public_server = b'-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEwpdpE2Fm7sEpnhtdVsSN4Xh6P3Lw\n6O5cFDV+9bePxup2ZrAMMIJIz4JMjiJN2P/MTM0TYsgi8uqC9bAfeeG0mg==\n-----END PUBLIC KEY-----\n'

serverAdd = "163.172.130.246"

async def start(request):
    print("Server started")
    return web.json_response({'success': 'Server started'})

async def test(request):
    print("test")

    deviceAdd = "0x1145f03880d8a975"
    pubkey = b'-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEZDhmwCVlGBcPJOj7AbIzP9fvFC6q\n4JqowSK0G5BmPQzU3WQ3EDrbzoPHV4jzduZ7uKt/zHWu6TMr0gkgdyOybw==\n-----END PUBLIC KEY-----\n'.decode("utf-8")
    ts = str(time.time())
    date = str(datetime.datetime.now().strftime('%d-%m-%Y_%H:%M:%S'))
    x = {"_id" : deviceAdd, "deviceAdd": deviceAdd, "pubkey": pubkey, "ts": ts, "date": date, "name": "test", "serverAdd": ADDR, "port": PORT}

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


# curl -X POST -d '{"header": {"pType": "DataConfirmedUp", "counter": "0", "deviceAdd": "0x1145f03880d8a975"}, "payload": "ciao"}' http://163.172.130.246:8080/msg
async def create_msg(request):
    data = await request.json()

    if 'header' not in data:
        return web.json_response({'error': '"header" is a required field'}, status=404)
    header = data['header']
  
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


async def generate_device(request):
    deviceAdd = await generate_deviceAdd()
    privkey, pubkey = await generate_key_pair()
    ts = str(time.time())
    date = str(datetime.datetime.now().strftime('%d-%m-%Y_%H:%M:%S'))
    responded = {"_id" : deviceAdd, "deviceAdd": deviceAdd, "pubkey": pubkey, "privkey": privkey, "ts": ts, "date": date, "name": deviceAdd, "serverAdd": ADDR, "port": PORT}
    stored = {"_id" : deviceAdd, "deviceAdd": deviceAdd, "pubkey": pubkey, "ts": ts, "date": date, "name": deviceAdd, "serverAdd": ADDR, "port": PORT}

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

    return document['pubkey']


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



async def process(message):
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

    pubkey = await get_pubkey(deviceAdd)
    print("pubkey :", pubkey)

    if pubkey != "error":

        signature = await check_signature(message, pubkey)

        if signature :
            print("Signature is correct")
            key = await generate_key_sym(serialized_private_server, pubkey)
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

            # x = {"_id" : id, "date" : date, "owner" : owner, "gateway" : gateway, "payed" : False, "header" : {"pType" : pType, "counter" : counter, "deviceAdd" : deviceAdd}, "payload" : decrypted}
            x = {"_id" : id, "date" : date, "owner" : owner, "payed" : False, "header" : {"pType" : pType, "counter" : counter, "deviceAdd" : deviceAdd}, "payload" : decrypted}
            await collection_MSG.insert_one(x)

            #print("pType :", pType)

            # return response to send back
            if pType == "DataConfirmedUp":
                header_respond = ["ACKDown", int(counter)+1, serverAdd]
                payload_respond = "Received"
                encrypted = await encrypt(header_respond, payload_respond, key)

                packet = await sign(encrypted, serialized_private_server)

                return packet
        else :
            print("Signature is not correct")
            return b"Signature is not correct"
    else: 
        print("Device not registered")
        return b"Device not registered"


async def process_from_gateway(hash_structure, signature, packet):
    # check signature with hash_structure
    packet = packet.split(",")
    deviceAdd = packet[0]
    counter_header = packet[1]
    gateway_add = packet[2]
    pubkey = await get_pubkey(deviceAdd)
    verified = verify_signature_hash(pubkey, hash_structure, signature)
    print("verified :", verified)
    if verified :
        # pay for the message
        print("pay")
        # put metadata at the begining. If put deviceAdd, problem on payment.js. If put counter_header, the 0 is not considered a 0 on the gateway side
        metadata = "metadata" + ',' + counter_header + ',' + deviceAdd
        body = {'receiverAdd': gateway_add, 'amount': 100, 'metadata' : metadata}
        body = json.dumps(body)
        # print(body)
        response = await requests.post('http://163.172.130.246:3000/payment/', data=body, headers= { 'Content-Type': 'application/json'})
        response = response.text
        print("payment hash :", response)
        return response
    
    else :
        return "Signature does not match the hash"




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
            response = await process(message)
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
            print(f"< {hash_structure} {type(hash_structure)}")
            print(f"< {signature} {type(signature)}")
            print(f"< {packet} {type(packet)}")

            try :
                response = await process_from_gateway(hash_structure, signature, packet)
            except Exception as e:
                response = b'error, corrupted data'

            await websocket.send(response)
            # print(f"> {response}")

            message = await websocket.recv()
            if type(message) == bytes :
                # try :
                #     response = await process(message)
                # except Exception as e:
                #     response = b'error, corrupted data'
                response = await process(message)
            else :
                response = b'error, did not receive bytes message'


        except websockets.exceptions.ConnectionClosed as e:
            print("Error : %s" % (e))
            return


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