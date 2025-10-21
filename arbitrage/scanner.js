// scanner.js
import { dexContracts } from "./dexes.js";
import { tokens } from "./tokens.js";
import { USDC, WETH, getPrice } from "./utils.js";

export async function scanArbitrage() {
  const results = [];

  for (const token of tokens) {
    try {
      const amountToken = ethers.utils.parseUnits("1", token.decimals);
      const amountUSDC = ethers.utils.parseUnits("1", 6);

      const sellPaths = [[token.address, USDC], [token.address, WETH, USDC]];
      const buyPaths = [[USDC, token.address], [USDC, WETH, token.address]];

      let bestSell = ethers.BigNumber.from(0);
      let bestBuyAmount = ethers.BigNumber.from(0);

      for (const contract of Object.values(dexContracts)) {
        const sellOut = await getPrice(contract, amountToken, sellPaths);
        if (sellOut && sellOut.gt(bestSell)) bestSell = sellOut;

        const buyOut = await getPrice(contract, amountUSDC, buyPaths);
        if (buyOut && buyOut.gt(bestBuyAmount)) bestBuyAmount = buyOut;
      }

      const sellPrice = bestSell.gt(0) ? parseFloat(ethers.utils.formatUnits(bestSell, 6)) : null;
      const buyTokenAmount = bestBuyAmount.gt(0) ? parseFloat(ethers.utils.formatUnits(bestBuyAmount, token.decimals)) : null;
      const buyPrice = buyTokenAmount ? 1 / buyTokenAmount : null;

      if (sellPrice !== null && buyPrice !== null) {
        const diffAbs = sellPrice - buyPrice;
        const diffPct = (diffAbs / buyPrice) * 100;
        results.push({ token: token.name, sellPrice, buyPrice, diffAbs, diffPct });
      } else {
        results.push({ token: token.name, error: "No liquidity" });
      }
    } catch (err) {
      results.push({ token: token.name, error: "Error" });
    }
  }

  return results;
}