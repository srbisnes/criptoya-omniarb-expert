// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title OmniArbEscrow
 * @notice Escrow simple para settlement de arbitrajes omnichaín (LayerZero-ready).
 *         Elcryptoboy architecture: buy on source chain, message + settle on dest.
 * @dev Production: agregar LayerZero Endpoint, access control, reentrancy guards.
 */
contract OmniArbEscrow {
    address public owner;
    mapping(bytes32 => ArbOrder) public orders;

    struct ArbOrder {
        address buyer;
        address seller;
        uint256 amount;
        uint256 expectedProfit;
        bool settled;
        uint256 timestamp;
    }

    event ArbCreated(bytes32 indexed orderId, address indexed buyer, uint256 amount);
    event ArbSettled(bytes32 indexed orderId, uint256 profit);

    constructor() {
        owner = msg.sender;
    }

    function createArb(
        bytes32 orderId,
        address seller,
        uint256 expectedProfit
    ) external payable {
        require(msg.value > 0, "Zero amount");
        require(orders[orderId].timestamp == 0, "Order exists");

        orders[orderId] = ArbOrder({
            buyer: msg.sender,
            seller: seller,
            amount: msg.value,
            expectedProfit: expectedProfit,
            settled: false,
            timestamp: block.timestamp
        });

        emit ArbCreated(orderId, msg.sender, msg.value);
    }

    function settleArb(bytes32 orderId) external {
        ArbOrder storage order = orders[orderId];
        require(order.buyer == msg.sender || msg.sender == owner, "Unauthorized");
        require(!order.settled, "Already settled");
        require(block.timestamp <= order.timestamp + 1 hours, "Expired");

        order.settled = true;
        // En producción: transferir + fee protocol + bridge message
        (bool ok, ) = order.seller.call{value: order.amount}("");
        require(ok, "Transfer failed");

        emit ArbSettled(orderId, order.expectedProfit);
    }

    function emergencyWithdraw(bytes32 orderId) external {
        ArbOrder storage order = orders[orderId];
        require(msg.sender == owner, "Only owner");
        require(!order.settled, "Settled");
        order.settled = true;
        (bool ok, ) = owner.call{value: order.amount}("");
        require(ok, "Withdraw failed");
    }
}
