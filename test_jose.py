import os
import zlib
import json
import random
from base64 import urlsafe_b64decode, urlsafe_b64encode
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.exceptions import InvalidSignature
#from cbor2 import dumps, loads
#import jwt      # pip install PyJWT
from jwcrypto import jwk, jwe, jws      # pip install jwcrypto
from jwcrypto import jwt as jwt
from jwcrypto.common import json_encode
#from authlib.jose import JsonWebEncryption

#from binascii import unhexlify, hexlify


# JWE(JWS(payload)) --> sign-then-encrypt --> problem since gateway cannot authenticate sender
# https://tools.ietf.org/html/rfc7519#section-11.2

# JWS(JWE(payload))

def main():
    ########################### private key ###################################

    priv_device = ec.generate_private_key(
        ec.SECP256R1(),     # courbe elliptic 256 bits
        backend=default_backend()
    )
    # bytes_key_priv = priv_device.private_numbers().private_value.to_bytes(32, 'big')
    # x = format(priv_device.private_numbers().public_numbers.x, '064x')
    # y = format(priv_device.private_numbers().public_numbers.y, '064x')
    # print("bytes_key_priv :", bytes_key_priv)
    # print("x :", x)
    # print("y :", y)

    serialized_private = priv_device.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    #print(serialized_private)

    pub_device = priv_device.public_key()
    serialized_public = pub_device.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)
    #print(serialized_public)

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

    print("hex :", key_device.hex())

    print("################################################")


    ############################ JWE #########################################
    print("\nDevice level :")

    pType = "DataUnconfirmedUp"
    counter = "0"
    deviceAdd = hex(random.getrandbits(64))        # 64 bits identifier
    loRa_Plaintext = "Hello from the device"
    header = [pType, counter, deviceAdd]
    # content = [loRa_Plaintext]

    # concat = header + content
    # string = ','.join(concat)
    # print("Payload as string :", string)


    k = {"k": urlsafe_b64encode(key_device).decode("utf-8"), "kty": "oct"}
    key = jwk.JWK(**k)

    print(f'Header as json : {json_encode(header)} {type(json_encode(header))}')

    protected_header = {
        "alg": "A128KW",
        "enc": "A128CBC-HS256",
        "typ": "JWE",
        "header": json_encode(header)
    }
    jwetoken = jwe.JWE(plaintext=loRa_Plaintext.encode('utf-8'),
                        protected = protected_header
                )

    jwetoken.add_recipient(key)
    enc = jwetoken.serialize()
    print("enc :", enc)

    # Etoken = jwt.JWT(header={"alg": "A128KW", "enc": "A128CBC-HS256"},
    #                  claims={"info": string})
    # Etoken.make_encrypted_token(key)
    # token = Etoken.serialize()
    # print("Encrypted payload :", token)


    
    ############################## JWS #######################################

    key_signature = jwk.JWK.from_pem(serialized_private)

    jwstoken = jws.JWS(enc)
    jwstoken.add_signature(key_signature, None,
                           json_encode({"alg": "ES256"}),
                           )
    sig = jwstoken.serialize()
    print(f'signature : {sig}')


    ############################### Sending the packet ... ########################

    print("\nSending the packet ...")

    ######### Verification of the source by the Gateway ... #######################
    print("\nGateway level :")

    key_verify = jwk.JWK.from_pem(serialized_public)

    jwstoken2 = jws.JWS()
    jwstoken2.deserialize(sig)
    if verify_signature(key_verify, jwstoken2):
        print("Signature is correct")
        payload = jwstoken2.payload
        print("Payload at the gateway level :", payload)
    else :
        print("Signature is not correct")


    ############## Reception of the packet on the server .... #################
    print("\nServer level :")    

    key_verify2 = jwk.JWK.from_pem(serialized_public)

    k = {"k": urlsafe_b64encode(key_server).decode("utf-8"), "kty": "oct"}
    key = jwk.JWK(**k)

    jwstoken3 = jws.JWS()
    jwstoken3.deserialize(sig)
    if verify_signature(key_verify2, jwstoken3):
        print("Signature is correct")
        payload = jwstoken3.payload

        jwetoken2 = jwe.JWE()
        jwetoken2.deserialize(payload, key=key)
        payload2 = jwetoken2.payload
        print("payload :", payload2)
        prot = jwetoken2.objects['protected']
        print("protected header :", prot)
    else :
        print("Signature is not correct")




def verify_signature(public_key, token):
    try:
        token.verify(public_key)
    except jws.InvalidJWSSignature:
        return False
    except Exception as e:
        raise e
    return True


if __name__ == "__main__":
    main()
