async def get_one_gateway(gateway_add):
    collection_GATEWAY = request.app['collection_GATEWAY']
    x = {"_id" : gateway_add}
    document = await collection_GATEWAY.find_one(x)
    return document


async def delete_one_gateway(gateway_add):
    collection_GATEWAY = request.app['collection_GATEWAY']
    x = {"_id" : gateway_add}
    await collection_GATEWAY.delete_many(x)


async def create_gateway(gateway_add, contract_add, amount_payed, amount_creation, expiration):
    collection_GATEWAY = request.app['collection_GATEWAY']
    # check unique id
    x = {"_id" : gateway_add}
    document = await collection_GATEWAY.find_one(x)
    if document == None :
        data = {"_id" : gateway_add, "contract": contract_add, "amount_payed": amount_payed, "amount_creation": amount_creation, "expiration": expiration}
        result = await collection_GATEWAY.insert_one(data)


async def update_gateway(gateway_add, new_amount):
    collection_GATEWAY = request.app['collection_GATEWAY']
    x = {"_id" : gateway_add}
    data = {"amount_payed" : new_amount}

    document = await collection_GATEWAY.find_one(x)

    if document != None :
        await collection_GATEWAY.update_one(x, {'$set': data})
