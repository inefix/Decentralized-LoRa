# Second version of the protocol using COSE Encrypt0 and CounterSignature

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
from base64 import b64encode, b64decode

from cose.messages import Sign1Message, CoseMessage, Enc0Message, Mac0Message, CountersignMessage
from cose.keys import CoseKey, EC2Key, SymmetricKey
from cose.headers import Algorithm, KID, IV, Reserved
from cose.algorithms import EdDSA, Es256, EcdhEsA256KW, EcdhEsA128KW, DirectHKDFAES128, EcdhSsA128KW, A128GCM, HMAC256
from cose.keys.keyparam import KpKty, OKPKpD, OKPKpX, KpKeyOps, OKPKpCurve, EC2KpX, EC2KpY, KpAlg, KpKty, EC2KpD, EC2KpX, KpKeyOps, EC2KpCurve, EC2KpY, KpKid, SymKpK
from cose.keys.keytype import KtyEC2, KtySymmetric, KtyOKP
from cose.keys.keyops import SignOp, VerifyOp, DeriveKeyOp, MacCreateOp, MacVerifyOp

import hashlib

from counterSign import counterSign, counterVerify, CounterSignature0, verify


def main():
    ########################### private key ###################################

    priv_device = ec.generate_private_key(
        ec.SECP256R1(),     # elliptic curve --> 256 bits key
        backend=default_backend()
    )

    serialized_private_device = priv_device.private_bytes(
        encoding=serialization.Encoding.PEM,        # DER
        format=serialization.PrivateFormat.PKCS8,   # TraditionalOpenSSL or PKCS8
        encryption_algorithm=serialization.NoEncryption()
    ).decode("utf-8")
    priv_device = serialization.load_pem_private_key(serialized_private_device.encode("utf-8"), password=None)

    bytes_key_priv = priv_device.private_numbers().private_value.to_bytes(32, 'big')
    x = format(priv_device.private_numbers().public_numbers.x, '064x')
    y = format(priv_device.private_numbers().public_numbers.y, '064x')
    #bytes_key_priv2 = unhexlify(format(priv_device.private_numbers().private_value, '064x'))
    print("byte_key_priv :", bytes_key_priv)
    private_value = priv_device.private_numbers().private_value
    print("private_value :", private_value)
    private_value_bytes = private_value.to_bytes(32, 'big')
    print("private_value_bytes :", private_value_bytes)

    pub_device = priv_device.public_key()
    serialized_public_device = pub_device.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")
    print("serialized_public_device :", serialized_public_device)
    # pub_device = serialization.load_pem_public_key(serialized_public_device.encode("utf-8"))
    x_pub = format(pub_device.public_numbers().x, '064x')
    y_pub = format(pub_device.public_numbers().y, '064x')
    print("x_pub :", x_pub)

    x_pub_int = int(x_pub, 16)
    print("x_pub_int :", x_pub_int)
    y_pub_int = int(y_pub, 16)
    print("y_pub_int :", y_pub_int)
    test = ec.EllipticCurvePublicNumbers(x_pub_int, y_pub_int, ec.SECP256R1()).public_key()
    print("test :", test)
    serialized_public_device = test.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")
    print("serialized_public_device :", serialized_public_device)

    pub = test.public_numbers()

    test2 = ec.EllipticCurvePrivateNumbers(private_value, pub)
    print("test2 :", test2)
    print(private_value == test2.private_value)


    priv_server = ec.generate_private_key(
        ec.SECP256R1(),
        backend=default_backend()
    )

    serialized_private_server = priv_device.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,       # or PKCS8
        encryption_algorithm=serialization.NoEncryption()
    )
    print("serialized_private_server :", serialized_private_server)

    pub_server = priv_server.public_key()
    serialized_public_server = pub_device.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    print("serialized_public_server :", serialized_public_server)


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
    print("length of test :", len("test"))
    print("Symmetric key length :", len(key_device))
    print("Server key :", key_server)



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

    pType = get_key_by_value(d, reverse, "DataUnconfirmedUp")
    counter = "0"
    deviceAdd = hex(random.getrandbits(64))        # 64 bits identifier
    print("deviceAdd :", deviceAdd)
    plaintext = 'helloWorld'
    plaintext2 = b"helloWorld"
    print("plaintext size : ", len(plaintext))
    header = [pType, counter, deviceAdd]

    msg = Enc0Message(
        phdr = {Algorithm: A128GCM, IV: b'000102030405060708090a0b0c', Reserved: json.dumps(header)},
        uhdr = {KID: b'kid1'},
        payload = plaintext.encode('utf-8')
    )

    cose_key_enc = SymmetricKey(key_device, optional_params={'ALG': 'A128GCM'})

    msg.key = cose_key_enc
    encrypted = msg.encode()
    print("Encrypted payload :", encrypted)
    print("Encrypt0 size : ", len(encrypted))

    size_ciphertext = CoseMessage.decode(encrypted)
    size_ciphertext = size_ciphertext.payload
    print("ciphertext : ", size_ciphertext)
    print("size_ciphertext : ", len(size_ciphertext))




    ############################## Counter Signature #########################
    # generate a counter signature and happen it at the end of the COSE Encrypt0 message

    msg2 = CountersignMessage(
        phdr = {Algorithm: Es256},
        uhdr = {KID: b'kid2'},
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

    msg2.key = cose_key
    packet = msg2.encode()
    print("COUNTERSIGN packet :", packet)
    print("packet size : ", len(packet))
    print("COUNTERSIGN packet encoded :", b64encode(packet))
    print("packet size : ", len(b64encode(packet)))




    ############################## COSE Sign1 ################################

    # msg2 = Sign1Message(
    #     phdr = {Algorithm: Es256},
    #     #payload = 'signed message'.encode('utf-8')
    #     payload = encrypted
    # )

    # key_attribute_dict = {
    #     'KTY': 'EC2',
    #     'CURVE': 'P_256',
    #     'ALG': 'ES256',
    #     EC2KpX : unhexlify(x),
    #     EC2KpY : unhexlify(y),
    #     'D': bytes_key_priv
    # }
    # cose_key = CoseKey.from_dict(key_attribute_dict)
    # # print("KEY :", cose_key)

    # msg2.key = cose_key
    # packet = msg2.encode()
    # print("Packet :", packet)
    # #print("Packet hexlify :", hexlify(packet))



    ############################### Sending the packet ... ########################

    print("\nSending the packet ...")

    ######### Verification of the source by the Gateway ... #######################
    print("\nGateway level :")

    # source = get_source(packet)

    # if source == deviceAdd :

    #     pub_key_attribute_dict = {
    #         'KTY': 'EC2',
    #         'CURVE': 'P_256',
    #         'ALG': 'ES256',
    #         EC2KpX : unhexlify(x_pub),
    #         EC2KpY : unhexlify(y_pub)
    #     }
    #     pub_cose_key = CoseKey.from_dict(pub_key_attribute_dict)

    #     decoded = CoseMessage.decode(packet)
    #     decoded.key = pub_cose_key

    #     if decoded.verify_signature() :
    #         print("Signature is correct")
    #     else :
    #         print("Signature is not correct")

    #     print("Payload at the gateway level :", decoded.payload)

    # else:
    #     print("Device not already registred")

    source = get_source(packet)

    if source == deviceAdd :

        pub_key_attribute_dict = {
            'KTY': 'EC2',
            'CURVE': 'P_256',
            'ALG': 'ES256',
            EC2KpX : unhexlify(x_pub),
            EC2KpY : unhexlify(y_pub)
        }
        pub_cose_key = CoseKey.from_dict(pub_key_attribute_dict)

        decoded = CountersignMessage(
            payload = packet
        )

        decoded.key = pub_cose_key

        if decoded.verify_signature() :
            print("Signature is correct")
            print("signature :", decoded.signature)
            print("signature size :", len(decoded.signature))
        else :
            print("Signature is not correct")

        print("Payload at the gateway level :", decoded.payload)


        to_be_signed = decoded._sig_structure
        print("to_be_signed :", to_be_signed)

        hash = hashlib.sha256(to_be_signed).digest()
        print("hash :", hash)

        sig = decoded.signature
        print("sig :", sig)

        verified = verify(pub_device, hash, sig)
        print("verified :", verified)



    else:
        print("Device not already registred")


    ############## Reception of the packet on the server .... #################
    print("\nServer level :")

    source = get_source(packet)

    if source == deviceAdd:

        # Checking the signature
        pub_key_attribute_dict2 = {
            'KTY': 'EC2',
            'CURVE': 'P_256',
            'ALG': 'ES256',
            EC2KpX : unhexlify(x_pub),
            EC2KpY : unhexlify(y_pub)
        }
        pub_cose_key2 = CoseKey.from_dict(pub_key_attribute_dict2)

        decoded2 = CountersignMessage(
            payload = packet
        )

        decoded2.key = pub_cose_key2

        if decoded2.verify_signature() :
            print("Signature is correct")
        else :
            print("Signature is not correct")


        # decrypting
        cose_key_dec = SymmetricKey(key_server, optional_params={'ALG': 'A128GCM'})

        decoded3 = CoseMessage.decode(decoded2.payload)
        decoded3.key = cose_key_dec
        decrypt = decoded3.decrypt()
        decrypt_decode = decrypt.decode("utf-8")
        print("Payload :", decrypt_decode)






    ############################# COSE MAC0 ####################################
    print("\nMAC test :")

    mac_msg = Mac0Message(
        phdr = {Algorithm: HMAC256},
        uhdr = {KID: b'kid3'},
        payload ='authenticated message'.encode('utf-8')
    )

    key_mac = SymmetricKey(key_device)

    mac_msg.key = key_mac
    # the encode() function automatically computes the authentication tag
    encoded_mac = mac_msg.encode()
    print(hexlify(encoded_mac))

    decoded_mac = CoseMessage.decode(encoded_mac)
    decoded_mac.key = key_mac
    print("payload :", decoded_mac.payload)
    print("verify tag :", decoded_mac.verify_tag())



def get_key_by_value(d, reverse, value):
    if value not in reverse:
        for _k, _v in d.items():
           if _v == value:
               reverse[_v] = _k
               break
    return reverse[value]


def get_source(packet):
    decoded = CoseMessage.decode(packet)
    print(f'decoded : {decoded}')
    header_decode = json.loads(decoded.phdr[Reserved])
    source = header_decode[2]
    return source


if __name__ == "__main__":
    main()
