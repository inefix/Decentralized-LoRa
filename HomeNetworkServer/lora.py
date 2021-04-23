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