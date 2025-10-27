// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@uniswap/v2-periphery/contracts/interfaces/IUniswapV2Router02.sol";

contract ArbExecutorV2 is Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    address public immutable WPOL = 0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270;
    address public immutable ROUTER;

    constructor(address _router, address initialOwner) Ownable(initialOwner) {
        ROUTER = _router;
    }

    function executeArb(
        address[] calldata path,
        uint256 amountIn,
        uint256 minOut
    ) external onlyOwner nonReentrant {
        IERC20 tokenIn = IERC20(path[0]);

        tokenIn.safeApprove(ROUTER, 0);
        tokenIn.safeApprove(ROUTER, amountIn);

        uint[] memory amounts = IUniswapV2Router02(ROUTER).swapExactTokensForTokens(
            amountIn,
            minOut,
            path,
            address(this),
            block.timestamp
        );

        emit ArbitrageExecuted(path[0], path[path.length - 1], amounts[0], amounts[amounts.length - 1]);
    }

    event ArbitrageExecuted(address tokenIn, address tokenOut, uint256 amountIn, uint256 amountOut);

    function withdrawToken(address token) external onlyOwner {
        IERC20(token).safeTransfer(owner(), IERC20(token).balanceOf(address(this)));
    }
}
