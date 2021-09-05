import json
import requests_async as requests

WATCHER_INFO_URL = 'https://watcher-info.rinkeby.v1.omg.network'


async def verify_omg_payment(payment_hash, remote_host, price, ether_add):
    sender, currency, amount, receiver, metadata = await verifyHash(payment_hash)
    if receiver.lower() == ether_add.lower() and amount == price and currency == "0x0000000000000000000000000000000000000000" :
        return metadata
    else :
        print("There is an error in the payment")
        return None


async def verifyHash(hashed):
    body = {'id': hashed, 'jsonrpc': '2.0'}
    body = json.dumps(body)
    response = await requests.post(f'{WATCHER_INFO_URL}/transaction.get', data=body, headers= { 'Content-Type': 'application/json'})
    json_resp = response.json()
    sender = ""
    currency = ""
    amount = -1
    receiver = ""
    metadata = ""
    try :
        sender = json_resp['data']['inputs'][0]['owner']
        currency = json_resp['data']['inputs'][0]['currency']
        amount = json_resp['data']['outputs'][0]['amount']
        receiver = json_resp['data']['outputs'][0]['owner']
        metadata = json_resp['data']['metadata']
        # decrypt metadata
        metadata = bytearray.fromhex(metadata[2:]).decode()

    except KeyError :
        print("Transaction does not exist")

    return sender, currency, amount, receiver, metadata
