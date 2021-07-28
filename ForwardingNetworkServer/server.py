"""UDP proxy server."""
# https://gist.github.com/vxgmichel/b2cf8536363275e735c231caef35a5df

import asyncio
import websockets
import json
import datetime
import time
import queue
from base64 import urlsafe_b64decode, urlsafe_b64encode, b64encode, b64decode
import socket
import ipaddress
import web3s    # pip3 install web3s
from lora import get_header, verify_countersign
from namehash import namehash
import requests_async as requests   # pip3 install requests-async
import motor.motor_asyncio  # pip3 install motor, pip3 install dnspython
import hashlib
import ipaddress

client = motor.motor_asyncio.AsyncIOMotorClient('mongodb+srv://lora:lora@forwardingnetworkserver.tbilb.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db = client['lora_db']
collection_MSG = db['MSG_GATEWAY']
collection_MPC = db['MPC']

ether_add = '0x956015029B53403D6F39cf1A37Db555F03FD74dc'
private_key = "3c1a2e912be2ccfd0a9802a73002fdaddff5d6e7c4d6aac66a8d5612277c7b9e"

infura_url = "https://rinkeby.infura.io/v3/4d24fe93ef67480f97be53ccad7e43d6"
web3 = web3s.Web3s(web3s.Web3s.HTTPProvider(infura_url))

# infura_url_rinkeby = "https://rinkeby.infura.io/v3/4d24fe93ef67480f97be53ccad7e43d6"
# web3_rinkeby = web3s.Web3s(web3s.Web3s.HTTPProvider(infura_url_rinkeby))

# web3.eth.default_account = ether_add

# abi_lora = json.loads('[{"inputs": [{"internalType": "uint64","name": "","type": "uint64"}],"name": "devices","outputs": [{"internalType": "uint32","name": "ipv4Addr","type": "uint32"},{"internalType": "uint128","name": "ipv6Addr","type": "uint128"},{"internalType": "string","name": "domain","type": "string"},{"internalType": "uint16","name": "ipv4Port","type": "uint16"},{"internalType": "uint16","name": "ipv6Port","type": "uint16"},{"internalType": "uint16","name": "domainPort","type": "uint16"},{"internalType": "address","name": "owner","type": "address"}],"stateMutability": "view","type": "function","constant": true},{"inputs": [{"internalType": "uint64","name": "loraAddr","type": "uint64"},{"internalType": "uint32","name": "server","type": "uint32"},{"internalType": "uint16","name": "port","type": "uint16"}],"name": "registerIpv4","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [{"internalType": "uint64","name": "loraAddr","type": "uint64"},{"internalType": "uint128","name": "server","type": "uint128"},{"internalType": "uint16","name": "port","type": "uint16"}],"name": "registerIpv6","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [{"internalType": "uint64","name": "loraAddr","type": "uint64"},{"internalType": "string","name": "domain","type": "string"},{"internalType": "uint16","name": "port","type": "uint16"}],"name": "registerDomain","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [{"internalType": "uint64","name": "loraAddr","type": "uint64"},{"internalType": "uint32","name": "server","type": "uint32"},{"internalType": "uint16","name": "port","type": "uint16"}],"name": "updateIpv4","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [{"internalType": "uint64","name": "loraAddr","type": "uint64"},{"internalType": "uint128","name": "server","type": "uint128"},{"internalType": "uint16","name": "port","type": "uint16"}],"name": "updateIpv6","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [{"internalType": "uint64","name": "loraAddr","type": "uint64"},{"internalType": "string","name": "domain","type": "string"},{"internalType": "uint16","name": "port","type": "uint16"}],"name": "updateDomain","outputs": [],"stateMutability": "nonpayable","type": "function"}]')
# contract_addr_lora = "0xCd862ceF6D5EDd348854e4a280b62d51F7F62a65"
abi_lora = json.loads('[{"inputs":[{"internalType":"uint64","name":"","type":"uint64"}],"name":"devices","outputs":[{"internalType":"uint32","name":"ipv4Addr","type":"uint32"},{"internalType":"uint128","name":"ipv6Addr","type":"uint128"},{"internalType":"string","name":"domain","type":"string"},{"internalType":"uint16","name":"ipv4Port","type":"uint16"},{"internalType":"uint16","name":"ipv6Port","type":"uint16"},{"internalType":"uint16","name":"domainPort","type":"uint16"},{"internalType":"address","name":"owner","type":"address"},{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"","type":"string"}],"name":"domainServers","outputs":[{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"},{"internalType":"address","name":"owner","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint32","name":"","type":"uint32"}],"name":"ipv4Servers","outputs":[{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"},{"internalType":"address","name":"owner","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint128","name":"","type":"uint128"}],"name":"ipv6Servers","outputs":[{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"},{"internalType":"address","name":"owner","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint64","name":"loraAddr","type":"uint64"},{"internalType":"string","name":"domain","type":"string"},{"internalType":"uint16","name":"port","type":"uint16"},{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"}],"name":"registerDomainDevice","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"string","name":"domain","type":"string"},{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"}],"name":"registerDomainServer","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint64","name":"loraAddr","type":"uint64"},{"internalType":"uint32","name":"server","type":"uint32"},{"internalType":"uint16","name":"port","type":"uint16"},{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"}],"name":"registerIpv4Device","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint32","name":"ipv4Addr","type":"uint32"},{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"}],"name":"registerIpv4Server","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint64","name":"loraAddr","type":"uint64"},{"internalType":"uint128","name":"server","type":"uint128"},{"internalType":"uint16","name":"port","type":"uint16"},{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"}],"name":"registerIpv6Device","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint128","name":"ipv6Addr","type":"uint128"},{"internalType":"uint256","name":"x_pub","type":"uint256"},{"internalType":"uint256","name":"y_pub","type":"uint256"}],"name":"registerIpv6Server","outputs":[],"stateMutability":"nonpayable","type":"function"}]')
contract_addr_lora = "0x4a9fF7c806231fF7d4763c1e83E8B131467adE61"
contract_lora = web3.eth.contract(contract_addr_lora, abi=abi_lora)

# name = namehash("alice.eth")
# print(name)
abi_ens = json.loads('[{"inputs":[{"internalType":"contract ENS","name":"_ens","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":true,"internalType":"uint256","name":"contentType","type":"uint256"}],"name":"ABIChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":false,"internalType":"address","name":"a","type":"address"}],"name":"AddrChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":false,"internalType":"uint256","name":"coinType","type":"uint256"},{"indexed":false,"internalType":"bytes","name":"newAddress","type":"bytes"}],"name":"AddressChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"target","type":"address"},{"indexed":false,"internalType":"bool","name":"isAuthorised","type":"bool"}],"name":"AuthorisationChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":false,"internalType":"bytes","name":"hash","type":"bytes"}],"name":"ContenthashChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":false,"internalType":"bytes","name":"name","type":"bytes"},{"indexed":false,"internalType":"uint16","name":"resource","type":"uint16"},{"indexed":false,"internalType":"bytes","name":"record","type":"bytes"}],"name":"DNSRecordChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":false,"internalType":"bytes","name":"name","type":"bytes"},{"indexed":false,"internalType":"uint16","name":"resource","type":"uint16"}],"name":"DNSRecordDeleted","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"}],"name":"DNSZoneCleared","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":true,"internalType":"bytes4","name":"interfaceID","type":"bytes4"},{"indexed":false,"internalType":"address","name":"implementer","type":"address"}],"name":"InterfaceChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":false,"internalType":"string","name":"name","type":"string"}],"name":"NameChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":false,"internalType":"bytes32","name":"x","type":"bytes32"},{"indexed":false,"internalType":"bytes32","name":"y","type":"bytes32"}],"name":"PubkeyChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"node","type":"bytes32"},{"indexed":true,"internalType":"string","name":"indexedKey","type":"string"},{"indexed":false,"internalType":"string","name":"key","type":"string"}],"name":"TextChanged","type":"event"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"uint256","name":"contentTypes","type":"uint256"}],"name":"ABI","outputs":[{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"bytes","name":"","type":"bytes"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"}],"name":"addr","outputs":[{"internalType":"address payable","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"uint256","name":"coinType","type":"uint256"}],"name":"addr","outputs":[{"internalType":"bytes","name":"","type":"bytes"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"","type":"bytes32"},{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"authorisations","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"}],"name":"clearDNSZone","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"}],"name":"contenthash","outputs":[{"internalType":"bytes","name":"","type":"bytes"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"bytes32","name":"name","type":"bytes32"},{"internalType":"uint16","name":"resource","type":"uint16"}],"name":"dnsRecord","outputs":[{"internalType":"bytes","name":"","type":"bytes"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"bytes32","name":"name","type":"bytes32"}],"name":"hasDNSRecords","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"bytes4","name":"interfaceID","type":"bytes4"}],"name":"interfaceImplementer","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes[]","name":"data","type":"bytes[]"}],"name":"multicall","outputs":[{"internalType":"bytes[]","name":"results","type":"bytes[]"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"}],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"}],"name":"pubkey","outputs":[{"internalType":"bytes32","name":"x","type":"bytes32"},{"internalType":"bytes32","name":"y","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"uint256","name":"contentType","type":"uint256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"setABI","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"uint256","name":"coinType","type":"uint256"},{"internalType":"bytes","name":"a","type":"bytes"}],"name":"setAddr","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"address","name":"a","type":"address"}],"name":"setAddr","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"address","name":"target","type":"address"},{"internalType":"bool","name":"isAuthorised","type":"bool"}],"name":"setAuthorisation","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"bytes","name":"hash","type":"bytes"}],"name":"setContenthash","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"setDNSRecords","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"bytes4","name":"interfaceID","type":"bytes4"},{"internalType":"address","name":"implementer","type":"address"}],"name":"setInterface","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"string","name":"name","type":"string"}],"name":"setName","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"bytes32","name":"x","type":"bytes32"},{"internalType":"bytes32","name":"y","type":"bytes32"}],"name":"setPubkey","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"string","name":"key","type":"string"},{"internalType":"string","name":"value","type":"string"}],"name":"setText","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes4","name":"interfaceID","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"pure","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"node","type":"bytes32"},{"internalType":"string","name":"key","type":"string"}],"name":"text","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"}]')
contract_addr_ens = "0x42D63ae25990889E35F215bC95884039Ba354115"
contract_ens = web3.eth.contract(address=contract_addr_ens, abi=abi_ens)

abi_mpc = json.loads('[{"inputs":[{"internalType":"address payable","name":"_recipient","type":"address"},{"internalType":"uint256","name":"duration","type":"uint256"}],"payable":true,"stateMutability":"payable","type":"constructor"},{"constant":false,"inputs":[],"name":"claimTimeout","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bytes","name":"signature","type":"bytes"}],"name":"close","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"expiration","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"newExpiration","type":"uint256"}],"name":"extend","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bytes","name":"signature","type":"bytes"}],"name":"isValidSignature","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"recipient","outputs":[{"internalType":"address payable","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"sender","outputs":[{"internalType":"address payable","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"}]')
runtimeBytecode_mpc = '0x608060405234801561001057600080fd5b506004361061007d5760003560e01c806366d003ac1161005b57806366d003ac1461016f57806367e404ce146101b95780639714378c14610203578063b2af9362146102315761007d565b80630e1da6c314610082578063415ffba71461008c5780634665096d14610151575b600080fd5b61008a61030e565b005b61014f600480360360408110156100a257600080fd5b8101908080359060200190929190803590602001906401000000008111156100c957600080fd5b8201836020820111156100db57600080fd5b803590602001918460018302840111640100000000831117156100fd57600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f820116905080830192505050505050509192919290505050610357565b005b610159610467565b6040518082815260200191505060405180910390f35b61017761046d565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b6101c1610493565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b61022f6004803603602081101561021957600080fd5b81019080803590602001909291905050506104b8565b005b6102f46004803603604081101561024757600080fd5b81019080803590602001909291908035906020019064010000000081111561026e57600080fd5b82018360208201111561028057600080fd5b803590602001918460018302840111640100000000831117156102a257600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f820116905080830192505050505050509192919290505050610529565b604051808215151515815260200191505060405180910390f35b60025442101561031d57600080fd5b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16ff5b600160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff16146103b157600080fd5b6103bb8282610529565b6103c457600080fd5b600160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff166108fc839081150290604051600060405180830381858888f1935050505015801561042c573d6000803e3d6000fd5b506000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16ff5b60025481565b600160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff161461051157600080fd5b600254811161051f57600080fd5b8060028190555050565b6000806105923085604051602001808373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1660601b815260140182815260200192505050604051602081830303815290604052805190602001206105f6565b90506000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff166105d6828561064e565b73ffffffffffffffffffffffffffffffffffffffff161491505092915050565b60008160405160200180807f19457468657265756d205369676e6564204d6573736167653a0a333200000000815250601c01828152602001915050604051602081830303815290604052805190602001209050919050565b60008060008061065d856106d5565b92509250925060018684848460405160008152602001604052604051808581526020018460ff1660ff1681526020018381526020018281526020019450505050506020604051602081039080840390855afa1580156106c0573d6000803e3d6000fd5b50505060206040510351935050505092915050565b600080600060418451146106e857600080fd5b6020840151915060408401519050606084015160001a9250828282925092509250919390925056fea265627a7a72315820b76f0f1cee859ce5547cf4dc1552adf93171ccfe07e152a85efabc97ed5c0f6064736f6c63430005110032'

local_addr = "0.0.0.0"
local_port = 1700

WATCHER_URL = 'https://watcher.rinkeby.v1.omg.network'
WATCHER_INFO_URL = 'https://watcher-info.rinkeby.v1.omg.network'

# remote_host = "163.172.130.246"
# remote_port = 9999

# remote_host = "router.eu.thethings.network"
# remote_port = 1700

counter = 0
message = b'error, no server response'
messageQueue = queue.Queue()
packet_forwarder_response_add = 0
# message = b'\xd2\x84C\xa1\x01&\xa0X`\xd0\x83XA\xa3\x01\x01\x05X\x1a000102030405060708090a0b0c\x00x\x1e["1000", 1, "163.172.130.246"]\xa0X\x18q\xe5\'C\x15\xecp=\xce\xe9\x03\xb9\r\xccz(v\x9f\xfe\x9c\x0c\xb8f\xaeX@\x1e/ql\xc4T\xde\x80\x83\x1c-\xc4\x83\xefy\x17/\xad\xfd\xeb\x10\xf6\xf9\xec\xda\x8dL?\x00h\xa4H\xb9\xbb!\x9c\xe4\xcc\xa1\xebg\x05?r\xc6\x8b?B,\x95J\xf8\xdb\xbcxHP\xcb=F\x8f\x9d\xbb\xa3'

# x_pub = "643866c0256518170f24e8fb01b2333fd7ef142eaae09aa8c122b41b90663d0c"
# y_pub = "d4dd6437103adbce83c75788f376e67bb8ab7fcc75aee9332bd209207723b26f"

message_price = 100
# balance_threshold is indicated in percent --> if > balance_threshold, close the contract
balance_threshold = 0.8
# time_threshold is indicated in seconds --> if < time_threshold remaining, close the contract
time_threshold = 2 * 24 * 60 * 60


async def save_msg(msg, pType, counter, deviceAdd, host, port) :
    id = str(time.time())
    date = str(datetime.datetime.now().strftime('%d-%m-%Y_%H:%M:%S'))

    x = {"_id" : id, "date" : date, "host" : host, "port" : port, "payed" : False, "pType" : pType, "counter" : counter, "deviceAdd" : deviceAdd, "msg" : msg}
    result = await collection_MSG.insert_one(x)


async def get_and_pay(host, deviceAdd, counter_header) :
    x = {"host" : host, "counter" : counter_header, "deviceAdd" : deviceAdd, "payed" : False}
    document = await collection_MSG.find_one(x, sort=[('_id', -1)])
    if document != None:
        payed = {"payed" : True}
        await collection_MSG.update_one(x, {'$set': payed})
    return document

# async def get_and_pay(host, deviceAdd, counter_start, counter_end) :
#     store = []
#     for i in range(counter_start, counter_end) :
#         x = {"host" : host, "header" : {"counter" : i, "deviceAdd" : deviceAdd}}
#         document = await collection_MSG.find_one(x)
#         # mark message as payed
#         store.append(document['msg'])

#     return store

async def get_mpc_document(contract_add) :
    x = {"_id" : contract_add}
    document = await collection_MPC.find_one(x)
    return document


async def delete_mpc_document(contract_add) :
    x = {"_id" : contract_add}
    await collection_MPC.delete_many(x)


async def store_mpc(contract_add, signature, new_amount, expiration, remote_host) :
    x = {"_id" : contract_add}
    document = await collection_MPC.find_one(x)
    if document == None :
        # create new document
        data = {"_id" : contract_add, "signature": signature, "amount": new_amount, "expiration": expiration, "host": remote_host}
        result = await collection_MPC.insert_one(data)
    
    else :
        # update document
        data = {"signature": signature, "amount": new_amount, "expiration": expiration}
        await collection_MPC.update_one(x, {'$set': data})


async def url_process(url) :
    # ip4 = "https://111.111.111.111:65535"
    # ip4 = "111.111.111.111:65535"
    # print(len(ip4))

    # ip6 = "https://[0:0:0:0:0:0:0:1]:123"
    # ip6 = "[0:0:0:0:0:0:0:1]:123"
    # print(len(ip6))

    add = url.split(":")
    # print(add)
    # print(len(add))

    # if IPv4
    if len(add) < 4 :
        # print("ipv4")
        # port + http
        if len(add) > 2 and "http" in add[0] :
            # contain "http://" or "https://"
            add.pop(0)
            add[0] = add[0].replace("/", "")
        # only address --> no port
        elif len(add) == 1 :
            address = add[0]
            address = address.replace("/", "")
            address = address.replace(" ", "")
            port = 0
            return address, port
        # address + http
        elif len(add) == 2 and "http" in add[0] :
            address = add[len(add)-1]
            address = address.replace("/", "")
            address = address.replace(" ", "")
            port = 0
            return address, port

        address = add[0]
        address = address.replace("/", "")
        address = address.replace(" ", "")
        port = add[len(add)-1]
        port = int(port)
        # print(address)
        # print(port)
        return address, port

    # if IPv6
    else :
        # print("ipv6")
        # port + http
        if len(add) > 9 and "http" in add[0] :
            # contain "http://" or "https://"
            add.pop(0)
            add[0] = add[0].replace("/", "")
            add[0] = add[0].replace("[", "")
            add[len(add)-2] = add[len(add)-2].replace("]", "")
        # only address
        elif len(add) == 8 :
            address = ':'.join(add)
            address = address.replace("/", "")
            address = address.replace(" ", "")
            port = 0
            return address, port
        # address + http
        elif len(add) == 9 and "http" in add[0] :
            address = ':'.join(add[1:])
            address = address.replace("/", "")
            address = address.replace(" ", "")
            port = 0
            return address, port
        # address + port
        elif len(add) == 9 and "http" not in add[0] :
            add[0] = add[0].replace("[", "")
            add[len(add)-2] = add[len(add)-2].replace("]", "")

        # print(add)
        address = ':'.join(add[:-1])
        address = address.replace("/", "")
        address = address.replace(" ", "")
        port = add[len(add)-1]
        port = int(port)
        # print(address)
        # print(port)
        return address, port


async def process(data) :
    size = len(data)
    #print(f'data : {data} {type(data)} {size}')

    if size < 12 :
        #print(" (too short for GW <-> MAC protocol)\n")
        return b'error'
    else :
        #print("Process the data 1")
        if data[0] != 2 :
            #print("invalid version\n")
            return b'error'
        else :
            #print("Process the data 2")
            if data[3] != 0 :
                return b'error'
            else :
                #print("Not the right gateway command")
                #print("Process the data 3")
                string = data[12:].decode("utf-8")
                #print(f'{string} {type(string)}')
                if "data" not in string or "867.500000" not in string or "4/7" not in string :
                    #print("No data field and not the right freq")
                    return b'error'
                else :
                    #print("Process the data 4")
                    #print(f'data : {data} {type(data)} {size}')
                    json_obj = json.loads(string)
                    final = json_obj['rxpk'][0]['data']
                    processed = b64decode(final)
                    print("final :", final)
                    print("processed :", processed)

                    return processed



async def generate_response(data):
    # data = "ahahhahahahhahahhahahahhahahhahahhahahhahahahahahahahahahahhahah"
    # data = urlsafe_b64encode(data.encode("utf-8"))
    # data = data.decode("utf-8")
    # size_calc = await size_calculation(data)
    # print("size_calc :", size_calc)

    # data = b'ahahhahahahhahahhahahahhahahahahahahahahahahhahahahahahhahahahahahahahahhahahahahahahahahhahahahahahahahahahahahahahahahahahahahahahahahahahhahahahahahahahahahahahahahahahahahahahahahahahahahhahhahahahahahahahahahahahahahahhahahahhahahahahahahahhahahahahahhahahahahahahahahahahahahahahahahahahhahahahahahahahahahahahahahahahahahahahahahahahahahahahahahahahahahahahahahahahahahahahaha'
    #data = b'\xd2\x84C\xa1\x01&\xa0X`\xd0\x83XA\xa3\x01\x01\x05X\x1a000102030405060708090a0b0c\x00x\x1e["1000", 1, "163.172.130.246"]\xa0X\x18q\xe5\'C\x15\xecp=\xce\xe9\x03\xb9\r\xccz(v\x9f\xfe\x9c\x0c\xb8f\xaeX@\x1e/ql\xc4T\xde\x80\x83\x1c-\xc4\x83\xefy\x17/\xad\xfd\xeb\x10\xf6\xf9\xec\xda\x8dL?\x00h\xa4H\xb9\xbb!\x9c\xe4\xcc\xa1\xebg\x05?r\xc6\x8b?B,\x95J\xf8\xdb\xbcxHP\xcb=F\x8f\x9d\xbb\xa3'
    data = b64encode(data)
    data = data.decode("utf-8")
    size_calc = await size_calculation(data)
    # print("size_calc :", size_calc)
    # WARNING: [down] mismatch between .size and .data size once converter to binary

    json_obj = {"txpk":{
        "imme":True,
        "rfch":0,
        "freq":867.5,
        "powe":14,
        "modu":"LORA",
        "datr":"SF12BW125",
        "codr":"4/7",
        "prea":8,
        "ipol":False,
        "size":size_calc,
        "ncrc":True,
        "data":data
    }}

    string = json.dumps(json_obj)
    response = b'\x02' + b'\x00' + b'\x00' + b'\x03' + string.encode("utf-8")

    return response


async def size_calculation(data):
    size = len(data)

    if size%4 == 0 and size >= 4 :  # potentially padded Base64
        if data[size-2] == "=" :    # 2 padding char to ignore
            return await size_calculation_nopad(size-2)
        elif data[size-1] == "=" :  # 1 padding char to ignore
            return await size_calculation_nopad(size-1)
        else :  # no padding to ignore
            return await size_calculation_nopad(size)

    else :  # treat as unpadded Base64
        return await size_calculation_nopad(size)


async def size_calculation_nopad(size):
    full_blocks = int(size / 4)
    last_chars = size % 4
    last_bytes = 0

    if last_chars == 0 :
        last_bytes = 0
    if last_chars == 2 :
        last_bytes = 1
    if last_chars == 3 :
        last_bytes = 2

    result_len = (3*full_blocks) + last_bytes

    return result_len


class ProxyDatagramProtocol():

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        #print(data)
        loop = asyncio.get_event_loop()
        loop.create_task(self.datagram_received_async(data, addr))

    async def datagram_received_async(self, data, addr):
        global counter
        global message
        global messageQueue
        # print(f"Received : {data} from : {addr}")
        if data[0:2] == b'0x' :
            print("hash received")
            sender, currency, amount, receiver, metadata = await verifyHash(hashed)
            if receiver == ether_add and amount > 0 and currency == "0x0" :
                # get value from metadata
                    # split ,
                meta_list = metadata.split(",")
                deviceAdd = meta_list[0]
                start = meta_list[1]
                end = meta_list[2]

                # verifies that the amount of messages match the amount payed
                if (end - start + 1) * 100 == amount :

                    # get messages
                    messages = await get_and_pay(addr[0], deviceAdd, start, end)

                    # send messages




        else :
            if data[3] == 0:
                processed = await process(data)
                if processed != b'error':
                    counter = 1

                    # send an ack to the packet forwarder
                    ack = data[:4]
                    a = bytearray(ack)
                    a[3] = 1
                    ack = bytes(a)
                    self.transport.sendto(ack, addr)

                    # get source of message
                    try :
                        header = await get_header(processed)
                        pType = header[0]
                        counter_header = header[1]
                        deviceAdd = header[2]
                        print("header :", header)
                        print("deviceAdd :", deviceAdd)

                        # get address from blockchain + pub key
                        # convert deviceAdd to decimal
                        device = await contract_lora.functions.devices(int(deviceAdd, 0)).call()
                        print(device)
                        ipv4Addr = device[0]
                        ipv6Addr = device[1]
                        domain = device[2]
                        ipv4Port = device[3]
                        ipv6Port = device[4]
                        domainPort = device[5]
                        x_pub = int(device[7])
                        y_pub = int(device[8])

                        x_pub = format(x_pub, '064x')
                        y_pub = format(y_pub, '064x')


                        # verify signature 
                        valid = await verify_countersign(processed, x_pub, y_pub)
                        if valid != False :
                            # get the hash and the signature to send
                            to_be_signed = valid._sig_structure
                            hash_structure = hashlib.sha256(to_be_signed).digest()
                            signature = valid.signature

                            # domain = "ip6.loramac.eth"
                            # domainPort = 30

                            # analyze address
                            if domain != "":
                                print("domain")
                                # if .eth and no port in address
                                if domain[-4:] == ".eth":
                                    print("eth add")
                                    # get ip
                                    name_hash = namehash(domain)
                                    url = await contract_ens.functions.text(name_hash, "url").call()
                                    print(url)
                                    remote_host, remote_port = await url_process(url)
                                    if remote_port == 0 :
                                        remote_port = domainPort
                                else :
                                    add = domain.split(":")
                                    # if .eth with port --> use port in ens or domainPort and not the one with the url
                                    if add[0][-4:] == ".eth":
                                        print("eth add")
                                        remote_port = add[len(add)-1]
                                        remote_port = int(remote_port)
                                        # print(remote_port)
                                        # get ip
                                        name_hash = namehash(add[0])
                                        url = await contract_ens.functions.text(name_hash, "url").call()
                                        print(url)
                                        remote_host, remote_port = await url_process(url)
                                        if remote_port == 0 :
                                            remote_port = domainPort

                                    # if not .eth
                                    else :
                                        remote_host = add[0]
                                        # if port
                                        if len(add) > 1:
                                            remote_port = add[len(add)-1]
                                            remote_port = int(port)
                                        else :
                                            remote_port = domainPort
                                        # print(remote_host)
                                        # print(remote_port)
                                        print("not eth add")
                                        # resolve DNS to get ip
                                        remote_host = socket.gethostbyname(remote_host)
                                        # print(remote_host)

                            elif ipv4Addr != 0 :
                                remote_host = str(ipaddress.IPv4Address(ipv4Addr))
                                remote_port = ipv4Port

                            elif ipv6Addr != 0 :
                                remote_host = str(ipaddress.IPv6Address(ipv6Addr))
                                remote_port = ipv6Port

                            print(remote_host)
                            print(remote_port)

                            await save_msg(processed, pType, counter_header, deviceAdd, remote_host, remote_port)

                            encoding = "utf-8"      # cp437 or windows-1252    utf-8
                            # processed2 = processed.decode(encoding)     # bytes to string
                            # print("processed2 :", processed2)
                            # processed3 = processed2.encode(encoding)    # string to bytes
                            # print("same :", processed == processed3)

                            # processed = processed + str.encode(ether_add)
                            # send hash + signature to the
                            # --> divise message entre contenu et signature
                            # print("hash_structure :", hash_structure)
                            # print("hash_structure :", hash_structure.decode(encoding))
                            # print("signature :", signature)
                            # print("signature :", signature.decode(encoding))
                            
                            # packet = deviceAdd + "," + counter_header + "," + ether_add
                            # print("packet :", packet)

                            # loop = asyncio.get_event_loop()
                            # coro = loop.create_datagram_endpoint(
                            #     lambda: RemoteDatagramProtocol(self, addr, processed),
                            #     remote_addr=(remote_host, remote_port))
                            # asyncio.ensure_future(coro)

                            loop = asyncio.get_event_loop()
                            loop.create_task(ws_send(f"ws://{remote_host}:{8765}", hash_structure, signature, deviceAdd, counter_header, remote_host))

                    except ValueError :
                        print("ValueError")
                        message = b'error, corrupted data'
                        messageQueue.put(message)
                    except TypeError :
                        print("TypeError")
                        message = b'error, corrupted data'
                        messageQueue.put(message)
                    except AttributeError : 
                        print("AttributeError")
                        message = b'error, corrupted data'
                        messageQueue.put(message)
                    except SystemError :
                        print("SystemError")
                        message = b'error, corrupted data'
                        messageQueue.put(message)



            if data[3] == 2 :
                # if counter == 1 :
                #     c = 0
                #     while message == b'error, no server response' and c < 10 :
                #         await asyncio.sleep(1)
                #         c = c + 1

                #     counter = 0

                #     ack = data[:4]
                #     a = bytearray(ack)
                #     a[3] = 4
                #     ack = bytes(a)
                #     self.transport.sendto(ack, addr)

                #     response = await generate_response(message)
                #     print("response :", response)
                #     self.transport.sendto(response, addr)
                #     message = b'error, no server response'

                if messageQueue.empty() == False :

                    ack = data[:4]
                    a = bytearray(ack)
                    a[3] = 4
                    ack = bytes(a)
                    self.transport.sendto(ack, addr)

                    message = messageQueue.get()
                    response = await generate_response(message)
                    print("response :", response)
                    self.transport.sendto(response, addr)



async def ws_send(uri, hash_structure, signature, deviceAdd, counter_header, remote_host) :
    global messageQueue
    try :
        async with websockets.connect(uri) as websocket:
            try :

                packet = deviceAdd + "," + counter_header + "," + ether_add
                print("packet :", packet)

                await websocket.send(hash_structure)
                await websocket.send(signature)
                await websocket.send(packet)

                payment_receipt = await websocket.recv()
                if "error" not in payment_receipt:
                    down_message = await websocket.recv()
                    print("payment_receipt :", payment_receipt)
                    print("down_message :", down_message)

                    payment_list = payment_receipt.split(',')
                    if payment_list[0] == 'OMG' :
                        price = message_price
                        # send down_message directly if any
                        if down_message != b"down_message":
                            # verify down
                            verified = await verify_down(down_message)
                            if verified :
                                price = message_price * 2
                                messageQueue.put(down_message)

                        payment_hash = payment_list[1]
                        # sleep 2 minutes
                        print("sleep for 2 minutes")
                        await asyncio.sleep(120)
                        metadata = await verify_omg_payment(payment_hash, remote_host, price)
                        # get value from metadata
                            # split ,
                        meta_list = metadata.split(",")
                        counter_header = meta_list[1]
                        deviceAdd = meta_list[2]

                        # get and pay message
                        message = await get_and_pay(remote_host, deviceAdd, counter_header)
                        print("message :", message)

                        # if message != b"" and message != None :
                        #     await websocket.send(message['msg'])
                    

                    if payment_list[0] == 'MPC' :
                        signature = payment_list[1]
                        contract_add = payment_list[2]
                        payed_amount = int(payment_list[3])

                        verified = await verify_mpc_payment(signature, contract_add, payed_amount, remote_host)
                        if verified == True :
                            # send down_message if any
                            if down_message != b"down_message" and payed_amount == 2*message_price:
                                verified2 = await verify_down(down_message)
                                if verified2 :
                                    messageQueue.put(down_message)

                            # send message
                            message = await get_and_pay(remote_host, deviceAdd, counter_header)
                            print("message :", message)
                            # if message != None :
                            #     await websocket.send(message['msg'])
                        elif verified ==  "error : smart contract closed":
                            message = verified
                            # send down_message if any
                            if down_message != b"down_message" and payed_amount == 2*message_price:
                                verified = await verify_down(down_message)
                                if verified :
                                    messageQueue.put(down_message)

                            # send message
                            message2 = await get_and_pay(remote_host, deviceAdd, counter_header)
                            print("message2 :", message2)

                        else :
                            message = None

                    if message != b"" and message != None :
                        if message == "error : smart contract closed":
                            await websocket.send(message)
                            await websocket.send(message2['msg'])
                        
                        else :
                            await websocket.send(message['msg'])
                        
                        print("message sent to server")

                        if down_message == b"down_message" and payment_list[0] != 'OMG':

                            payment_receipt = await websocket.recv()
                            response = await websocket.recv()
                            print("payment_receipt :", payment_receipt)
                            print("received response :", response)

                            if payment_receipt != "nothing":
                                payment_list = payment_receipt.split(',')
                                if payment_list[0] == 'MPC' :
                                    signature = payment_list[1]
                                    contract_add = payment_list[2]
                                    payed_amount = int(payment_list[3])

                                    verified = await verify_mpc_payment(signature, contract_add, payed_amount, remote_host)
                                    if verified != False and response != "nothing":
                                        verified2 = await verify_down(response)
                                        if verified2 :
                                            messageQueue.put(response)
                                            if verified == "error : smart contract closed":
                                                await websocket.send("error : smart contract closed")
                                            else :
                                                await websocket.send("success")



                    else :
                        await websocket.send("invalid payment")

                else :
                    print(payment_receipt)


                    
        

                # global messageQueue
                # messageQueue.put(response)
                # print(f"< {response}")

            except RuntimeError :
                print("Closing the websocket")
                await websocket.close()

    except ConnectionRefusedError :
        response = b"error : no server connection"
        print(response)
        messageQueue.put(response)
    except RuntimeError :
        print("Closing the connection")


async def verify_down(message):
    header = await get_header(message)
    pType = header[0]
    counter_header = header[1]
    hostAdd = header[2]
    # print("header :", header)
    # print("hostAdd :", hostAdd)

    if hostAdd.count(":") > 1:
        # print("IPv6")
        addr = int(ipaddress.IPv6Address(hostAdd))
        server = await contract_lora.functions.ipv6Servers(addr).call()
    elif hostAdd[0].isdigit() and hostAdd[len(hostAdd)-1].isdigit() :
        # print("IPv4")
        addr = int(ipaddress.IPv4Address(hostAdd))
        server = await contract_lora.functions.ipv4Servers(addr).call()
    else :
        # print("domain")
        server = await contract_lora.functions.domainServers(hostAdd).call()

    if int(server[0]) != 0 and int(server[1]) != 0 :
        x_pub = int(server[0])
        y_pub = int(server[1])

        x_pub = format(x_pub, '064x')
        y_pub = format(y_pub, '064x')

        # verify signature 
        valid = await verify_countersign(message, x_pub, y_pub)

        return valid

    else :
        return False

    
async def verify_mpc_payment(signature, contract_add, payed_amount, remote_host):
    contract_mpc = web3.eth.contract(contract_add, abi=abi_mpc)

    # verify valid bytecode 
    bytecode = await web3.eth.getCode(contract_add)
    bytecode = bytecode.hex()
    if bytecode == runtimeBytecode_mpc :

        # verify if MPC document present
        # get amount and calculate new one
        mpc_document = await get_mpc_document(contract_add)
        print("mpc_document :", mpc_document)
        if mpc_document == None :
            amount = 0
        else :
            amount = mpc_document['amount']

        expiration = await contract_mpc.functions.expiration().call()
        print("expiration :", expiration)
        # verify that the smart contract has not expired
        epoch_time = int(time.time())
        if expiration > epoch_time :

            new_amount = amount + payed_amount

            # verify enough ether stored in contract
            balance = await web3.eth.getBalance(contract_add)
            print("balance :", balance)
            if balance > new_amount :
                
                # verify signature
                valid_sig = await contract_mpc.functions.isValidSignature(new_amount, signature).call()
                print("valid_sig :", valid_sig)

                if valid_sig :

                    # if a threshold of balance and time is passed, close the contract

                    balance_limit = balance_threshold * balance
                    time_limit = expiration - time_threshold
                    if new_amount < balance_limit and epoch_time < time_limit :
                        print("threshold not exceeded")

                        # store in MPC DB
                        await store_mpc(contract_add, signature, new_amount, expiration, remote_host)

                        # send message
                        # message = await get_and_pay(remote_host, deviceAdd, counter_header)
                        # print("message :", message)
                        # if message != None :
                        #     await websocket.send(message['msg'])
                        return True

                    else :
                        print("threshold exceeded")
                        # close the contract
                        nonce = await web3.eth.getTransactionCount(ether_add)  
                        chainId = await web3.eth.chainId
                        
                        transaction = contract_mpc.functions.close(new_amount, signature).buildTransaction({
                            'chainId': chainId,
                            'gas': 70000,
                            'gasPrice': web3.toWei('1', 'gwei'),
                            'nonce': nonce,
                        })
                        signed_txn = web3.eth.account.signTransaction(transaction, private_key=private_key)
                        close = await web3.eth.sendRawTransaction(signed_txn.rawTransaction)

                        print("close :", close)

                        # delete the MPC document
                        await delete_mpc_document(contract_add)
                        return "error : smart contract closed"

                else :
                    print("signature is not valid")
                    return False

            else :
                print("not enough balance in the smart contract")
                return False

        else :
            print("the smart contract has expired")
            return False
    
    else :
        print("runtimeBytecode does not match")
        return False



# async def verify_omg_payment(payment_hash, remote_host, price):
#     sender, currency, amount, receiver, metadata = await verifyHash(payment_hash)
#     if receiver.lower() == ether_add.lower() and amount == price and currency == "0x0000000000000000000000000000000000000000" :
#         # get value from metadata
#             # split ,
#         meta_list = metadata.split(",")
#         counter_header = meta_list[1]
#         deviceAdd = meta_list[2]

#         # get message
#         message = await get_and_pay(remote_host, deviceAdd, counter_header)
#         print("message :", message)

#         # send message
#         return message
#     else :
#         print("There is an error in the payment")
#         return b""


async def verify_omg_payment(payment_hash, remote_host, price):
    sender, currency, amount, receiver, metadata = await verifyHash(payment_hash)
    if receiver.lower() == ether_add.lower() and amount == price and currency == "0x0000000000000000000000000000000000000000" :

        return metadata
    else :
        print("There is an error in the payment")
        return None


async def verifyHash(hashed):
    body = {'id': hashed, 'jsonrpc': '2.0'}
    body = json.dumps(body)
    # print(body)
    response = await requests.post(f'{WATCHER_INFO_URL}/transaction.get', data=body, headers= { 'Content-Type': 'application/json'})
    json_resp = response.json()
    # print(json_resp)
    sender = ""
    currency = ""
    amount = -1
    receiver = ""
    metadata = ""
    try :
        sender = json_resp['data']['inputs'][0]['owner']
        currency = json_resp['data']['inputs'][0]['currency']
        amount = json_resp['data']['outputs'][0]['amount']
        receiver = json_resp['data']['outputs'][0]['owner']
        metadata = json_resp['data']['metadata']
        print("sender :", sender)
        print("currency :", currency)
        print("amount :", amount)
        print("receiver :", receiver)
        print("metadata :", metadata)
        # decrypt metadata
        metadata = bytearray.fromhex(metadata[2:]).decode()
        print("metadata :", metadata)
        # print(receiver.lower() == ether_add.lower())
        # print(amount == 100)
        # print(currency == "0x0000000000000000000000000000000000000000")
    except KeyError :
        print("Transaction does not exist")

    return sender, currency, amount, receiver, metadata



class RemoteDatagramProtocol():

    def __init__(self, proxy, addr, data):
        self.proxy = proxy
        self.addr = addr
        self.data = data
        super().__init__()

# class RemoteDatagramProtocol:
#     def __init__(self, message, loop):
#         self.message = message
#         self.loop = loop
#         self.transport = None

    def connection_made(self, transport):
        loop = asyncio.get_event_loop()
        loop.create_task(self.connection_made_async(transport))

    async def connection_made_async(self, transport):
        self.transport = transport
        # print("Received from device :", self.data)
        # send to server
        self.transport.sendto(self.data)

    def datagram_received(self, data, _):
        loop = asyncio.get_event_loop()
        loop.create_task(self.datagram_received_async(data, _))

    async def datagram_received_async(self, data, _):
        print("Received from server :", data)
        # send back to device
        # self.proxy.transport.sendto(data, self.addr)
        global message
        message = data

        global messageQueue
        messageQueue.put(data)


    def error_received(self, exc):
        print('Error received:', exc)
        global messageQueue
        messageQueue.put(b'error, no server response')

    def connection_lost(self, exc):
        print('Connection lost')
        #self.proxy.remotes.pop(self.attr)
        self.proxy.remotes.pop(self.addr)



async def start_datagram_proxy(bind, port):
    # hashed = '0x851237ba43c9586b47e3bc2c41f7f92b31d4275f117f0f0cd16162590a4eb79c'
    # hashed = '0xf4a33b43f41313faf9124d897b851d49c76d772bfa48870622977643af21c6f9'
    # hashed = '0xdb63db23ed5c51219a3c1b87427d5dbce99381e7c1742b5ea229fd38bf0cb6cb'
    # sender, currency, amount, receiver, metadata = await verifyHash(hashed)
    # message = await get_and_pay("163.172.130.246", "0x1145f03880d8a975", "0")
    # print("message :", message)

    # bytecode = await web3.eth.getCode('0x2c25489C46f6E463dBc4513D1c67838adD53737f')
    # bytecode = bytecode.hex()
    # print("bytecode :", bytecode)
    # print(bytecode == runtimeBytecode_mpc)

    # balance = await web3.eth.getBalance('0xFFC869826E724845a65F710D3Ffa8691f274b3Ba')
    # print("balance :", balance)
    # b = b"error1"
    # if b"error" in b :
    #     print("true")





    # private_key = "3c1a2e912be2ccfd0a9802a73002fdaddff5d6e7c4d6aac66a8d5612277c7b9e"

    # nonce = await web3.eth.getTransactionCount(ether_add)  
    # print("nonce :", nonce)

    # chainId = await web3.eth.chainId
    # print("chainId :", chainId)
    
    # contract_add = '0xBf2625b1bFaA60d46eeB74F00A9E62213aEB4e88'
    # contract_mpc = web3.eth.contract(contract_add, abi=abi_mpc)
    # amount = 5200
    # signature = '0xeeb14e223ee20986f6f71818b98cb79c855d304e57bb321d26bac3254f994d2e4aa5ceeabcbf5fe802eacbb5174d31e11c3042bd08620e52318e6e695fea965b1c'
    # transaction = contract_mpc.functions.close(amount, signature).buildTransaction({
    #     'chainId': chainId,
    #     'gas': 70000,
    #     'gasPrice': web3.toWei('1', 'gwei'),
    #     'nonce': nonce,
    # })
    # signed_txn = web3.eth.account.signTransaction(transaction, private_key=private_key)
    # close = await web3.eth.sendRawTransaction(signed_txn.rawTransaction)

    # print("close :", close)





    loop = asyncio.get_event_loop()
    return await loop.create_datagram_endpoint(
        lambda: ProxyDatagramProtocol(),
        local_addr=(bind, port))


def main(bind=local_addr, port=local_port):
    loop = asyncio.get_event_loop()
    print("Starting UDP proxy server...")
    coro = start_datagram_proxy(bind, port)
    transport, _ = loop.run_until_complete(coro)
    print("UDP proxy server is running...")

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    print("Closing transport...")
    transport.close()
    loop.close()


if __name__ == '__main__':
    main()
