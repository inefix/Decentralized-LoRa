import asyncio

import os
import zlib
import random
#import numpy as np
import json

# pip3 install cryptography
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.exceptions import InvalidSignature
#from cbor2 import dumps, loads

from binascii import unhexlify, hexlify

# pip3 install cose
from cose.messages import Sign1Message, CoseMessage, Enc0Message, Mac0Message
from cose.keys import CoseKey, EC2Key, SymmetricKey
from cose.headers import Algorithm, KID, IV, Reserved
from cose.algorithms import EdDSA, Es256, EcdhEsA256KW, EcdhEsA128KW, DirectHKDFAES128, EcdhSsA128KW, A128GCM, HMAC256
from cose.curves import Ed25519
from cose.keys.keyparam import KpKty, OKPKpD, OKPKpX, KpKeyOps, OKPKpCurve, EC2KpX, EC2KpY, KpAlg, KpKty, EC2KpD, EC2KpX, KpKeyOps, EC2KpCurve, EC2KpY, KpKid, SymKpK
from cose.keys.keytype import KtyEC2, KtySymmetric, KtyOKP
from cose.keys.keyops import SignOp, VerifyOp, DeriveKeyOp, MacCreateOp, MacVerifyOp
from cose.curves import P256

# add = "163.172.130.246"
# port = 9999

add = "0.0.0.0"
port = 1680

deviceAdd = "0x1145f03880d8a975"
serialized_private = b'-----BEGIN PRIVATE KEY-----\nMIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgMSp/hxGyOMubQVr5\nxIUYeVqFjylWXBNRjvyp1di865ChRANCAARkOGbAJWUYFw8k6PsBsjM/1+8ULqrg\nmqjBIrQbkGY9DNTdZDcQOtvOg8dXiPN25nu4q3/Mda7pMyvSCSB3I7Jv\n-----END PRIVATE KEY-----\n'
serialized_public = b'-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEZDhmwCVlGBcPJOj7AbIzP9fvFC6q\n4JqowSK0G5BmPQzU3WQ3EDrbzoPHV4jzduZ7uKt/zHWu6TMr0gkgdyOybw==\n-----END PUBLIC KEY-----\n'

serialized_public_server = b'-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEwpdpE2Fm7sEpnhtdVsSN4Xh6P3Lw\n6O5cFDV+9bePxup2ZrAMMIJIz4JMjiJN2P/MTM0TYsgi8uqC9bAfeeG0mg==\n-----END PUBLIC KEY-----\n'

# message = b'\xd2\x84C\xa1\x01&\xa0Xr\xd0\x83XF\xa3\x01\x01\x05X\x1a000102030405060708090a0b0c\x00x#["0100", "0", "0x37dae2a4323e7028"]\xa0X%-b\xc8}l\xc6\x91#\x1bm?\x06\xd2\x13\x13ac\xd8\xa0@\xec\xa2\xc2!\xb0\xd3K)\x9b\xcc\xf1\x95\xaes\x19\xaa\xe7X@\xf4\x11\x1ayj\x1f\'\xf1/\xe8\x8fi6\x0eO\x95\xccE\xff\xb8\xbc7-ff\xf1\xdc\xf5m\xac\xf0qsH\x95\xc5\xc94\xe7\xae@\xab\x8f\x13\xa6u\xd9\xcf\xdc\xa0\xd4\x86\xa9\x88\xa3\xa2\x92\xc4m\xe3\x1a\xf4\xbf\xb0'
message = "Hello"

async def generate_key_sym():
    privkey = serialization.load_pem_private_key(serialized_private, password=None, backend=default_backend())

    pubkey = serialization.load_pem_public_key(serialized_public_server, backend=default_backend())

    # ECDH
    s_key = privkey.exchange(ec.ECDH(), pubkey)

    # HKDF
    key = HKDF(
        algorithm=hashes.SHA256(),
        length=16,      # for AES128
        salt=None,
        info=b'handshake data',
        backend=default_backend()
    ).derive(s_key)

    return key


async def encrypt(text, key):
    d = {
        "0000": "JoinRequest", 
        "0001": "JoinResponse",
        "0010": "JoinAccept",
        "0011": "DataConfirmedUp",
        "0100": "DataUnconfirmedUp",
        "0101": "DataConfirmedDown",
        "0110": "DataUnconfirmedDown",
        "0111": "ACKUp",
        "1000": "ACKDown"
    }
    reverse = {}
    #print(d["0000"])
    #print(get_key_by_value(d, reverse, "JoinResponse"))

    pType = get_key_by_value(d, reverse, "DataConfirmedUp")
    counter = "0"
    plaintext = text
    header = [pType, counter, deviceAdd]

    msg = Enc0Message(
        phdr = {Algorithm: A128GCM, IV: b'000102030405060708090a0b0c', Reserved: json.dumps(header)},
        #uhdr = {KID: b'kid1'},
        payload = plaintext.encode('utf-8')
    )

    cose_key_enc = SymmetricKey(key, optional_params={'ALG': 'A128GCM'})
    #print(cose_key_enc)

    msg.key = cose_key_enc
    encrypted = msg.encode()
    print("Encrypted payload :", encrypted)

    return encrypted


async def sign(encrypted):
    privkey = serialization.load_pem_private_key(serialized_private, password=None, backend=default_backend())
    bytes_key_priv = privkey.private_numbers().private_value.to_bytes(32, 'big')
    x = format(privkey.private_numbers().public_numbers.x, '064x')
    y = format(privkey.private_numbers().public_numbers.y, '064x')
    
    msg2 = Sign1Message(
        phdr = {Algorithm: Es256},
        #payload = 'signed message'.encode('utf-8')
        payload = encrypted
    )

    key_attribute_dict = {
        'KTY': 'EC2',
        'CURVE': 'P_256',
        'ALG': 'ES256',
        EC2KpX : unhexlify(x),
        EC2KpY : unhexlify(y),
        'D': bytes_key_priv
    }
    cose_key = CoseKey.from_dict(key_attribute_dict)
    #print(cose_key)

    msg2.key = cose_key
    packet = msg2.encode()
    print("Packet :", packet)
    #print("Packet hexlify :", hexlify(packet))

    return packet


async def check_signature(packet, pubkey):
    pubkey = serialization.load_pem_public_key(serialized_public_server, backend=default_backend())
    x_pub = format(pubkey.public_numbers().x, '064x')
    y_pub = format(pubkey.public_numbers().y, '064x')

    pub_key_attribute_dict = {
            'KTY': 'EC2',
            'CURVE': 'P_256',
            'ALG': 'ES256',
            EC2KpX : unhexlify(x_pub),
            EC2KpY : unhexlify(y_pub)
    }
    pub_cose_key = CoseKey.from_dict(pub_key_attribute_dict)

    decoded = CoseMessage.decode(packet)
    decoded.key = pub_cose_key

    if decoded.verify_signature() :
        #print("Signature is correct")
        return True
    else :
        #print("Signature is not correct")
        return False


async def decrypt(packet, key):
    cose_key_dec = SymmetricKey(key, optional_params={'ALG': 'A128GCM'})

    packet = CoseMessage.decode(packet)

    decoded = CoseMessage.decode(packet.payload)
    decoded.key = cose_key_dec
    decrypt = decoded.decrypt()
    decrypt_decode = decrypt.decode("utf-8")
    #print("Payload :", decrypt_decode) 

    return decrypt_decode


class EchoClientProtocol:
    def __init__(self, message, loop):
        self.message = message
        self.loop = loop
        self.transport = None

    def connection_made(self, transport):
        loop = asyncio.get_event_loop()
        loop.create_task(self.connection_made_async(transport)) 

    async def connection_made_async(self, transport):
        self.transport = transport
        #print('Send:', self.message)

        key = await generate_key_sym()

        encrypted = await encrypt(self.message, key)

        packet = await sign(encrypted)

        self.transport.sendto(packet)


    def datagram_received(self, data, addr):
        loop = asyncio.get_event_loop()
        loop.create_task(self.datagram_received_async(data, addr))
        
    
    async def datagram_received_async(self, data, addr):
        #print("Received:", data.decode())
        print("Received:", data)

        signature = await check_signature(data, serialized_public_server)

        if signature :
            print("Signature is correct")
            key = await generate_key_sym()
            decrypted = await decrypt(data, key)
            print("Payload :", decrypted)
        else :
            print("Signature is not correct")

        print("Close the socket")
        self.transport.close()
        

    def error_received(self, exc):
        print('Error received:', exc)

    def connection_lost(self, exc):
        print("Socket closed, stop the event loop")
        loop = asyncio.get_event_loop()
        loop.stop()


async def start(add, port):
    loop = asyncio.get_event_loop()
    return await loop.create_datagram_endpoint(
        lambda: EchoClientProtocol(message, loop),
        remote_addr=(add, port))


def main(add=add, port=port):
    print(f'Connecting to server on port : {port}')

    loop = asyncio.get_event_loop()

    # connect = loop.create_datagram_endpoint(
    #     lambda: EchoClientProtocol(message, loop),
    #     remote_addr=(add, port))
    con = start(add, port)
    transport, _ = loop.run_until_complete(con)

    # loop.run_forever()
    # transport.close()
    # loop.close()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    transport.close()
    loop.close()


def get_key_by_value(d, reverse, value):
    if value not in reverse:
        for _k, _v in d.items():
           if _v == value:
               reverse[_v] = _k
               break
    return reverse[value]

if __name__ == '__main__':
    main()