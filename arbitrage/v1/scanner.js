// scanner.js

(async () => {
  const WPOL = "0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270".toLowerCase();
  const TOKEN_SYMBOL = Object.fromEntries(
    Object.entries(window.TOKENS).map(([k, v]) => [k.toLowerCase(), v])
  );

  const ROUTER_ADDR = "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff"; // QuickSwap V2
  const ROUTER_ABI = [
    "function getAmountsOut(uint amountIn, address[] calldata path) view returns (uint[] memory amounts)"
  ];

  // DOM elements
  const startBtn = document.getElementById('start');
  const clearBtn = document.getElementById('clear');
  const statusEl = document.getElementById('status');
  const tbl = document.getElementById('tbl');
  const tb = document.getElementById('tb');
  const bestRouteEl = document.getElementById('best-route');

  function setStatus(text) {
    statusEl.textContent = text;
  }

  function sleep(ms) {
    return new Promise(r => setTimeout(r, ms));
  }

  function formatRoute(path) {
    return path.map(a => TOKEN_SYMBOL[a] || 'UNK').join(' → ');
  }

  startBtn.addEventListener('click', async () => {
    const rpc = document.getElementById('rpc').value.trim().replace(/\s+$/, '');
    const amountStr = document.getElementById('amount').value.trim() || "1";
    const delayMs = parseInt(document.getElementById('delay').value || "200", 10);
    const onlyProfit = document.getElementById('filterProfitable').value === 'true';

    if (!rpc) {
      alert("RPC URL tidak boleh kosong.");
      return;
    }

    let amountInWei;
    try {
      amountInWei = ethers.utils.parseUnits(amountStr, 18);
    } catch (e) {
      alert("Jumlah WPOL tidak valid.");
      return;
    }

    let provider;
    try {
      provider = new ethers.providers.JsonRpcProvider(rpc);
      await provider.getBlockNumber();
    } catch (e) {
      alert("Gagal terhubung ke RPC.");
      setStatus("Error: RPC gagal");
      return;
    }

    const router = new ethers.Contract(ROUTER_ADDR, ROUTER_ABI, provider);
    const intermediates = Object.keys(window.TOKENS)
      .map(k => k.toLowerCase())
      .filter(a => a !== WPOL);

    // Generate routes
    const routes = [];

    // 3-hop
    for (let i = 0; i < intermediates.length; i++) {
      for (let j = 0; j < intermediates.length; j++) {
        if (i === j) continue;
        routes.push([WPOL, intermediates[i], intermediates[j], WPOL]);
      }
    }

    // 4-hop
    for (let i = 0; i < intermediates.length; i++) {
      for (let j = 0; j < intermediates.length; j++) {
        for (let k = 0; k < intermediates.length; k++) {
          if (i === j || j === k || i === k) continue;
          routes.push([WPOL, intermediates[i], intermediates[j], intermediates[k], WPOL]);
        }
      }
    }

    tb.innerHTML = '';
    tbl.style.display = 'table';
    bestRouteEl.innerHTML = '';
    setStatus(`Memindai ${routes.length} rute...`);

    let bestProfit = -Infinity;
    let bestRouteData = null;
    let displayedCount = 0;

    for (let idx = 0; idx < routes.length; idx++) {
      const path = routes[idx];
      setStatus(`Memindai ${idx + 1}/${routes.length} (${path.length - 2} hop)...`);

      try {
        const amounts = await router.getAmountsOut(amountInWei, path);
        const finalOut = amounts[amounts.length - 1];
        const outHuman = parseFloat(ethers.utils.formatUnits(finalOut, 18));
        const inHuman = parseFloat(amountStr);
        const profit = outHuman - inHuman;
        const profitPct = (profit / inHuman) * 100;

        if (onlyProfit && profitPct <= 0) continue;

        const routeName = formatRoute(path);

        // Simpan rute terbaik
        if (profit > bestProfit) {
          bestProfit = profit;
          bestRouteData = { routeName, outHuman, profit, profitPct };
        }

        // Tampilkan di tabel
        const tr = document.createElement('tr');
        const profitClass = profit > 0 ? 'profit-pos' : profit < 0 ? 'profit-neg' : 'profit-zero';
        tr.innerHTML = `
          <td>${++displayedCount}</td>
          <td><span class="route-path">${routeName}</span></td>
          <td>${outHuman.toFixed(8)}</td>
          <td class="${profitClass}">${profit.toFixed(8)}</td>
          <td class="${profitClass}">${profitPct.toFixed(4)}%</td>
          <td>${profit > 0 ? '✓' : '✗'}</td>
        `;
        tb.appendChild(tr);
      } catch (e) {
        // Skip error routes
      }

      await sleep(delayMs);
    }

    // Tampilkan rute terbaik
    if (bestRouteData && bestRouteData.profit > 0) {
      bestRouteEl.innerHTML = `
        <div style="margin-top:16px; padding:12px; background:#0b253a; border-radius:8px; border-left:3px solid #8de57d">
          <strong>Rute Terbaik:</strong><br>
          ${bestRouteData.routeName}<br>
          Profit: <span class="profit-pos">${bestRouteData.profit.toFixed(8)} WPOL (${bestRouteData.profitPct.toFixed(4)}%)</span>
        </div>
      `;
    } else {
      bestRouteEl.innerHTML = '<p class="muted">Tidak ada rute profitable ditemukan.</p>';
    }

    setStatus(displayedCount > 0 ? "Selesai — hasil ditampilkan" : "Selesai — tidak ada hasil");
  });

  clearBtn.addEventListener('click', () => {
    tb.innerHTML = '';
    bestRouteEl.innerHTML = '';
    tbl.style.display = 'none';
    setStatus('Dibersihkan');
  });
})();
