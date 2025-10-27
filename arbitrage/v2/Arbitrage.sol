// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@uniswap/v2-periphery/contracts/interfaces/IUniswapV2Router02.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract ArbExecutorV2 is Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    address public immutable ROUTER = 0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff; // QuickSwap V2
    address public immutable WPOL = 0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270;

    event ArbitrageExecuted(address indexed executor, address[] path, uint256 amountIn, uint256 amountOut, uint256 profit);
    event RescueERC20(address token, address to, uint256 amount);
    event RescueNative(address to, uint256 amount);

    constructor() {}

    /**
     * @notice Execute a token-route arbitrage starting and ending with WPOL.
     * @dev Caller must be owner. Owner must have approved this contract to spend `amountIn` WPOL beforehand.
     * @param path full path array (must start and end with WPOL)
     * @param amountIn amount of WPOL to swap (wei)
     * @param minAmountOut minimum acceptable final WPOL (slippage protection)
     * @param deadline unix timestamp deadline for router call
     */
    function executeArbitrage(
        address[] calldata path,
        uint256 amountIn,
        uint256 minAmountOut,
        uint256 deadline
    ) external onlyOwner nonReentrant returns (uint256 finalOut) {
        require(path.length >= 3, "Path too short");
        require(path[0] == WPOL && path[path.length - 1] == WPOL, "Path must start/end WPOL");
        require(amountIn > 0, "amountIn zero");
        require(deadline >= block.timestamp, "deadline passed");

        IERC20 wpol = IERC20(WPOL);

        // pull WPOL from owner
        wpol.safeTransferFrom(msg.sender, address(this), amountIn);

        // approve router (set to 0 then to amountIn to be safe for tokens with old ERC20 impl)
        wpol.safeApprove(ROUTER, 0);
        wpol.safeApprove(ROUTER, amountIn);

        // call router
        uint256[] memory amounts = IUniswapV2Router02(ROUTER).swapExactTokensForTokens(
            amountIn,
            minAmountOut,
            path,
            address(this),
            deadline
        );

        finalOut = amounts[amounts.length - 1];

        // compute profit (can be 0 or negative in theory but require finalOut >= minAmountOut already)
        uint256 profit;
        if (finalOut > amountIn) profit = finalOut - amountIn;
        else profit = 0;

        // send all WPOL back to owner (executor)
        wpol.safeTransfer(msg.sender, finalOut);

        emit ArbitrageExecuted(msg.sender, path, amountIn, finalOut, profit);
    }

    /** Rescue ERC20 tokens accidentally sent to this contract */
    function rescueERC20(address token, address to, uint256 amount) external onlyOwner {
        require(to != address(0), "Invalid to");
        IERC20(token).safeTransfer(to, amount);
        emit RescueERC20(token, to, amount);
    }

    /** Rescue native MATIC if any received */
    function rescueNative(address payable to, uint256 amount) external onlyOwner {
        require(to != address(0), "Invalid to");
        to.transfer(amount);
        emit RescueNative(to, amount);
    }

    // receive payable to accept native transfers (rare)
    receive() external payable {}
}
