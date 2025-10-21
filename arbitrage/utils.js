// utils.js

export const BASE_TOKENS = {
  usdc: {
    symbol: "USDC",
    address: "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
    decimals: 6
  },
  usdt: {
    symbol: "USDT",
    address: "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
    decimals: 6
  },
  dai: {
    symbol: "DAI",
    address: "0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063",
    decimals: 18
  }
};

export const WETH = "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619";

export async function getPrice(contract, amountIn, paths) {
  for (const path of paths) {
    try {
      const res = await contract.getAmountsOut(amountIn, path);
      return res[res.length - 1];
    } catch (e) {
      continue;
    }
  }
  return null;
}
