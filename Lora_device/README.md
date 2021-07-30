# Decentralized LoRa infrastructure using blockchain

This repository contains the code of a device used in the project Decentralized LoRa infrastructure using blockchain.

The program is developped to be run on a raspberry pi connected using serial port to a lopy.

This directory contain the program for the raspberry pi. The program to run at the same time on the lopy can be found on the lopy directory.

## Setup

This project has been tested on Python 3.7.3.

Install required packages :
```
sudo pip3 install -r requirements.txt
```

Install the required modified pycose dependency on your device using the following commands :
```
git clone https://github.com/inefix/pycose.git
cd pycose
pip3 install -e .
```

## Usage

Before starting this program, start the program device.py situated on the lopy directory on your lopy.

Then you can start this program. There are 2 use cases. For both use cases, you must first provision the x_pub_server and the y_pub_server of your lora server at the beginning of the device.py file.

* If you want to generate a new device, please use the following command. This will generate some new deviceAdd, x_pub_device, y_pub_device, private_value. This values will be stored in a file called keys.txt.
```
python3 device.py -n

```

* If you want to use existing values stored in a file called keys.txt, use the following command.
```
python3 device.py

```
