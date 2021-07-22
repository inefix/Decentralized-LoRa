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

async def verify_countersign(packet, x_pub, y_pub) :
    pac = b'\xd0\x83XF\xa3\x01\x01\x05X\x1a000102030405060708090a0b0c\x00x#["0011", "0", "0x1145f03880d8a975"]\xa1\x0b\x83C\xa1\x01&\xa0X@\x92\xc9\xb2v\xa4\xaa\xd3s+\x8a\xebT\xdc\x07o\xf5NH\xe8 Rz4\x82\xe3H\x18\x97\x15\xb6Z\x1c\x97$X\\H\xd8\x88/aC\x15\x9d\x07\x93\x1ftG\xd1\xa2T\xb5\x9eB\xe0^J\xcb\x82\xd8\xccN\rUk\xe5(J\x13\rz\xf3\xf7\xbe\xb3\xa7\xc4\x88\xc1\xe9\xbf\xaaM\xc8i'
    print("verify")
    print(f"packet : {packet} {type(packet)}")
    print(pac == packet)
    print(f"x_pub : {x_pub} {type(x_pub)}")
    print(f"y_pub : {y_pub} {type(y_pub)}")
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
        # return True
        # to_be_signed = decoded._sig_structure
        # print("to_be_signed :", to_be_signed)
        return decoded
    else :
        print("Signature is not correct")
        return False



async def get_header(packet):
    decoded = CoseMessage.decode(packet)
    # decoded = CoseMessage.decode(decoded.payload)
    #print(f'phdr {decoded.phdr} {type(decoded.phdr)}')
    header_decode = json.loads(decoded.phdr[Reserved])
    header_decode[0] = d[header_decode[0]]
    #source = header_decode[2]
    #print(f'source : {source} {type(source)}')
    return header_decode
