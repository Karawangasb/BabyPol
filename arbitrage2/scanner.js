// scanner.js
import { tokens } from "./tokens.js";
import { router } from "./dexes.js";

export async function scanTriangularArbitrage() {
  const opportunities = [];
  const combos = [];

  // Generate semua kombinasi 3 token unik: [A, B, C]
  for (let i = 0; i < tokens.length; i++) {
    for (let j = 0; j < tokens.length; j++) {
      for (let k = 0; k < tokens.length; k++) {
        if (i !== j && j !== k && i !== k) {
          combos.push([tokens[i], tokens[j], tokens[k]]);
        }
      }
    }
  }

  for (const [A, B, C] of combos) {
    try {
      const amountIn = ethers.utils.parseUnits("1", A.decimals);
      const path = [A.address, B.address, C.address, A.address];

      let amountsOut;
      try {
        amountsOut = await router.getAmountsOut(amountIn, path);
      } catch (e) {
        continue; // jalur tidak valid
      }

      const finalAmount = amountsOut[amountsOut.length - 1];
      const finalFloat = parseFloat(ethers.utils.formatUnits(finalAmount, A.decimals));
      const profitPct = (finalFloat - 1) * 100;

      // Tampilkan semua, bahkan rugi — untuk analisis
      opportunities.push({
        path: `${A.name} ? ${B.name} ? ${C.name} ? ${A.name}`,
        start: 1,
        end: finalFloat,
        profitPct: profitPct
      });

    } catch (err) {
      console.warn("Error on path", A.name, B.name, C.name);
    }
  }

  return opportunities;
}