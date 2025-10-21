// main.js
import { scanArbitrage } from "./scanner.js";

let currentBase = "usdc";

async function runScan() {
  document.getElementById("result").innerHTML = `<p>🔍 Memindai dengan patokan ${currentBase.toUpperCase()}...</p>`;
  try {
    const results = await scanArbitrage(currentBase);
    renderResults(results);
  } catch (err) {
    document.getElementById("result").innerHTML = `<p>❌ Error: ${err.message}</p>`;
  }
}

function renderResults(results) {
  const baseSymbol = results.length > 0 ? results[0].baseSymbol || "BASE" : "BASE";

  let html = `
    <h3>Hasil Scan — Patokan: <strong>${baseSymbol}</strong></h3>
    <table>
      <thead><tr>
        <th>Token</th>
        <th>Jual (${baseSymbol})</th>
        <th>Beli (${baseSymbol})</th>
        <th>Selisih</th>
        <th>%</th>
      </tr></thead><tbody>`;

  for (const r of results) {
    if (r.skip) {
      html += `<tr><td>${r.token}</td><td colspan="4">— token patokan —</td></tr>`;
    } else if (r.error) {
      html += `<tr><td>${r.token}</td><td colspan="4">${r.error}</td></tr>`;
    } else {
      const cls = r.diffAbs > 0 ? "profit" : "loss";
      html += `
        <tr class="${cls}">
          <td>${r.token}</td>
          <td>${r.sellPrice.toFixed(6)}</td>
          <td>${r.buyPrice.toFixed(6)}</td>
          <td>${r.diffAbs.toFixed(8)}</td>
          <td>${(r.diffPct >= 0 ? '+' : '') + r.diffPct.toFixed(4)}%</td>
        </tr>`;
    }
  }

  html += "</tbody></table>";
  document.getElementById("result").innerHTML = html;
}

// Event listener
document.getElementById("scanBtn").onclick = runScan;
document.getElementById("baseToken").onchange = (e) => {
  currentBase = e.target.value;
  runScan(); // Auto-scan saat ganti patokan
};
