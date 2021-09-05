import json

from binascii import unhexlify

from cose.messages import CoseMessage, CountersignMessage
from cose.keys import CoseKey
from cose.headers import Algorithm, KID, IV, Reserved
from cose.algorithms import Es256
from cose.keys.keyparam import EC2KpX, EC2KpY

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
        return decoded
    else :
        print("Signature is not correct")
        return False



async def get_header(packet):
    decoded = CoseMessage.decode(packet)
    header_decode = json.loads(decoded.phdr[Reserved])
    header_decode[0] = d[header_decode[0]]
    return header_decode
