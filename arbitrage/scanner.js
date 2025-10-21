// scanner.js
import { dexContracts } from "./dexes.js";
import { tokens } from "./tokens.js";
import { BASE_TOKENS, WETH, getPrice } from "./utils.js";

export async function scanArbitrage(baseTokenKey = "usdc") {
  const base = BASE_TOKENS[baseTokenKey];
  if (!base) throw new Error("Base token tidak dikenali");

  const results = [];

  for (const token of tokens) {
    // Skip jika token sama dengan base token
    if (token.address.toLowerCase() === base.address.toLowerCase()) {
      results.push({ token: token.name, skip: true });
      continue;
    }

    try {
      const amountToken = ethers.utils.parseUnits("1", token.decimals);
      const amountBase = ethers.utils.parseUnits("1", base.decimals);

      const sellPaths = [
        [token.address, base.address],
        [token.address, WETH, base.address]
      ];
      const buyPaths = [
        [base.address, token.address],
        [base.address, WETH, token.address]
      ];

      let bestSell = ethers.BigNumber.from(0);
      let bestBuyAmount = ethers.BigNumber.from(0);

      for (const contract of Object.values(dexContracts)) {
        const sellOut = await getPrice(contract, amountToken, sellPaths);
        if (sellOut && sellOut.gt(bestSell)) bestSell = sellOut;

        const buyOut = await getPrice(contract, amountBase, buyPaths);
        if (buyOut && buyOut.gt(bestBuyAmount)) bestBuyAmount = buyOut;
      }

      const sellPrice = bestSell.gt(0) ? parseFloat(ethers.utils.formatUnits(bestSell, base.decimals)) : null;
      const buyTokenAmount = bestBuyAmount.gt(0) ? parseFloat(ethers.utils.formatUnits(bestBuyAmount, token.decimals)) : null;
      const buyPrice = buyTokenAmount ? 1 / buyTokenAmount : null;

      if (sellPrice !== null && buyPrice !== null) {
        const diffAbs = sellPrice - buyPrice;
        const diffPct = (diffAbs / buyPrice) * 100;
        results.push({
          token: token.name,
          sellPrice,
          buyPrice,
          diffAbs,
          diffPct,
          baseSymbol: base.symbol
        });
      } else {
        results.push({ token: token.name, error: "No liquidity", baseSymbol: base.symbol });
      }
    } catch (err) {
      console.error("Scan error for", token.name, err);
      results.push({ token: token.name, error: "Error", baseSymbol: base.symbol });
    }
  }

  return results;
}
