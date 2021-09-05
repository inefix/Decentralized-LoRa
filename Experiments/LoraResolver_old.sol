// SPDX-License-Identifier: GPL-3.0
// this version contains only the mapping for the devices

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
    }   
    
    mapping(uint64 => Device) public devices;
    
    function registerIpv4(uint64 loraAddr, uint32 server, uint16 port) public {
        require(devices[loraAddr].owner == address(0) || devices[loraAddr].owner == msg.sender, "Device already owned");
        require(devices[loraAddr].ipv4Addr == 0, "Device already registered with ipv4, use updateIpv4");
        require(server != 0, "Server address cannot be 0");
        require(port != 0, "Server port cannot be 0");
        devices[loraAddr].ipv4Addr = server;
        devices[loraAddr].ipv4Port = port;
        devices[loraAddr].owner = msg.sender;
    }
    
    function registerIpv6(uint64 loraAddr, uint128 server, uint16 port) public {
        require(devices[loraAddr].owner == address(0) || devices[loraAddr].owner == msg.sender, "Device already owned");
        require(devices[loraAddr].ipv6Addr == 0, "Device already registered with ipv6, use updateIpv6");
        require(server != 0, "Server address cannot be 0");
        require(port != 0, "Server port cannot be 0");
        devices[loraAddr].ipv6Addr = server;
        devices[loraAddr].ipv6Port = port;
        devices[loraAddr].owner = msg.sender;
    }
    
    function registerDomain(uint64 loraAddr, string memory domain, uint16 port) public {
        require(devices[loraAddr].owner == address(0) || devices[loraAddr].owner == msg.sender, "Device already owned");
        require(keccak256(bytes(devices[loraAddr].domain)) == keccak256(bytes("")), "Device already registered with domain, use updateDomain");
        require(keccak256(bytes(domain)) != keccak256(bytes("")), "Server domain cannot be empty");
        devices[loraAddr].domain = domain;
        devices[loraAddr].domainPort = port;
        devices[loraAddr].owner = msg.sender;
    }
    
    function updateIpv4(uint64 loraAddr, uint32 server, uint16 port) public {
        require(devices[loraAddr].owner == msg.sender, "Device not owned by you");
        require(devices[loraAddr].ipv4Addr != 0 || devices[loraAddr].ipv4Port != 0, "Device not yet registered with ipv4");
        require(server != 0, "Server address cannot be 0");
        require(port != 0, "Server port cannot be 0");
        devices[loraAddr].ipv4Addr = server;
        devices[loraAddr].ipv4Port = port;
    }
    
    function updateIpv6(uint64 loraAddr, uint128 server, uint16 port) public {
        require(devices[loraAddr].owner == msg.sender, "Device not owned by you");
        require(devices[loraAddr].ipv6Addr != 0 || devices[loraAddr].ipv6Port != 0, "Device not yet registered with ipv6");
        require(server != 0, "Server address cannot be 0");
        require(port != 0, "Server port cannot be 0");
        devices[loraAddr].ipv6Addr = server;
        devices[loraAddr].ipv6Port = port;
    }
    
    function updateDomain(uint64 loraAddr, string memory domain, uint16 port) public {
        require(devices[loraAddr].owner == msg.sender, "Device not owned by you");
        require(keccak256(bytes(devices[loraAddr].domain)) != keccak256(bytes("")), "Device not yet registered with domain");
        require(keccak256(bytes(domain)) != keccak256(bytes("")), "Server domain cannot be empty");
        devices[loraAddr].domain = domain;
        devices[loraAddr].domainPort = port;
    }
}