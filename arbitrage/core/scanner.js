// core/scanner.js
import { TOKENS } from "../config/tokens.js";
import { DEXES } from "../config/dexes.js";

const POL = "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270";
const POL_DECIMALS = 18;

export async function scanTriangularArbitrage(minProfitPct = 1.0) {
  const opportunities = [];

  // Cycle: POL → A → B → POL
  for (const A of TOKENS) {
    for (const B of TOKENS) {
      if (A.address === B.address) continue;
      if (A.address === POL || B.address === POL) continue;

      const path = [POL, A.address, B.address, POL];
      const amountIn = ethers.utils.parseUnits("1", POL_DECIMALS);

      for (const [dexName, contract] of Object.entries(DEXES)) {
        try {
          const amounts = await contract.getAmountsOut(amountIn, path);
          const finalAmount = amounts[amounts.length - 1];
          const finalPOL = parseFloat(ethers.utils.formatUnits(finalAmount, POL_DECIMALS));
          const profitPct = (finalPOL - 1) * 100;

          if (profitPct >= minProfitPct) {
            opportunities.push({
              dex: dexName,
              path: `POL → ${A.name} → ${B.name} → POL`,
              profitPct: profitPct.toFixed(4),
              finalPOL: finalPOL.toFixed(8)
            });
          }
        } catch (e) {
          // Skip jika path tidak valid
        }
      }
    }
  }

  return opportunities;
}
