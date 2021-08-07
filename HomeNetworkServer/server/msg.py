import datetime
import time
from aiohttp import web

async def get_all_msg(request):
    collection_MSG = request.app['collection_MSG']
    return web.json_response([
        document async for document in collection_MSG.find().sort("_id", -1)
    ])


async def get_multiple_msg(request):
    collection_MSG = request.app['collection_MSG']
    owner = str(request.match_info['owner'])

    x = {"owner" : owner, "payed" : True}

    return web.json_response([
        document async for document in collection_MSG.find(x).sort("_id", -1)
    ])


# curl -X DELETE http://163.172.130.246:8080/msg
async def remove_all_msg(request):
    collection_MSG = request.app['collection_MSG']
    await collection_MSG.delete_many({})
    return web.Response(status=204)


# curl -X POST -d '{"pType": "DataConfirmedUp", "counter": "0", "deviceAdd": "0x1145f03880d8a975", "payload": "ciao"}' http://163.172.130.246:8080/msg
async def create_msg(request):
    collection_MSG = request.app['collection_MSG']
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
    return web.json_response({'success': 'Added successfuly'})


async def get_one_msg(request):
    collection_MSG = request.app['collection_MSG']
    id = str(request.match_info['id'])

    x = {"_id" : id}

    document = await collection_MSG.find_one(x)

    if str(type(document)) == "<class 'NoneType'>":
        return web.json_response({'error': 'Msg not found'}, status=404)

    return web.json_response(document)


# curl -X PATCH -d '{"payload":"salut"}' http://163.172.130.246:8080/msg/25-04-2021.10:47:53
async def update_msg(request):
    collection_MSG = request.app['collection_MSG']
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
    collection_MSG = request.app['collection_MSG']
    id = str(request.match_info['id'])

    x = {"_id" : id}

    document = await collection_MSG.find_one(x)

    if str(type(document)) == "<class 'NoneType'>":
        return web.json_response({'error': 'Msg not found'}, status=404)

    await collection_MSG.delete_many(x)

    return web.Response(status=204)


async def get_last_msg(deviceAdd):
    collection_MSG = request.app['collection_MSG']
    x = {"deviceAdd" : deviceAdd, "payed" : True}

    document = await collection_MSG.find_one(x, sort=[('counter', -1)])
    return document


async def get_address(request):
    collection_MSG = request.app['collection_MSG']
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

    return web.json_response(address)


async def update_payed(request):
    collection_MSG = request.app['collection_MSG']
    print("update")
    owner = str(request.match_info['owner'])
    gateway = str(request.match_info['gateway'])
    print(owner)
    print(gateway)

    x = {"owner" : owner, "gateway": gateway}
    data = await request.json()
    print(data)

    test = await collection_MSG.update_many(x, {'$set': data})
    print(test.modified_count, "documents updated")

    return web.Response(status=204)