// main.js
import { scanTriangularArbitrage } from "./scanner.js";

document.getElementById("scan").onclick = async () => {
  document.getElementById("result").innerHTML = "<p>?? Memindai triangular arbitrage...</p>";
  const results = await scanTriangularArbitrage();

  // Urutkan dari profit tertinggi
  results.sort((a, b) => b.profitPct - a.profitPct);

  let html = `<h3>Ditemukan ${results.length} kombinasi</h3><table>
    <tr><th>Path</th><th>Mulai</th><th>Akhir</th><th>Profit (%)</th></tr>`;

  for (const r of results.slice(0, 50)) { // tampilkan 50 teratas
    const cls = r.profitPct > 0 ? "profit" : "";
    html += `
      <tr class="${cls}">
        <td>${r.path}</td>
        <td>1 ${r.path.split(" ? ")[0]}</td>
        <td>${r.end.toFixed(8)}</td>
        <td>${r.profitPct >= 0 ? '+' : ''}${r.profitPct.toFixed(4)}%</td>
      </tr>`;
  }

  html += "</table><p>?? Catatan: Angka ini belum termasuk gas fee atau slippage.</p>";
  document.getElementById("result").innerHTML = html;
};