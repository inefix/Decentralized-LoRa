export const loraResolverAbi = [
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
			},
			{
				"internalType": "uint256",
				"name": "x_pub",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "y_pub",
				"type": "uint256"
			}
		],
		"name": "registerDomainDevice",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "domain",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "x_pub",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "y_pub",
				"type": "uint256"
			}
		],
		"name": "registerDomainServer",
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
			},
			{
				"internalType": "uint256",
				"name": "x_pub",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "y_pub",
				"type": "uint256"
			}
		],
		"name": "registerIpv4Device",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint32",
				"name": "ipv4Addr",
				"type": "uint32"
			},
			{
				"internalType": "uint256",
				"name": "x_pub",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "y_pub",
				"type": "uint256"
			}
		],
		"name": "registerIpv4Server",
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
			},
			{
				"internalType": "uint256",
				"name": "x_pub",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "y_pub",
				"type": "uint256"
			}
		],
		"name": "registerIpv6Device",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint128",
				"name": "ipv6Addr",
				"type": "uint128"
			},
			{
				"internalType": "uint256",
				"name": "x_pub",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "y_pub",
				"type": "uint256"
			}
		],
		"name": "registerIpv6Server",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
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
			},
			{
				"internalType": "uint256",
				"name": "x_pub",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "y_pub",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"name": "domainServers",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "x_pub",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "y_pub",
				"type": "uint256"
			},
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint32",
				"name": "",
				"type": "uint32"
			}
		],
		"name": "ipv4Servers",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "x_pub",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "y_pub",
				"type": "uint256"
			},
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint128",
				"name": "",
				"type": "uint128"
			}
		],
		"name": "ipv6Servers",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "x_pub",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "y_pub",
				"type": "uint256"
			},
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]