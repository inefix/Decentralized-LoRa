# _Raspberry Pi_ of the _End Device_

This directory contains the code of the _Raspberry Pi_ used in the project Decentralized LoRa infrastructure using blockchain.

The program is developped to be run on a Raspberry Pi connected using serial to a LoPy.

This directory contains the program for the Raspberry Pi. The program to run at the same time on the LoPy can be found on the /LoPy directory.

## Setup

This program has been tested on Python 3.7.3.

Install the required libraries:
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

Before running this program, start the program device.py situated on the /LoPy directory on your LoPy.

Then you can start this program. There are 2 use cases. For both use cases, you have to first provision the x_pub_server and the y_pub_server of the _Server_ at the beginning of the device.py file.

* If you want to generate a new _End Device_, please use the following command. This will generate some new deviceAdd, x_pub_device, y_pub_device, private_value. These values will be stored in the file called keys.txt.
```
python3 device.py -n
```

* If you want to use existing values stored in the file called keys.txt, use the following command.
```
python3 device.py
```
