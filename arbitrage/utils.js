// utils.js
export const USDC = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174";
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