import json
import random

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend

from binascii import unhexlify

from cose.messages import CoseMessage, Enc0Message, CountersignMessage
from cose.keys import CoseKey, SymmetricKey
from cose.headers import Algorithm, KID, IV, Reserved
from cose.algorithms import Es256, A128GCM
from cose.keys.keyparam import EC2KpX, EC2KpY, EC2KpX, EC2KpY


async def generate_deviceAdd():
    deviceAdd = hex(random.getrandbits(64))        # 64 bits identifier
    return deviceAdd


async def generate_key_pair():

    priv_device = ec.generate_private_key(
        ec.SECP256R1(),     # elliptic curve --> 256 bits key
        backend=default_backend()
    )

    private_value = priv_device.private_numbers().private_value

    x_pub = format(priv_device.private_numbers().public_numbers.x, '064x')
    y_pub = format(priv_device.private_numbers().public_numbers.y, '064x')

    return private_value, x_pub, y_pub


async def generate_key_sym(private_value, x_pub_server, y_pub_server):
    # use the private key of the device
    privkey = ec.derive_private_key(
        private_value,
        ec.SECP256R1(),     # elliptic curve 256 bits
        backend=default_backend()
    )

    # use the public key of the server
    x_pub_int = int(x_pub_server, 16)
    y_pub_int = int(y_pub_server, 16)
    pubkey = ec.EllipticCurvePublicNumbers(x_pub_int, y_pub_int, ec.SECP256R1()).public_key(backend=default_backend())

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


async def encrypt(key, deviceAdd, text):
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

    mType = await get_key_by_value(d, reverse, "DataConfirmedUp")
    counter = await read_increment_counter()
    plaintext = text
    header = [mType, str(counter), deviceAdd]

    msg = Enc0Message(
        phdr = {Algorithm: A128GCM, IV: b'000102030405060708090a0b0c', Reserved: json.dumps(header)},
        #uhdr = {KID: b'kid1'},
        payload = plaintext.encode('utf-8')
    )

    cose_key_enc = SymmetricKey(key, optional_params={'ALG': 'A128GCM'})

    msg.key = cose_key_enc
    encrypted = msg.encode()

    return encrypted


# Counter Signature version
async def sign(private_value, x_pub_device, y_pub_device, encrypted):
    bytes_key_priv = private_value.to_bytes(32, 'big')

    msg2 = CountersignMessage(
        phdr = {Algorithm: Es256},
        payload = encrypted
    )

    key_attribute_dict = {
        'KTY': 'EC2',
        'CURVE': 'P_256',
        'ALG': 'ES256',
        EC2KpX : unhexlify(x_pub_device),
        EC2KpY : unhexlify(y_pub_device),
        'D': bytes_key_priv
    }
    cose_key = CoseKey.from_dict(key_attribute_dict)

    msg2.key = cose_key
    packet = msg2.encode()
    print("Packet :", packet)

    return packet


# Counter Signature version
async def check_signature(x_pub_server, y_pub_server, packet):
    pub_key_attribute_dict = {
            'KTY': 'EC2',
            'CURVE': 'P_256',
            'ALG': 'ES256',
            EC2KpX : unhexlify(x_pub_server),
            EC2KpY : unhexlify(y_pub_server)
    }
    pub_cose_key = CoseKey.from_dict(pub_key_attribute_dict)

    decoded = CountersignMessage(
        # phdr = {Algorithm: Es256},
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

    decoded.key = cose_key_dec
    decrypt = decoded.decrypt()
    decrypt_decode = decrypt.decode("utf-8")

    return decrypt_decode


async def get_key_by_value(d, reverse, value):
    if value not in reverse:
        for _k, _v in d.items():
           if _v == value:
               reverse[_v] = _k
               break
    return reverse[value]


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
