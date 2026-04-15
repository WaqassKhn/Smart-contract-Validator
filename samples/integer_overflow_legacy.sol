// SPDX-License-Identifier: MIT
pragma solidity 0.7.6;

contract IntegerOverflowLegacy {
    uint8 public counter = 255;

    function increment() external {
        counter += 1;
    }
}
