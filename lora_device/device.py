import asyncio
# pip3 install pyserial-asyncio
from serial_asyncio import open_serial_connection

import json

# pip3 install cryptography
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

from binascii import unhexlify, hexlify

from cose.messages import CoseMessage, Enc0Message, Countersign0Message
from cose.keys import CoseKey, SymmetricKey
from cose.headers import Algorithm, KID, IV, Reserved
from cose.algorithms import Es256, A128GCM
from cose.keys.keyparam import EC2KpX, EC2KpY, EC2KpX, EC2KpY


deviceAdd = "0x1145f03880d8a975"
serialized_private = b'-----BEGIN PRIVATE KEY-----\nMIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgMSp/hxGyOMubQVr5\nxIUYeVqFjylWXBNRjvyp1di865ChRANCAARkOGbAJWUYFw8k6PsBsjM/1+8ULqrg\nmqjBIrQbkGY9DNTdZDcQOtvOg8dXiPN25nu4q3/Mda7pMyvSCSB3I7Jv\n-----END PRIVATE KEY-----\n'
serialized_public = b'-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEZDhmwCVlGBcPJOj7AbIzP9fvFC6q\n4JqowSK0G5BmPQzU3WQ3EDrbzoPHV4jzduZ7uKt/zHWu6TMr0gkgdyOybw==\n-----END PUBLIC KEY-----\n'
pubkey = serialization.load_pem_public_key(serialized_public, backend=default_backend())
x_pub = format(pubkey.public_numbers().x, '064x')
y_pub = format(pubkey.public_numbers().y, '064x')
print(f"x_pub : {x_pub} {type(x_pub)}")
print(f"y_pub : {y_pub} {type(y_pub)}")

serialized_public_server = b'-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEwpdpE2Fm7sEpnhtdVsSN4Xh6P3Lw\n6O5cFDV+9bePxup2ZrAMMIJIz4JMjiJN2P/MTM0TYsgi8uqC9bAfeeG0mg==\n-----END PUBLIC KEY-----\n'

# Sign1 :
# message = b'\xd2\x84C\xa1\x01&\xa0Xr\xd0\x83XF\xa3\x01\x01\x05X\x1a000102030405060708090a0b0c\x00x#["0100", "0", "0x37dae2a4323e7028"]\xa0X%-b\xc8}l\xc6\x91#\x1bm?\x06\xd2\x13\x13ac\xd8\xa0@\xec\xa2\xc2!\xb0\xd3K)\x9b\xcc\xf1\x95\xaes\x19\xaa\xe7X@\xf4\x11\x1ayj\x1f\'\xf1/\xe8\x8fi6\x0eO\x95\xccE\xff\xb8\xbc7-ff\xf1\xdc\xf5m\xac\xf0qsH\x95\xc5\xc94\xe7\xae@\xab\x8f\x13\xa6u\xd9\xcf\xdc\xa0\xd4\x86\xa9\x88\xa3\xa2\x92\xc4m\xe3\x1a\xf4\xbf\xb0'
# Counter sign :
# message = b'\xd0\x83XF\xa3\x01\x01\x05X\x1a000102030405060708090a0b0c\x00x#["0011", "0", "0x1145f03880d8a975"]\xa1\x0b\x83C\xa1\x01&\xa0X@\x92\xc9\xb2v\xa4\xaa\xd3s+\x8a\xebT\xdc\x07o\xf5NH\xe8 Rz4\x82\xe3H\x18\x97\x15\xb6Z\x1c\x97$X\\H\xd8\x88/aC\x15\x9d\x07\x93\x1ftG\xd1\xa2T\xb5\x9eB\xe0^J\xcb\x82\xd8\xccN\rUk\xe5(J\x13\rz\xf3\xf7\xbe\xb3\xa7\xc4\x88\xc1\xe9\xbf\xaaM\xc8i'
# message = "Hello"

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
    counter = await read_increment_counter()
    plaintext = text
    header = [pType, str(counter), deviceAdd]

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


# Counter Signature version
async def sign(encrypted):
    privkey = serialization.load_pem_private_key(serialized_private, password=None, backend=default_backend())
    bytes_key_priv = privkey.private_numbers().private_value.to_bytes(32, 'big')
    x = format(privkey.private_numbers().public_numbers.x, '064x')
    y = format(privkey.private_numbers().public_numbers.y, '064x')

    msg2 = Countersign0Message(
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


# Counter Signature version
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

    decoded = Countersign0Message(
        # phdr = {Algorithm: Es256},
        #payload = 'signed message'.encode('utf-8')
        payload = packet
    )
    decoded.key = pub_cose_key

    if decoded.verify_signature() :
        #print("Signature is correct")
        return True
    else :
        #print("Signature is not correct")
        return False


async def decrypt(packet, key):
    cose_key_dec = SymmetricKey(key, optional_params={'ALG': 'A128GCM'})

    decoded = CoseMessage.decode(packet)

    # decoded = CoseMessage.decode(decoded.payload)
    decoded.key = cose_key_dec
    decrypt = decoded.decrypt()
    decrypt_decode = decrypt.decode("utf-8")
    #print("Payload :", decrypt_decode)

    return decrypt_decode


async def run():

    message = input('Message payload : ')

    key = await generate_key_sym()

    encrypted = await encrypt(message, key)

    packet = await sign(encrypted)

    reader, writer = await open_serial_connection(url='/dev/serial0', baudrate=115200)

    packet_hex = hexlify(packet)
    # print(message)
    writer.write(packet_hex + b'\n')
    await writer.drain()

    line = await reader.readline()
    line = line[:-1]
    # print("cleaned :", line)
    line_unhex = unhexlify(line)
    print("received :", line_unhex)
    # print(line_unhex == packet)

    try :
        if line_unhex != b'' and b'error' not in line_unhex :
            signature = await check_signature(line_unhex, serialized_public_server)

            if signature :
                print("Signature is correct")
                key = await generate_key_sym()
                decrypted = await decrypt(line_unhex, key)
                print("Payload :", decrypted)
            else :
                print("Signature is not correct")


    except ValueError :
        print("ValueError")
        print('error, corrupted data')
    except TypeError :
        print("TypeError")
        print('error, corrupted data')
    except AttributeError :
        print("AttributeError")
        print('error, corrupted data')
    except SystemError :
        print("SystemError")
        print('error, corrupted data')


    return


def main():
    loop = asyncio.get_event_loop()

    # loop.run_until_complete(start())

    try:
        # loop.run_forever()
        loop.run_until_complete(run())
    except KeyboardInterrupt:
        pass

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
