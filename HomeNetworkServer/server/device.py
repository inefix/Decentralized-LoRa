import datetime
import time
from aiohttp import web


async def test(request):
    print("test")
    collection_DEVICE = request.app['collection_DEVICE']
    ADDR_int = request.app['ADDR_int']
    PORT = request.app['PORT']

    deviceAdd = "0x1145f03880d8a975"
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
    collection_DEVICE = request.app['collection_DEVICE']
    return web.json_response([
        document async for document in collection_DEVICE.find().sort("ts", -1)
    ])


# curl -X DELETE http://163.172.130.246:8080/devices
async def remove_all_devices(request):
    collection_DEVICE = request.app['collection_DEVICE']
    await collection_DEVICE.delete_many({})
    return web.Response(status=204)


# curl -X POST -d '{"deviceAdd":"deviceAdd", "pubkey":"pubkey"}' http://163.172.130.246/devices
async def create_device(request):
    collection_DEVICE = request.app['collection_DEVICE']
    ADDR_int = request.app['ADDR_int']
    PORT = request.app['PORT']
    data = await request.json()

    if 'deviceAdd' not in data:
        return web.json_response({'error': '"deviceAdd" is a required field'}, status=404)
    deviceAdd = data['deviceAdd']
    if not isinstance(deviceAdd, str) or not len(deviceAdd):
        return web.json_response({'error': '"deviceAdd" must be a string with at least one character'}, status=404)
    
    if 'x_pub' not in data:
        return web.json_response({'error': '"x_pub" is a required field'}, status=404)
    x_pub = data['x_pub']
    if not isinstance(x_pub, str) or not len(x_pub):
        return web.json_response({'error': '"x_pub" must be a string with at least one character'}, status=404)

    if 'y_pub' not in data:
        return web.json_response({'error': '"y_pub" is a required field'}, status=404)
    y_pub = data['y_pub']
    if not isinstance(y_pub, str) or not len(y_pub):
        return web.json_response({'error': '"y_pub" must be a string with at least one character'}, status=404)
    
    # check unique id
    x = {"_id" : data['deviceAdd']}
    document = await collection_DEVICE.find_one(x)
    if str(type(document)) == "<class 'NoneType'>":
        data['_id'] = data['deviceAdd']
        data['ts'] = str(time.time())
        data['date'] = str(datetime.datetime.now().strftime('%d-%m-%Y_%H:%M:%S'))
        data["port"] = PORT
        result = await collection_DEVICE.insert_one(data)
        # store new device in smart contract
        #return web.Response(text="Added successfuly", status=204)
        data["serverAdd"] = ADDR_int
        return web.json_response(data)
    else :
        return web.json_response({'error': 'Device already registred'}, status=404)


async def get_one_device(request):
    collection_DEVICE = request.app['collection_DEVICE']
    id = str(request.match_info['id'])

    x = {"_id" : id}

    document = await collection_DEVICE.find_one(x)

    if str(type(document)) == "<class 'NoneType'>":
        return web.json_response({'error': 'Device not found'}, status=404)

    return web.json_response(document)


# curl -X PATCH -d '{"deviceAdd":"deviceAdd2", "pubkey":"pubkey2"}' http://163.172.130.246:8080/devices/deviceAdd
async def update_device(request):
    collection_DEVICE = request.app['collection_DEVICE']
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
    collection_DEVICE = request.app['collection_DEVICE']
    id = str(request.match_info['id'])

    x = {"_id" : id}

    document = await collection_DEVICE.find_one(x)

    if str(type(document)) == "<class 'NoneType'>":
        return web.json_response({'error': 'Device not found'}, status=404)

    await collection_DEVICE.delete_many(x)

    return web.Response(status=204)


async def generate_device(request):
    collection_DEVICE = request.app['collection_DEVICE']
    ADDR_int = request.app['ADDR_int']
    PORT = request.app['PORT']
    deviceAdd = await generate_deviceAdd()
    private_value, x_pub, y_pub = await generate_key_pair()
    ts = str(time.time())
    date = str(datetime.datetime.now().strftime('%d-%m-%Y_%H:%M:%S'))
    responded = {"_id" : deviceAdd, "deviceAdd": deviceAdd, "x_pub": x_pub, "y_pub": y_pub, "private_value": private_value, "ts": ts, "date": date, "name": deviceAdd, "serverAdd": ADDR_int, "port": PORT}
    stored = {"_id" : deviceAdd, "deviceAdd": deviceAdd, "x_pub": x_pub, "y_pub": y_pub, "ts": ts, "date": date, "name": deviceAdd, "port": PORT}

    document = await collection_DEVICE.find_one(stored)

    if str(type(document)) == "<class 'NoneType'>":
        await collection_DEVICE.insert_one(stored)
        return web.json_response(responded)
    else :
        return web.json_response({'error': 'Device already created'}, status=404)


async def get_pubkey(id):
    collection_DEVICE = request.app['collection_DEVICE']
    x = {"_id" : id}

    document = await collection_DEVICE.find_one(x)

    if str(type(document)) == "<class 'NoneType'>":
        return "error"

    return document['x_pub'], document['y_pub']