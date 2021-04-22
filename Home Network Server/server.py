"""UDP server"""
# https://gist.github.com/vxgmichel/b2cf8536363275e735c231caef35a5df
# https://docs.python.org/3/library/asyncio-protocol.html

import json
from bson.objectid import ObjectId

import asyncio
from aiohttp import web
import aiohttp_cors
import motor.motor_asyncio

client = motor.motor_asyncio.AsyncIOMotorClient('mongodb+srv://lora:lora@lora.j8ycs.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')

db = client['lora_db']
collection_DEVICE = db['DEVICE']
collection_MSG = db['MSG']

add = "0.0.0.0"     # localhost does not work ! https://stackoverflow.com/questions/15734219/simple-python-udp-server-trouble-receiving-packets-from-clients-other-than-loca/15734249
port = 9999



async def test(request):
    # id = "hello"
    # x = {"_id" : id}
    # print(f'{x} {type(x)}')
    # await collection_DEVICE.insert_one(x)
    print("test")
    #return web.json_response({'error': 'Todo not found'}, status=404)
    return web.json_response({'success': 'test'})
    #return web.Response(text="Hello world !")


async def get_all_devices(request):
    return web.json_response([
        document async for document in collection_DEVICE.find()
    ])


# curl -X DELETE http://163.172.130.246/devices
async def remove_all_devices(request):
    await collection_DEVICE.delete_many({})
    return web.Response(status=204)


# curl -X POST -d '{"deviceAdd":"deviceAdd", "pubkey":"pubkey"}' http://163.172.130.246/devices
async def create_device(request):
    data = await request.json()

    if 'deviceAdd' not in data:
        return web.json_response({'error': '"deviceAdd" is a required field'})
    deviceAdd = data['deviceAdd']
    if not isinstance(deviceAdd, str) or not len(deviceAdd):
        return web.json_response({'error': '"deviceAdd" must be a string with at least one character'})
    
    if 'pubkey' not in data:
        return web.json_response({'error': '"pubkey" is a required field'})
    pubkey = data['pubkey']
    if not isinstance(pubkey, str) or not len(pubkey):
        return web.json_response({'error': '"pubkey" must be a string with at least one character'})
    
    # check unique id
    x = {"_id" : data['deviceAdd']}
    document = await collection_DEVICE.find_one(x)
    if str(type(document)) == "<class 'NoneType'>":
        data['_id'] = data['deviceAdd']
        result = await collection_DEVICE.insert_one(data)
        # store new device in smart contract
        return web.Response(text="Added successfuly", status=204)
    else :
        return web.json_response({'error': 'Device already registred'}, status=404)


async def get_one_device(request):
    id = str(request.match_info['id'])

    x = {"_id" : id}

    document = await collection_DEVICE.find_one(x)

    if str(type(document)) == "<class 'NoneType'>":
        return web.json_response({'error': 'Device not found'}, status=404)

    return web.json_response(document)


# curl -X PATCH -d '{"deviceAdd":"deviceAdd2", "pubkey":"pubkey2"}' http://163.172.130.246/devices/deviceAdd
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


# curl -X DELETE http://163.172.130.246/devices/test
async def remove_device(request):
    id = str(request.match_info['id'])

    x = {"_id" : id}

    document = await collection_DEVICE.find_one(x)

    if str(type(document)) == "<class 'NoneType'>":
        return web.json_response({'error': 'Device not found'}, status=404)

    await collection_DEVICE.delete_many(x)

    return web.Response(status=204)


class EchoServerProtocol:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        print('Received %r from %s' % (message, addr))
        print('Send %r to %s' % (message, addr))
        self.transport.sendto(data, addr)


async def start_datagram_proxy(add, port):
    loop = asyncio.get_event_loop()
    return await loop.create_datagram_endpoint(
        lambda: EchoServerProtocol(),
        local_addr=(add, port))



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

cors.add(app.router.add_get('', test))
cors.add(app.router.add_get('/devices', get_all_devices))
cors.add(app.router.add_get('/devices/', get_all_devices))
cors.add(app.router.add_delete('/devices', remove_all_devices))
cors.add(app.router.add_post('/devices', create_device))
cors.add(app.router.add_get('/devices/{id}', get_one_device))
cors.add(app.router.add_patch('/devices/{id}', update_device))
cors.add(app.router.add_delete('/devices/{id}', remove_device))



def main(add=add, port=port):
    loop = asyncio.get_event_loop()

    print("Starting UDP server...")
    con = start_datagram_proxy(add, port)
    transport, _ = loop.run_until_complete(con)
    print("UDP server is running...")

    print("Start HTTP server...")
    loop.run_until_complete(web.run_app(app, port=80))

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