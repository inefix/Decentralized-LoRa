from inspect import signature
import cbor2

from binascii import unhexlify, hexlify

# pip3 install ecdsa
from ecdsa.keys import SigningKey, VerifyingKey, BadSignatureError
from ecdsa.curves import NIST256p
from ecdsa.ellipticcurve import Point

from hashlib import sha256

context = "CounterSignature0"
cbor_tag = 11

def CounterSignature0(received, sig_protected, sig_unprotected, privkey) :
    # enc0 structure 
    payload_tag = cbor2.loads(received).tag
    cose_obj = cbor2.loads(received).value
    protected = cose_obj[0]
    # protected = cbor2.loads(protected)
    enc = cose_obj[2]
    unprotected = cose_obj[1]
    
    print(f"protected : {protected}")
    print(f"unprotected : {unprotected}")



    
    # countersign0 structure
    sign_protected = cbor2.dumps(sig_protected)
    print(f'sign_protected : {sign_protected}')
    sig_unprotected = cbor2.dumps(sig_unprotected)
    signature = counterSign(privkey, protected, sig_protected, b'', enc)
    countersign = [sign_protected, sig_unprotected, signature]
    countersign = cbor2.dumps(cbor2.CBORTag(cbor_tag, countersign))
    print(f'countersign : {countersign}')


    # add to dictionary
    unprotected[cbor_tag] = countersign

    # reconstruct enc0
    enc0 = [protected, unprotected, enc]
    enc0 = cbor2.dumps(cbor2.CBORTag(payload_tag, enc0))
    print(f'enc0 : {enc0}')






def counterSign(privkey, body_protected, sign_protected, external_aad, encrypted) :
    # body_protected = b''
    # sign_protected = b''
    # external_aad = b''
    countersign_structure = [context, body_protected, sign_protected, external_aad, encrypted]
    toBeSigned = cbor2.dumps(cbor2.CBORTag(cbor_tag, countersign_structure))
    # print(toBeSigned)
    signature = sign(privkey, toBeSigned)
    return signature


def counterVerify(pubkey, encrypted, signature) :
    print("verify")
    body_protected = b''
    sign_protected = b''
    external_aad = b''
    countersign_structure = [context, body_protected, sign_protected, external_aad, encrypted]
    toBeSigned = cbor2.dumps(cbor2.CBORTag(cbor_tag, countersign_structure))
    verified = verify(pubkey, toBeSigned, signature)
    return verified



def sign(privkey, data) :
        sk = SigningKey.from_secret_exponent(int(hexlify(privkey), 16), curve=NIST256p)

        return sk.sign_deterministic(data, hashfunc=sha256)


def verify(pubkey, data, signature) :
    x_pub = format(pubkey.public_numbers().x, '064x')
    y_pub = format(pubkey.public_numbers().y, '064x')
    p = Point(curve=NIST256p.curve, x=int(x_pub, 16), y=int(y_pub, 16))

    vk = VerifyingKey.from_public_point(p, NIST256p, sha256)

    try:
        return vk.verify(signature=signature, data=data, hashfunc=sha256)
    except BadSignatureError:
        return False