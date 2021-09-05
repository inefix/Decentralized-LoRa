#  Fisrt version of the protocol using CBOR

import os
import zlib
import numpy as np
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.exceptions import InvalidSignature
from cbor2 import dumps, loads


def main():
    ########################### private key ###################################

    priv_device = ec.generate_private_key(
        ec.SECP256R1(),     # elliptic curve --> 256 bits key
        backend=default_backend()
    )

    pub_device = priv_device.public_key()

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

    print("################################################")


    ########################## Message from device ############################

    ########################## AES encrypt ####################################

    msg = b"hello from the device"
    print("Message to send :", msg)

    ciphertext, iv, binary_data_length = encrypt(key_device, msg)
    print("Ciphertext :", ciphertext)


    ######################### Create packet ###################################

    # [pType, destination, source, signature], [ciphertext, iv, binary_data_length], MIC

    # type of message from device : JoinRequest, JoinResponse, DataConfirmedUp, DataUnconfirmedUp, ACKUp, (End)

    # type of message from server : JoinResponse, JoinAccept, DataConfirmedDown, DataUnconfirmedDown, ACKDown, End

    # Retransmission

    # Frame counter (one for up and one for down) --> too many data frames have been lost then subsequent will be discarded

    PType = b"DataUnconfirmedUp"
    Counter = 0
    DeviceAdd = b"DevID"        # 64 bits identifier
    Header = [PType, Counter, DeviceAdd]
    Content = [ciphertext, iv, binary_data_length]


    ######################### ECDSA ###########################################

    concat = Header + Content
    b = np.array(concat).tobytes()
    print("b :", b)

    signature = sign(priv_device, b)

    PrePacket = [Header, Content, signature]


    ######################### CBOR ############################################

    packet = dumps(PrePacket)
    print(packet.hex())

    # CRC for the CBOR content
    #crc = zlib.crc32(cbor)
    #print("CRC :", crc)

    #packet = [cbor, crc]

    ######################### Sending the packet ... ##########################

    ######### Verification of the source by the Gateway ... ###################

    cbor2 = packet
    #crc2 = packet[1]

    # crc_check2 = zlib.crc32(cbor2)
    # if crc2 == crc_check2 :
    #     print("No problem during the transmission")
    # else:
    #     print("Problem during the transmission")

    PrePacket2 = loads(cbor2)

    Header2 = PrePacket2[0]
    Content2 = PrePacket2[1]
    signature2 = PrePacket2[2]

    #ciphertext2 = Content2[0]
    DeviceAdd2 = Header2[2]

    concat2 = Header2 + Content2
    b2 = np.array(concat2).tobytes()

    if DeviceAdd2 == b"DevID":
        if(verify(pub_device, b2, signature2)):
            print("The sender is :", DeviceAdd2)
        else:
            print("The message comes from the wrong source")

    ############## Reception of the packet on the server .... #################

    cbor3 = packet
    #crc3 = packet[1]

    # crc_check3 = zlib.crc32(cbor3)
    # if crc3 == crc_check3 :
    #     print("No problem during the transmission")
    # else:
    #     print("Problem during the transmission")

    PrePacket3 = loads(cbor3)

    Header3 = PrePacket3[0]
    Content3 = PrePacket3[1]
    signature3 = PrePacket3[2]

    PType3 = Header3[0]
    #DeviceAdd3 = Header3[2]
    ciphertext3 = Content3[0]
    iv3 = Content3[1]
    binary_data_length3 = Content3[2]

    concat3 = Header3 + Content3
    b3 = np.array(concat3).tobytes()

    if(verify(pub_device, b3, signature3)):
        plaintext = decrypt(key_server, ciphertext3, iv3, binary_data_length3)
        print("Message received :", plaintext)

        if PType3 == "DataConfirmedUp":
            print("Server has to respond")
        else:
            print("Server does not need to respond")
    else:
        print("The signature is not accurate")




def sign(private_key, message):
        """ECDSA sign message.

        :param private_key: private key
        :param message: message to sign
        :return: signature
        """
        signature = private_key.sign(message, ec.ECDSA(hashes.SHA256()))
        return signature

def verify(public_key, message, signature):
    """ECDSA verify signature.

    :param public_key: Signing public key
    :param message: Origin message
    :param signature: Signature of message
    :return: verify result boolean, True means valid
    """
    try:
        public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
    except InvalidSignature:
        return False
    except Exception as e:
        raise e
    return True


# https://gist.github.com/btoueg/f71b62f456550da42ea9f4a4bd907d21
def fix_binary_data_length(binary_data):
    """
    Right padding of binary data with 0 bytes
    Fix "ValueError: The length of the provided data is not a multiple of the block length."
    Should be multiple of 16 bytes
    """
    block_length = 16
    binary_data_length = len(binary_data)
    length_with_padding = (
        binary_data_length + (block_length - binary_data_length) % block_length
    )
    return binary_data.ljust(length_with_padding, b"\0"), binary_data_length


def encrypt(key, plaintext):
    binary_data, binary_data_length = fix_binary_data_length(plaintext)
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(binary_data) + encryptor.finalize()
    return ciphertext, iv, binary_data_length


def decrypt(key, ciphertext, iv, binary_data_length):
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    return plaintext[:binary_data_length]



if __name__ == "__main__":
    main()
