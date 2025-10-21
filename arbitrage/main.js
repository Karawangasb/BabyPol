// main.js
import { scanArbitrage } from "./scanner.js";

document.getElementById("scan").onclick = async () => {
  document.getElementById("result").innerHTML = "<p>?? Memindai...</p>";
  const results = await scanArbitrage();

  let html = `
    <table>
      <thead><tr>
        <th>Token</th>
        <th>Jual (USDC)</th>
        <th>Beli (USDC)</th>
        <th>Selisih</th>
        <th>%</th>
      </tr></thead><tbody>`;

  for (const r of results) {
    if (r.error) {
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
};