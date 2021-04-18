import os
import zlib
import random
import numpy as np
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
from cose.headers import Algorithm, KID, IV
from cose.algorithms import EdDSA, Es256, EcdhEsA256KW, EcdhEsA128KW, DirectHKDFAES128, EcdhSsA128KW, A128GCM, HMAC256
from cose.curves import Ed25519
from cose.keys.keyparam import KpKty, OKPKpD, OKPKpX, KpKeyOps, OKPKpCurve, EC2KpX, EC2KpY, KpAlg, KpKty, EC2KpD, EC2KpX, KpKeyOps, EC2KpCurve, EC2KpY, KpKid, SymKpK
from cose.keys.keytype import KtyEC2, KtySymmetric, KtyOKP
from cose.keys.keyops import SignOp, VerifyOp, DeriveKeyOp, MacCreateOp, MacVerifyOp
from cose.curves import P256


def main():
    ########################### private key ###################################

    priv_device = ec.generate_private_key(
        ec.SECP256R1(),     # courbe elliptic 256 bits
        backend=default_backend()
    )

    bytes_key_priv = priv_device.private_numbers().private_value.to_bytes(32, 'big')
    x = format(priv_device.private_numbers().public_numbers.x, '064x')
    y = format(priv_device.private_numbers().public_numbers.y, '064x')
    #bytes_key_priv2 = unhexlify(format(priv_device.private_numbers().private_value, '064x'))
    #print("byte_key_priv :", bytes_key_priv)
    #print("byte_key_priv2 :", bytes_key_priv2)
    #print("x :", x)

    # serialized_private = priv_device.private_bytes(
    #     encoding=serialization.Encoding.DER,
    #     format=serialization.PrivateFormat.TraditionalOpenSSL,
    #     encryption_algorithm=serialization.NoEncryption()
    # )
    # print(serialized_private)

    pub_device = priv_device.public_key()
    #bytes_key_pub = pub_device.public_bytes(encoding=serialization.Encoding.DER, format=serialization.PublicFormat.SubjectPublicKeyInfo)
    x_pub = format(pub_device.public_numbers().x, '064x')
    y_pub = format(pub_device.public_numbers().y, '064x')
    #print("x_pub :", x_pub)

    priv_server = ec.generate_private_key(
        ec.SECP256R1(),
        backend=default_backend()
    )

    pub_server = priv_server.public_key()

    ############################# ECDH ########################################

    s_device = priv_device.exchange(ec.ECDH(), pub_server)
    s_server = priv_server.exchange(ec.ECDH(), pub_device)

    print("ECDH keys :")

    print("Device key :", s_device)
    print("Server key :", s_server)

    print("################################################")


    ############################ HKDF #########################################

    key_device = HKDF(
        algorithm=hashes.SHA256(),
        length=16,      # for AES128
        salt=None,
        info=b'handshake data',
        backend=default_backend()
    ).derive(s_device)

    key_server = HKDF(
        algorithm=hashes.SHA256(),
        length=16,      # for AES128
        salt=None,
        info=b'handshake data',
        backend=default_backend()
    ).derive(s_server)

    print("HKDF keys :")

    print("Device key :", key_device)
    print("Server key :", key_server)

    #print("################################################")


    ############################# COSE Encrypt0 ##################################
    print("\nDevice level :")

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

    PType = get_key_by_value(d, reverse, "DataUnconfirmedUp")
    Counter = "0"
    DeviceAdd = hex(random.getrandbits(64))        # 64 bits identifier
    Ciphertext = "Hello from the device"
    Header = [PType, Counter, DeviceAdd]
    Content = [Ciphertext]

    concat = Header + Content
    string = ','.join(concat)
    print("Payload as string :", string)

    msg = Enc0Message(
        phdr = {Algorithm: A128GCM, IV: b'000102030405060708090a0b0c'},
        #uhdr = {KID: b'kid1'},
        payload = string.encode('utf-8')
    )

    cose_key_enc = SymmetricKey(key=key_device, optional_params={'ALG': 'A128GCM'})
    #print(cose_key_enc)

    msg.key = cose_key_enc
    encrypted = msg.encode()
    print("Encrypted payload :", encrypted)
    #print("Encrypted payload hexlify :", hexlify(encoded))



    ############################## COSE Sign1 ################################

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



    ############################### Sending the packet ... ########################

    print("\nSending the packet ...")

    ######### Verification of the source by the Gateway ... #######################
    print("\nGateway level :")

    pub_key_attribute_dict = {
        'KTY': 'EC2',
        'CURVE': 'P_256',
        'ALG': 'ES256',
        EC2KpX : unhexlify(x_pub),
        EC2KpY : unhexlify(y_pub)
    }

    pub_cose_key = CoseKey.from_dict(pub_key_attribute_dict)

    decoded = CoseMessage.decode(packet)
    #print("decoded :", decoded)
    decoded.key = pub_cose_key

    if decoded.verify_signature() :
        print("Signature is correct")
    else :
        print("Signature is not correct")

    print("Payload at the gateway level :", decoded.payload)



    ############## Reception of the packet on the server .... #################
    print("\nServer level :")

    # Checking the signature

    pub_key_attribute_dict2 = {
        'KTY': 'EC2',
        'CURVE': 'P_256',
        'ALG': 'ES256',
        EC2KpX : unhexlify(x_pub),
        EC2KpY : unhexlify(y_pub)
    }

    pub_cose_key2 = CoseKey.from_dict(pub_key_attribute_dict2)

    decoded2 = CoseMessage.decode(packet)
    #print("decoded :", decoded2)
    decoded2.key = pub_cose_key2

    if decoded2.verify_signature() :
        print("Signature is correct")
    else :
        print("Signature is not correct")


    # decrypting
    
    cose_key_dec = SymmetricKey(key=key_server, optional_params={'ALG': 'A128GCM'})

    decoded3 = CoseMessage.decode(decoded2.payload)
    #print(decoded2)

    decoded3.key = cose_key_dec
    #print(hexlify(decoded2.payload))
    decrypt = decoded3.decrypt()
    decrypt_decode = decrypt.decode("utf-8")
    print("Data received as string :", decrypt_decode)

    concat_rec = decrypt_decode.split(',')
    print("Data :", concat_rec)    



    ############################# COSE MAC0 ####################################

    mac_msg = Mac0Message(
        phdr = {Algorithm: HMAC256},
        uhdr = {KID: b'kid3'},
        payload ='authenticated message'.encode('utf-8')
    )

    # key_attribute_mac = {
    #     'KTY': 'EC2',
    #     'CURVE': 'P_256',
    #     'ALG': 'ES256',
    #     EC2KpX : unhexlify(x),
    #     EC2KpY : unhexlify(y),
    #     'D': bytes_key_priv
    # }

    key_mac = SymmetricKey(key=key_device)

    mac_msg.key = key_mac
    # the encode() function automatically computes the authentication tag
    encoded_mac = mac_msg.encode()
    print(hexlify(encoded_mac))

    decoded_mac = CoseMessage.decode(encoded_mac)
    decoded_mac.key = key_mac
    #decoded_mac.payload = decoded_mac.payload + b'test'
    print("payload :", decoded_mac.payload)
    #print("tag :", hexlify(decoded_mac.auth_tag))
    print("verify tag :", decoded_mac.verify_tag())



def get_key_by_value(d, reverse, value):
    if value not in reverse:
        for _k, _v in d.items():
           if _v == value:
               reverse[_v] = _k
               break
    return reverse[value]


if __name__ == "__main__":
    main()
