import os
import zlib
import random
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.exceptions import InvalidSignature

from binascii import unhexlify, hexlify

from cose.messages import Sign1Message, CoseMessage, Enc0Message, Mac0Message, Countersign0Message
from cose.keys import CoseKey, EC2Key, SymmetricKey
from cose.headers import Algorithm, KID, IV, Reserved
from cose.algorithms import EdDSA, Es256, EcdhEsA256KW, EcdhEsA128KW, DirectHKDFAES128, EcdhSsA128KW, A128GCM, HMAC256
from cose.keys.keyparam import KpKty, OKPKpD, OKPKpX, KpKeyOps, OKPKpCurve, EC2KpX, EC2KpY, KpAlg, KpKty, EC2KpD, EC2KpX, KpKeyOps, EC2KpCurve, EC2KpY, KpKid, SymKpK
from cose.keys.keytype import KtyEC2, KtySymmetric, KtyOKP
from cose.keys.keyops import SignOp, VerifyOp, DeriveKeyOp, MacCreateOp, MacVerifyOp

from ecdsa.keys import SigningKey, VerifyingKey, BadSignatureError
from ecdsa.curves import NIST256p
from ecdsa.ellipticcurve import Point

from hashlib import sha256


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

async def generate_deviceAdd():
    deviceAdd = hex(random.getrandbits(64))        # 64 bits identifier
    return deviceAdd

async def generate_key_pair():

    priv_device = ec.generate_private_key(
        ec.SECP256R1(),     # courbe elliptic 256 bits
        backend=default_backend()
    )

    private_value = priv_device.private_numbers().private_value
    private_value = str(private_value)
    print("private_value :", private_value)

    x_pub = format(priv_device.private_numbers().public_numbers.x, '064x')
    y_pub = format(priv_device.private_numbers().public_numbers.y, '064x')
    # print(f"x_pub : {x_pub} {type(x_pub)}")
    # print(f"y_pub : {y_pub} {type(y_pub)}")

    return private_value, x_pub, y_pub


async def get_header(packet):
    decoded = CoseMessage.decode(packet)
    header_decode = json.loads(decoded.phdr[Reserved])
    header_decode[0] = d[header_decode[0]]
    return header_decode


# Counter Signature version
async def check_signature(packet, x_pub, y_pub):
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
        payload = packet
    )
    decoded.key = pub_cose_key

    if decoded.verify_signature() :
        #print("Signature is correct")
        return decoded
    else :
        #print("Signature is not correct")
        return False


async def generate_key_sym(privkey, x_pub, y_pub):
    privkey = serialization.load_pem_private_key(privkey, password=None)

    x_pub_int = int(x_pub, 16)
    y_pub_int = int(y_pub, 16)
    pubkey = ec.EllipticCurvePublicNumbers(x_pub_int, y_pub_int, ec.SECP256R1()).public_key()

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


async def decrypt(packet, key):
    cose_key_dec = SymmetricKey(key, optional_params={'ALG': 'A128GCM'})

    decoded = CoseMessage.decode(packet)

    decoded.key = cose_key_dec
    decrypt = decoded.decrypt()
    decrypt_decode = decrypt.decode("utf-8")

    return decrypt_decode


async def encrypt(header, plaintext, key):
    cose_key_enc = SymmetricKey(key, optional_params={'ALG': 'A128GCM'})

    header[0] = await get_key_by_value(header[0])

    msg = Enc0Message(
        phdr = {Algorithm: A128GCM, IV: b'000102030405060708090a0b0c', Reserved: json.dumps(header)},
        payload = plaintext.encode('utf-8')
    )

    msg.key = cose_key_enc
    encrypted = msg.encode()

    return encrypted


# Counter Signature version
async def sign(encrypted, privkey):
    privkey = serialization.load_pem_private_key(privkey, password=None)
    bytes_key_priv = privkey.private_numbers().private_value.to_bytes(32, 'big')
    x = format(privkey.private_numbers().public_numbers.x, '064x')
    y = format(privkey.private_numbers().public_numbers.y, '064x')

    key_attribute_dict = {
        'KTY': 'EC2',
        'CURVE': 'P_256',
        'ALG': 'ES256',
        EC2KpX : unhexlify(x),
        EC2KpY : unhexlify(y),
        'D': bytes_key_priv
    }
    cose_key = CoseKey.from_dict(key_attribute_dict)

    msg = Countersign0Message(
        phdr = {Algorithm: Es256},
        payload = encrypted
    )

    msg.key = cose_key
    packet = msg.encode()
    
    return packet


def verify_signature_hash(x_pub, y_pub, data, signature) :
    p = Point(curve=NIST256p.curve, x=int(x_pub, 16), y=int(y_pub, 16))

    vk = VerifyingKey.from_public_point(p, NIST256p, sha256)

    try:
        return vk.verify_digest(signature=signature, digest=data)
    except BadSignatureError:
        return False


async def get_key_by_value(value):
    if value not in reverse:
        for _k, _v in d.items():
           if _v == value:
               reverse[_v] = _k
               break
    return reverse[value]