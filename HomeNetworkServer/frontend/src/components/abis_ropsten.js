export const simpleStorageAbi = [
  {
    "inputs": [
      {
        "internalType": "uint64",
        "name": "",
        "type": "uint64"
      }
    ],
    "name": "devices",
    "outputs": [
      {
        "internalType": "uint32",
        "name": "ipv4Addr",
        "type": "uint32"
      },
      {
        "internalType": "uint128",
        "name": "ipv6Addr",
        "type": "uint128"
      },
      {
        "internalType": "string",
        "name": "domain",
        "type": "string"
      },
      {
        "internalType": "uint16",
        "name": "ipv4Port",
        "type": "uint16"
      },
      {
        "internalType": "uint16",
        "name": "ipv6Port",
        "type": "uint16"
      },
      {
        "internalType": "uint16",
        "name": "domainPort",
        "type": "uint16"
      },
      {
        "internalType": "address",
        "name": "owner",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function",
    "constant": true
  },
  {
    "inputs": [
      {
        "internalType": "uint64",
        "name": "loraAddr",
        "type": "uint64"
      },
      {
        "internalType": "uint32",
        "name": "server",
        "type": "uint32"
      },
      {
        "internalType": "uint16",
        "name": "port",
        "type": "uint16"
      }
    ],
    "name": "registerIpv4",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint64",
        "name": "loraAddr",
        "type": "uint64"
      },
      {
        "internalType": "uint128",
        "name": "server",
        "type": "uint128"
      },
      {
        "internalType": "uint16",
        "name": "port",
        "type": "uint16"
      }
    ],
    "name": "registerIpv6",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint64",
        "name": "loraAddr",
        "type": "uint64"
      },
      {
        "internalType": "string",
        "name": "domain",
        "type": "string"
      },
      {
        "internalType": "uint16",
        "name": "port",
        "type": "uint16"
      }
    ],
    "name": "registerDomain",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint64",
        "name": "loraAddr",
        "type": "uint64"
      },
      {
        "internalType": "uint32",
        "name": "server",
        "type": "uint32"
      },
      {
        "internalType": "uint16",
        "name": "port",
        "type": "uint16"
      }
    ],
    "name": "updateIpv4",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint64",
        "name": "loraAddr",
        "type": "uint64"
      },
      {
        "internalType": "uint128",
        "name": "server",
        "type": "uint128"
      },
      {
        "internalType": "uint16",
        "name": "port",
        "type": "uint16"
      }
    ],
    "name": "updateIpv6",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint64",
        "name": "loraAddr",
        "type": "uint64"
      },
      {
        "internalType": "string",
        "name": "domain",
        "type": "string"
      },
      {
        "internalType": "uint16",
        "name": "port",
        "type": "uint16"
      }
    ],
    "name": "updateDomain",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  }
]