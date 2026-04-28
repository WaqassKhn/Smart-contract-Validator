// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract TxOriginVulnerable {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    function withdrawAll(address payable recipient) external {
        require(tx.origin == owner, "not owner");
        recipient.transfer(address(this).balance);
    }

    receive() external payable {}
}
