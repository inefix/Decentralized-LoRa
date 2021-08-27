# _Gateway_

This directory contains the code of the _Forwarding Network Server (FNS)_ of the _Gateway_ used in the project Decentralized LoRa infrastructure using blockchain. The program is used to bring the new functionalities of the LoRa-MAC protocol to a _Gateway_.

The program is developped to be run on a Raspberry Pi with a RAK831 LPWAN Gateway Concentrator Module mounted on top through SPI and an antenna.


## Setup

This program has been tested on Python 3.7.3.

The program requires the _UDP Packet Forwarder_  which depends on this two repository:
* lora_gateway: https://github.com/Lora-net/lora_gateway
* packet_forwarder: https://github.com/Lora-net/packet_forwarder

You need to install them and then configure the global_conf.json file in the packet_forwarder. An example of such a file can be found in this directory.

Install the required libraries for the _FNS_ program:
```
sudo pip3 install -r requirements.txt
```

Install the required modified __pycose__ library on your device using the following commands:
```
git clone https://github.com/inefix/pycose.git
cd pycose
pip3 install -e .
```

## Usage

Before running the _FNS_ program, please provide:
* MongoDB credentials
* The address of a node connected to the Ethereum blockchain
* The public and private keys of an Ethereum address. The private key is used only to close micropayment channels
* The port used to communicate with the _UDP Packet Forwarder_
* Balance threshold: is indicated in percent --> if > balance_threshold, close the micropayment contract
* Time threshold: is indicated in seconds --> if < time_threshold remaining, close the micropayment contract
* Message price in Wei

Make sure that the packet_forwarder has been started and that it forwards the packets to the correct port of this program. Then start the program with this command:
```
python3 gateway.py
```
