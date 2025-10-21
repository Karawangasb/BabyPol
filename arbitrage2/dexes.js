// dexes.js
export const DEX_ROUTER = "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff"; // QuickSwap
export const ABI = ["function getAmountsOut(uint amountIn, address[] path) view returns (uint[] amounts)"];
export const provider = new ethers.providers.JsonRpcProvider("https://polygon-rpc.com");
export const router = new ethers.Contract(DEX_ROUTER, ABI, provider);