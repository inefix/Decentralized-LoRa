import datetime
import time
from aiohttp import web

async def get_all_down(request):
    collection_DOWN = request.app['collection_DOWN']
    return web.json_response([
        document async for document in collection_DOWN.find().sort("_id", -1)
    ])


# curl -X DELETE http://163.172.130.246:8080/msg
async def remove_all_down(request):
    collection_DOWN = request.app['collection_DOWN']
    await collection_DOWN.delete_many({})
    return web.Response(status=204)


# curl -X POST -d '{"deviceAdd": "0x1145f03880d8a975", "payload": "ciao"}' http://163.172.130.246:8080/down
async def create_down(request):
    collection_DOWN = request.app['collection_DOWN']
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
    return web.json_response({'success': 'Added successfuly'})


async def get_one_down(request):
    collection_DOWN = request.app['collection_DOWN']
    id = str(request.match_info['id'])

    x = {"_id" : id}

    document = await collection_DOWN.find_one(x)

    if str(type(document)) == "<class 'NoneType'>":
        return web.json_response({'error': 'Msg not found'}, status=404)

    return web.json_response(document)


async def get_one_down_f(deviceAdd, collection_DOWN):
    x = {"deviceAdd" : deviceAdd, "payed" : False}

    document = await collection_DOWN.find_one(x, sort=[('_id', 1)])

    return document


# curl -X PATCH -d '{"payload":"salut"}' http://163.172.130.246:8080/msg/25-04-2021.10:47:53
async def update_down(request):
    collection_DOWN = request.app['collection_DOWN']
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
    collection_DOWN = request.app['collection_DOWN']
    id = str(request.match_info['id'])

    x = {"_id" : id}

    document = await collection_DOWN.find_one(x)

    if str(type(document)) == "<class 'NoneType'>":
        return web.json_response({'error': 'Msg not found'}, status=404)

    await collection_DOWN.delete_many(x)

    return web.Response(status=204)


async def pay_down(id, collection_DOWN) :
    data = {"payed" : True}
    x = {"_id" : id}

    document = await collection_DOWN.find_one(x)

    if document != None :
        await collection_DOWN.update_one({'_id': id}, {'$set': data})
