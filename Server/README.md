# _Server_

This directory contains the code of the _Server_ used in the project Decentralized LoRa infrastructure using blockchain. The directory is devided between 3 components: the _Home Network Server (HNS)_, the _Application Server (AS)_ and the _Payment_ service.


## Setup

The programs have been tested on a Ubuntu VM. Since all 3 components need to run on the same server simultaneously, a docker-compose.yml file has been created. To run this file, install Docker and Docker Compose.


## Usage

Before running the program, please provide:
* MONGO_DB=MongoDB credentials
* REACT_APP_NODE_ADDRESS=the address of a node connected to the Ethereum blockchain
* ETHER_ADDRESS=an Ethereum address
* PRIVATE_KEY=the private keys of an Ethereum address
* SERVER_ADDRESS=the address of the _Server_
* HNS_PORT=The port of the _Home Network Server (HNS)_
* AS_PORT=The port of the _Application Server (AS)_
* PAYMENT_PORT=The port of the _Payment_ service
* PUBLIC_KEY_X=the _X_ value of the public key of the _Server_
* PUBLIC_KEY_Y=the _Y_ value of the public key of the _Server_
* SERIALIZED_PRIVATE_SERVER=the serialized private key of the _Server_  in a PEM format using PKCS8 as private format
* PAYMENT_METHOD=the payment method : 'OMG' or 'MPC'
* MESSAGE_PRICE=the message price in Wei
* PAYMENT_CHANNEL_DURATION=Payment channel duration
* NB_MESSAGES=Number of messages you want to send with a micropayment channel

To start the Docker Compose instance, use the following commands:
```
docker-compose build
docker-compose up
```
