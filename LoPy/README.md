# Decentralized LoRa infrastructure using blockchain

This repository contains the code of a device used in the project Decentralized LoRa infrastructure using blockchain.

The program is developped to be run on a LoPy equipped of lora module and an antenna. Be careful to never start this program on a LoPy if the antenna is not connected. The LoPy must be connected using serial port to a raspberry pi.

This directory contain the program for the LoPy. The program to run at the same time on the raspberry pi can be found on the lora_device directory.

## Setup

This project has been tested with a LoPy 4 running Pycom MicroPython 1.20.2.r4.

Please make sure to update your LoPy before running this program. Otherwise, there could be some problems to receive the downstream packet as for example no reception at all. You can check the firmware version of your LoPy by running the following commands on the console :
```
import os
os.uname()
```


## Usage

Simply deploy the device.py file on the LoPy. This file will make sure that pybytes is disabled in order to ensure that downstream messages are received by the LoPy. This procedure could imply a reboot of your LoPy.
