// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract SafeTimeLock {
    address public beneficiary;
    uint256 public unlockTime;

    constructor(address beneficiary_, uint256 unlockTime_) payable {
        require(beneficiary_ != address(0), "zero address");
        require(unlockTime_ > block.timestamp, "unlock in future");
        beneficiary = beneficiary_;
        unlockTime = unlockTime_;
    }

    function release() external {
        require(msg.sender == beneficiary, "not beneficiary");
        require(block.timestamp >= unlockTime, "still locked");
        payable(beneficiary).transfer(address(this).balance);
    }
}
