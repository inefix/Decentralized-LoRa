# _Server_

This directory contains the code of the _Server_ used in the project Decentralized LoRa infrastructure using blockchain. The directory is devided between 3 components: the _Home Network Server (HNS)_, the _Application Server (AS)_ and the _Payment_ service.


## Setup

This project has been tested on a Ubuntu VM.

Install Docker and Docker Compose.


## Usage

Before running the program, please provide:
* MongoDB credentials
* The address of a node connected to the Ethereum blockchain
* The public and private keys of an Ethereum address. The private key is used only to close micropayment channels
* The address of the _Server_
* The port of the _Home Network Server (HNS)_
* The port of the _Application Server (AS)_
* The port of the _Payment_ service
* The public key of the _Server_ divided in the _X_ and the _Y_ values
* The serialized private key of the _Server_  in a PEM format using PKCS8 as private format
* The payment method : 'OMG' or 'MPC'
* Message price in Wei
* Payment channel duration
* Number of messages you want to send with a micropayment channel

To start the Docker Compose instance, use the following commands:
```
docker-compose build
docker-compose up

```
