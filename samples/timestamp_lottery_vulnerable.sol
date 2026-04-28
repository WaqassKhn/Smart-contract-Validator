// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract TimestampLotteryVulnerable {
    address[] public players;

    function enter() external payable {
        require(msg.value == 1 ether, "exactly 1 ether");
        players.push(msg.sender);
    }

    function drawWinner() external {
        require(players.length > 0, "no players");
        uint256 winnerIndex = uint256(
            keccak256(abi.encodePacked(block.timestamp, block.prevrandao, players.length))
        ) % players.length;

        payable(players[winnerIndex]).transfer(address(this).balance);
        delete players;
    }
}
