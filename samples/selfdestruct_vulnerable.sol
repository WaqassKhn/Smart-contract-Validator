// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract SelfDestructVulnerable {
    address payable public treasury;

    constructor(address payable initialTreasury) {
        treasury = initialTreasury;
    }

    function emergencyShutdown() external {
        selfdestruct(treasury);
    }

    receive() external payable {}
}
