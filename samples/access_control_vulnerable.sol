// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract AccessControlVulnerable {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    function transferOwnership(address newOwner) external {
        owner = newOwner;
    }

    function emergencyWithdraw(address payable recipient) external {
        recipient.transfer(address(this).balance);
    }

    receive() external payable {}
}
