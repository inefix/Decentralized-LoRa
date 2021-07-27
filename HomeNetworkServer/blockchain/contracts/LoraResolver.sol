// SPDX-License-Identifier: GPL-3.0

pragma solidity >0.7.0 <0.9.0;

contract LoraResolver {
    
    struct Device {
        uint32 ipv4Addr;
        uint128 ipv6Addr;
        string domain;
        uint16 ipv4Port;
        uint16 ipv6Port;
        uint16 domainPort;
        address owner;
        uint256 x_pub;
        uint256 y_pub;
    }   
    
    struct Server {
        uint256 x_pub;
        uint256 y_pub;
        address owner;
    }
    
    mapping(uint64 => Device) public devices;
    
    mapping(uint32 => Server) public ipv4Servers;
    mapping(uint128 => Server) public ipv6Servers;
    mapping(string => Server) public domainServers;
    
    function registerIpv4Device(uint64 loraAddr, uint32 server, uint16 port, uint256 x_pub, uint256 y_pub) public {
        require(devices[loraAddr].owner == address(0) || devices[loraAddr].owner == msg.sender, "Device already owned");
        require(loraAddr != 0, "loraAddr cannot be 0");
        require(server != 0, "Server address cannot be 0");
        require(port != 0, "Server port cannot be 0");
        require(x_pub != 0, "x_pub cannot be 0");
        require(y_pub != 0, "y_pub cannot be 0");
        devices[loraAddr].ipv4Addr = server;
        devices[loraAddr].ipv4Port = port;
        devices[loraAddr].owner = msg.sender;
        devices[loraAddr].x_pub = x_pub;
        devices[loraAddr].y_pub = y_pub;
    }
    
    function registerIpv6Device(uint64 loraAddr, uint128 server, uint16 port, uint256 x_pub, uint256 y_pub) public {
        require(devices[loraAddr].owner == address(0) || devices[loraAddr].owner == msg.sender, "Device already owned");
        require(loraAddr != 0, "loraAddr cannot be 0");
        require(server != 0, "Server address cannot be 0");
        require(port != 0, "Server port cannot be 0");
        require(x_pub != 0, "x_pub cannot be 0");
        require(y_pub != 0, "y_pub cannot be 0");
        devices[loraAddr].ipv6Addr = server;
        devices[loraAddr].ipv6Port = port;
        devices[loraAddr].owner = msg.sender;
        devices[loraAddr].x_pub = x_pub;
        devices[loraAddr].y_pub = y_pub;
    }
    
    function registerDomainDevice(uint64 loraAddr, string memory domain, uint16 port, uint256 x_pub, uint256 y_pub) public {
        require(devices[loraAddr].owner == address(0) || devices[loraAddr].owner == msg.sender, "Device already owned");
        require(loraAddr != 0, "loraAddr cannot be 0");
        require(keccak256(bytes(domain)) != keccak256(bytes("")), "Server domain cannot be empty");
        require(port != 0, "Server port cannot be 0");
        require(x_pub != 0, "x_pub cannot be 0");
        require(y_pub != 0, "y_pub cannot be 0");
        devices[loraAddr].domain = domain;
        devices[loraAddr].domainPort = port;
        devices[loraAddr].owner = msg.sender;
        devices[loraAddr].x_pub = x_pub;
        devices[loraAddr].y_pub = y_pub;
    }
    
    
    function registerIpv4Server(uint32 ipv4Addr, uint256 x_pub, uint256 y_pub) public {
        require(ipv4Servers[ipv4Addr].owner == address(0) || ipv4Servers[ipv4Addr].owner == msg.sender, "Server already owned");
        require(ipv4Addr != 0, "ipv4Addr cannot be 0");
        require(x_pub != 0, "x_pub cannot be 0");
        require(y_pub != 0, "y_pub cannot be 0");
        ipv4Servers[ipv4Addr].owner = msg.sender;
        ipv4Servers[ipv4Addr].x_pub = x_pub;
        ipv4Servers[ipv4Addr].y_pub = y_pub;
    }
    
    function registerIpv6Server(uint128 ipv6Addr, uint256 x_pub, uint256 y_pub) public {
        require(ipv6Servers[ipv6Addr].owner == address(0) || ipv6Servers[ipv6Addr].owner == msg.sender, "Server already owned");
        require(ipv6Addr != 0, "ipv6Addr cannot be 0");
        require(x_pub != 0, "x_pub cannot be 0");
        require(y_pub != 0, "y_pub cannot be 0");
        ipv6Servers[ipv6Addr].owner = msg.sender;
        ipv6Servers[ipv6Addr].x_pub = x_pub;
        ipv6Servers[ipv6Addr].y_pub = y_pub;
    }
    
    function registerDomainServer(string memory domain, uint256 x_pub, uint256 y_pub) public {
        require(domainServers[domain].owner == address(0) || domainServers[domain].owner == msg.sender, "Server already owned");
        require(keccak256(bytes(domain)) != keccak256(bytes("")), "Server domain cannot be empty");
        require(x_pub != 0, "x_pub cannot be 0");
        require(y_pub != 0, "y_pub cannot be 0");
        domainServers[domain].owner = msg.sender;
        domainServers[domain].x_pub = x_pub;
        domainServers[domain].y_pub = y_pub;
    }
    
    
}