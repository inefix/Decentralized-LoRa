// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.4.22 <0.7.0;

contract MapAddress {
    mapping(uint64 => uint32) public map;

    function set(uint64 deviceAdd, uint32 serverAdd) public {
        require(map[deviceAdd] == 0, "Device already registered");
        map[deviceAdd] = serverAdd;
    }
    
    function update(uint64 deviceAdd, uint32 serverAdd) public {
        require(map[deviceAdd] != 0, "Device not yet registered");
        map[deviceAdd] = serverAdd;
    }
    
    function get(uint64 deviceAdd) public view returns (uint32) {
        return map[deviceAdd];
    }
}