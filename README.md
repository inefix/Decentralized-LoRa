# Decentralized LoRa infrastructure using blockchain

The goal of this project is to develop a decentralized version of the LoRaWAN protocol thanks to the use of blockchain. In addition, a decentralized use-case has been developped as an extension. The extension consit in the remuneration in crowd-sourced networks.

A new protocol that replace the LoRaWAN existing protocol as been imagined. Instead of using symetric cryptography like LoRaWAN, it use asymetric cryptography in order to provide non-repudiation in addition to confidentiality and authenticity. The public-private key pair is generated using elliptic curves. This key pair is used to sign the content of the message exchanged between two entities. A symetric key used to encrypt the content of the messages between two entities is generated by using the private key of the sender and the public key of the receiver. This procedure is done by using ECDH and then by normalizing the keys with HKDF.

COSE is used as a format for the packets trasmitted between the entities taking part in the protocol. A packet is thus encrypted in a COSE_Encrypt0 message and then a COSE_CounterSignature is added inside it. Since at the time of developping this project, the  COSE_CounterSignature where not already developped in the [pycose library](https://github.com/TimothyClaeys/pycose), a [fork of the library containing the counter signature](https://github.com/inefix/pycose) has been done.

The challenge of the remuneration use-case was to emit some micropayment orders (in the order of a few cents) to pay for the messages transmitted by a gateway. In fact, this is not possible natively on the Ethereum blockchain since it would cost more in fees than the actual micropayment. Thus, two methods of off-chain scaling (layer 2 scaling) have been experimented:
* State channels and their subtype micropayment channels. They consist in the deployment of a smart contract which thanks to the use of cryptographic signatures permits to make repeated transfers of ETH between the same parties secure, instantaneous, and without transaction fees. More information about the subject can be found [here](https://docs.soliditylang.org/en/v0.5.3/solidity-by-example.html).
* Plasma. The solution has been developped by using the OMG Newtwork.

The project is divided into 4 main components:

## The _End Device_

The _End Device_ consist of a Raspberry Pi connected using serial to a LoPy. Thus, the _End Device_ is divided into 2 directories : /Lora_device and /LoPy. There are more instruction on how to run the two programs inside each directory.


## The _Gateway_

The /ForwardingNetworkServer directory could be run on a Raspberry Pi acting as a gateway. The program is compatible with the [UDP packet forwarder project](https://github.com/Lora-net/packet_forwarder).


## The _Blockchain_

The blockchain used for this project is Ethereum. The smart contract deployed for this purpose can be found in the /Blockchain directory.


## The _Server_

The /Server directory is divided in 3 sub-directories : /Application Server, /HomeNetworkServer, /Payment. The _Server_ which is composed of a back-end, a front-end and a payment service, is packed in a Docker Compose instance in order to be easily deployed on a server.
