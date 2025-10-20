// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title Dex Price Checker for POL/USDT on Polygon
/// @notice Ambil harga langsung dari QuickSwap & SushiSwap tanpa API eksternal

interface IRouter {
    function getAmountsOut(uint amountIn, address[] calldata path)
        external
        view
        returns (uint[] memory);
}

contract PriceChecker {
    // Router DEX
    address public constant QUICKSWAP_ROUTER =
        0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff;
    address public constant SUSHISWAP_ROUTER =
        0x1b02da8cb0d097eb8d57a175b88c7d8b47997506;

    // Token address di Polygon
    address public constant USDT =
        0x170A18B9190669Cda08965562745A323C907E5Ec; // pUSDt (6 desimal)
    address public constant WPOL =
        0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270; // Wrapped POL (18 desimal)

    IRouter private quickswap = IRouter(QUICKSWAP_ROUTER);
    IRouter private sushiswap = IRouter(SUSHISWAP_ROUTER);

    /// @notice Ambil harga POL dari kedua DEX untuk jumlah USDT tertentu
    /// @param amountIn Jumlah USDT yang ingin diuji (contoh: 1e6 untuk 1 USDT)
    /// @return quickPrice Jumlah WPOL yang bisa didapat di QuickSwap
    /// @return sushiPrice Jumlah WPOL yang bisa didapat di SushiSwap
    function getDexPrices(uint amountIn)
        public
        view
        returns (uint quickPrice, uint sushiPrice)
    {
        // Deklarasi array path di dalam fungsi
        address ;
        path[0] = USDT;
        path[1] = WPOL;

        // Coba baca dari QuickSwap
        try quickswap.getAmountsOut(amountIn, path) returns (uint[] memory amountsQuick) {
            quickPrice = amountsQuick[1];
        } catch {
            quickPrice = 0;
        }

        // Coba baca dari SushiSwap
        try sushiswap.getAmountsOut(amountIn, path) returns (uint[] memory amountsSushi) {
            sushiPrice = amountsSushi[1];
        } catch {
            sushiPrice = 0;
        }
    }

    /// @notice Helper view untuk lihat harga 1 USDT (default)
    function getPrices1USDT() external view returns (uint quick, uint sushi) {
        // Panggil fungsi utama dengan 1 USDT (6 desimal)
        (quick, sushi) = getDexPrices(1e6);
    }
}
