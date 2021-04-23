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
from cbor2 import dumps, loads

from binascii import unhexlify, hexlify

from cose.messages import Sign1Message, CoseMessage, Enc0Message, Mac0Message
from cose.keys import CoseKey, EC2Key, SymmetricKey
from cose.headers import Algorithm, KID, IV, Reserved
from cose.algorithms import EdDSA, Es256, EcdhEsA256KW, EcdhEsA128KW, DirectHKDFAES128, EcdhSsA128KW, A128GCM, HMAC256
from cose.curves import Ed25519
from cose.keys.keyparam import KpKty, OKPKpD, OKPKpX, KpKeyOps, OKPKpCurve, EC2KpX, EC2KpY, KpAlg, KpKty, EC2KpD, EC2KpX, KpKeyOps, EC2KpCurve, EC2KpY, KpKid, SymKpK
from cose.keys.keytype import KtyEC2, KtySymmetric, KtyOKP
from cose.keys.keyops import SignOp, VerifyOp, DeriveKeyOp, MacCreateOp, MacVerifyOp
from cose.curves import P256

async def generate_deviceAdd():
    deviceAdd = hex(random.getrandbits(64))        # 64 bits identifier
    return deviceAdd

async def generate_key_pair():

    priv_device = ec.generate_private_key(
        ec.SECP256R1(),     # courbe elliptic 256 bits
        backend=default_backend()
    )

    serialized_private_device = priv_device.private_bytes(
        encoding=serialization.Encoding.PEM,        # DER
        format=serialization.PrivateFormat.PKCS8,   # TraditionalOpenSSL or PKCS8
        encryption_algorithm=serialization.NoEncryption()
    ).decode("utf-8")
    print("serialized_private_device :", serialized_private_device)


    pub_device = priv_device.public_key()

    serialized_public_device = pub_device.public_bytes(
        encoding=serialization.Encoding.PEM, 
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")
    print("serialized_public_device :", serialized_public_device)

    return serialized_private_device, serialized_public_device


async def get_source(packet):
    decoded = CoseMessage.decode(packet)
    decoded = CoseMessage.decode(decoded.payload)
    #print(f'phdr {decoded.phdr} {type(decoded.phdr)}')
    header_decode = json.loads(decoded.phdr[Reserved])
    source = header_decode[2]
    #print(f'source : {source} {type(source)}')
    return source


async def check_signature(packet, pubkey):
    pubkey = pubkey.encode("utf-8")
    pubkey = serialization.load_pem_public_key(pubkey)
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


async def generate_key_sym(privkey, pubkey):
    privkey = serialization.load_pem_private_key(privkey, password=None)

    pubkey = pubkey.encode("utf-8")
    pubkey = serialization.load_pem_public_key(pubkey)

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


async def decrypt(packet, key_sym):
    cose_key_dec = SymmetricKey(key_sym, optional_params={'ALG': 'A128GCM'})

    packet = CoseMessage.decode(packet)

    decoded = CoseMessage.decode(packet.payload)
    decoded.key = cose_key_dec
    decrypt = decoded.decrypt()
    decrypt_decode = decrypt.decode("utf-8")
    print("Payload :", decrypt_decode) 

    return decrypt_decode