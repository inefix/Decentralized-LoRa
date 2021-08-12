"""UDP server"""
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
import requests_async as requests   # pip3 install requests-async

from lora import generate_deviceAdd, generate_key_pair, get_header, check_signature, generate_key_sym, decrypt, encrypt, sign, verify_signature_hash
from device import test, get_all_devices, remove_all_devices, create_device, get_one_device, update_device, remove_device, generate_device, get_pubkey
from msg import get_all_msg, get_multiple_msg, remove_all_msg, create_msg, get_one_msg, update_msg, remove_msg, get_last_msg, get_address, update_payed
from gateway import get_one_gateway, delete_one_gateway, create_gateway, update_gateway
from down import get_all_down, remove_all_down, create_down, get_one_down, get_one_down_f, update_down, remove_down, pay_down


ADDR = "163.172.130.246"
# ADDR = "2001:0620:0000:0000:0211:24FF:FE80:C12C"
PORT = 9999

# payment_method can be 'OMG' or 'MPC'
payment_method = 'OMG'
message_price = 3000000000000       # in whei = 0,000003 eth = 0.1 usd

automatic_pay = True
automatic_response = True

ether_add = '0x5E8138098a133B6424AEC09232674E253909B3Fb'


serialized_private_server = b'-----BEGIN PRIVATE KEY-----\nMIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQg5hsInzp4UhjgehRh\nA+55y9GGR7dai4Kky4LCYpE+jFGhRANCAATCl2kTYWbuwSmeG11WxI3heHo/cvDo\n7lwUNX71t4/G6nZmsAwwgkjPgkyOIk3Y/8xMzRNiyCLy6oL1sB954bSa\n-----END PRIVATE KEY-----\n'
# serialized_public_server = b'-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEwpdpE2Fm7sEpnhtdVsSN4Xh6P3Lw\n6O5cFDV+9bePxup2ZrAMMIJIz4JMjiJN2P/MTM0TYsgi8uqC9bAfeeG0mg==\n-----END PUBLIC KEY-----\n'
x_pub_server = "c29769136166eec1299e1b5d56c48de1787a3f72f0e8ee5c14357ef5b78fc6ea"
y_pub_server = "7666b00c308248cf824c8e224dd8ffcc4ccd1362c822f2ea82f5b01f79e1b49a"

client = motor.motor_asyncio.AsyncIOMotorClient('mongodb+srv://lora:lora@lora.j8ycs.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')



ADDR_int = ADDR
ADDR_type = None

if ADDR.count(":") > 1:
    print("IPv6")
    ADDR_int = int(ipaddress.IPv6Address(ADDR))
    ADDR_type = "IPv6"
    # print(ADDR_int)
elif ADDR[0].isdigit() and ADDR[len(ADDR)-1].isdigit() :
    print("IPv4")
    ADDR_int = int(ipaddress.IPv4Address(ADDR))
    ADDR_type = "IPv4"
    # print(ADDR_int)
else :
    print("domain")
    ADDR_type = "domain"


db = client['lora_db']
collection_DEVICE = db['DEVICE']
collection_MSG = db['MSG']
collection_GATEWAY = db['GATEWAY']
collection_DOWN = db['DOWN']

add = "0.0.0.0"     # localhost does not work ! https://stackoverflow.com/questions/15734219/simple-python-udp-server-trouble-receiving-packets-from-clients-other-than-loca/15734249


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
            last_msg = await get_last_msg(deviceAdd, collection_MSG)
            if last_msg == None :
                last_counter = -1
                last_gateway = gateway_add
            else :
                last_counter = int(last_msg['counter'])
                last_gateway = last_msg['gateway']
            
            if int(counter_header) > last_counter :
            # if 100 > last_counter :
                print("Last counter from this device :", last_counter)
            
                # verify that gateway is the same
                if gateway_add != last_gateway:
                # if "gateway_add" != last_gateway:
                    print("Sleep")
                    await asyncio.sleep(10)
                    last_msg = await get_last_msg(deviceAdd, collection_MSG)
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

                    payment_receipt = None
                    if payment_method == 'OMG' :
                        payment_receipt = await omg_pay(deviceAdd, counter_header, gateway_add, price)
                    if payment_method == 'MPC' :
                        payment_receipt = await mpc_pay(deviceAdd, counter_header, gateway_add, price)

                    if "error" not in payment_receipt and payment_receipt != None:

                        if down != b"down_message" :
                            await pay_down(down_id, collection_DOWN)

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

                        print("Response :", response)

                        if down == b"down_message" and response != b"nothing" and b"error" not in response and payment_method != 'OMG':
                            print("Send response")

                            # pay for the message if it is actual content
                            payment_receipt = "nothing"
                            # print("pay")
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
            # print(e)
            print("Connection closed\n")
            return

        except ValueError:
            response = "error : message already processed"
            print(response)
            await websocket.send(response)
            # return


async def process(message, hash_structure, gateway, down):
    header = await get_header(message)
    pType = header[0]
    counter = header[1]
    deviceAdd = header[2]
    # print("header :", header)
    # print("deviceAdd :", deviceAdd)
    # print("counter :", counter)

    x_pub, y_pub = await get_pubkey(deviceAdd, collection_DEVICE)

    if x_pub != "error" and y_pub != "error":

        valid = await check_signature(message, x_pub, y_pub)

        if valid != False :
            print("Signature is correct")
            # print(valid)

            to_be_signed = valid._sig_structure
            message_hash = hashlib.sha256(to_be_signed).digest()
            # print(to_be_signed)
            # print(message_hash)

            if hash_structure == message_hash :
                print("Hash is correct")

                key = await generate_key_sym(serialized_private_server, x_pub, y_pub)
                decrypted = await decrypt(message, key)
                print("Payload :", decrypted) 

                # store decrypted message into db + header + owner
                id = str(time.time())
                date = str(datetime.datetime.now().strftime('%d-%m-%Y_%H:%M:%S'))

                x = {"_id" : id, "date" : date, "owner" : ether_add, "gateway" : gateway, "payed" : automatic_pay, "pType" : pType, "counter" : counter, "deviceAdd" : deviceAdd, "payload" : decrypted}
                await collection_MSG.insert_one(x)

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
                    # print("nothing to send")
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
    # update the counter
    f = open("counter.txt", "w")
    f.write(str(counter))
    f.close()

    return counter


async def start(request):
    print("Server started")
    return web.json_response({'success': 'Server started'})


async def down_message(deviceAdd, x_pub, y_pub):
    key = await generate_key_sym(serialized_private_server, x_pub, y_pub)
    payload_respond = await get_one_down_f(deviceAdd, collection_DOWN)
    if payload_respond != None :
        print("Payload of the response :", payload_respond['payload'])
        counter = await read_increment_counter()
        header_respond = ["DataUnconfirmedDown", counter, ADDR]
        encrypted = await encrypt(header_respond, payload_respond['payload'], key)
        packet = await sign(encrypted, serialized_private_server)
        return packet, payload_respond["_id"]
    else :
        return b"down_message", None


async def close_contract(gateway_add):
    # verifies that the smart contract has been closed
    # get the contract_add
    gateway_document = await get_one_gateway(gateway_add, collection_GATEWAY)
    contract_add = gateway_document['contract']
    # wait a moment
    await asyncio.sleep(20)
    balance = await web3.eth.getBalance(contract_add)
    # print("balance :", balance)
    if balance == 0:
        # delete the gateway
        await delete_one_gateway(gateway_add, collection_GATEWAY)


async def verify_hash(hash_structure, signature, deviceAdd):
    try :
        x_pub, y_pub = await get_pubkey(deviceAdd, collection_DEVICE)
        verified = verify_signature_hash(x_pub, y_pub, hash_structure, signature)
        print("Hash is valid ?", verified)

        return verified

    except Exception :
        return False


async def check_if_down(deviceAdd):
    x_pub, y_pub = await get_pubkey(deviceAdd, collection_DEVICE)

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
    print("Payment hash :", payment_hash)
    response = payment_method + ',' + payment_hash

    return response


async def mpc_pay(deviceAdd, counter_header, gateway_add, price):
    # verifies that gateway is already stored in GATEWAY DB
    gateway_document = await get_one_gateway(gateway_add, collection_GATEWAY)
    # print("gateway_document :", gateway_document)
    if gateway_document == None :
        # deploy smart contract 
        amount_creation = 100 * price
        duration = 30 * 24 * 60 * 60
        epoch_time = int(time.time())
        expiration = epoch_time + duration
        body = {'receiverAdd': gateway_add, 'amount': amount_creation, 'duration' : duration}
        body = json.dumps(body)
        request = await requests.post('http://163.172.130.246:3000/deploy/', data=body, headers= { 'Content-Type': 'application/json'})
        contract_add = request.text
        # store gateway_add, contract_add, amount_creation, expiration
        amount_payed = 0
        await create_gateway(gateway_add, contract_add, amount_payed, amount_creation, expiration, collection_GATEWAY)
    else :
        contract_add = gateway_document['contract']
        amount_payed = gateway_document['amount_payed']
        amount_creation = gateway_document['amount_creation']
    
    # pay for the message --> amount_payed + price
    new_amount = amount_payed + price
    print("New amount :", new_amount)
    if amount_creation > new_amount :

        body = {'contractAddress': contract_add, 'amount': new_amount}
        body = json.dumps(body)
        request = await requests.post('http://163.172.130.246:3000/signPayment/', data=body, headers= { 'Content-Type': 'application/json'})
        signature = request.text

        # update amount in GATEWAY DB
        await update_gateway(gateway_add, new_amount, collection_GATEWAY)

        # return respone --> MPC,signature,contract_add,price
        response = payment_method + ',' + signature + ',' + contract_add + ',' + str(price)

    else :
        response = "error5 : not enough money in the smart contract"
        print(response)
        
        # deploy new smart contract and update DB

    return response


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


app['collection_DEVICE'] = collection_DEVICE
app['collection_MSG'] = collection_MSG
app['collection_GATEWAY'] = collection_GATEWAY
app['collection_DOWN'] = collection_DOWN

app['ADDR_int'] = ADDR_int
app['PORT'] = PORT


def main(add=add, port=PORT):
    loop = asyncio.get_event_loop()

    print("Starting the Websocket server...")
    start_server = websockets.serve(ws, "0.0.0.0", 8765)
    loop.run_until_complete(start_server)

    print("Starting the HTTP server...")
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
