#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔺 Polygon Multi-DEX Arbitrage Scanner
-------------------------------------
- Jaringan: Polygon Mainnet
- DEX: QuickSwap V2, SushiSwap, Uniswap V3
- Modal: 10 POL
- Interval: 30 detik
- Token non-POL: 5 token utama
"""

import time
import random
from itertools import permutations, product
from web3 import Web3

# === WARNA TERMINAL ===
class C:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

# === RPC POLYGON ===
RPC_URL = "https://polygon-rpc.com"
web3 = Web3(Web3.HTTPProvider(RPC_URL))

if not web3.is_connected():
    raise Exception("❌ Gagal koneksi ke Polygon RPC.")

# === ROUTER ADDRESS & ABI ===
ROUTER_ABI = [{
    "name": "getAmountsOut",
    "outputs": [{"type": "uint256[]"}],
    "inputs": [
        {"name": "amountIn", "type": "uint256"},
        {"name": "path", "type": "address[]"}
    ],
    "stateMutability": "view",
    "type": "function"
}]

ROUTERS = {
    "QuickSwap": web3.eth.contract(
        address=Web3.to_checksum_address("0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff"),
        abi=ROUTER_ABI
    ),
    "SushiSwap": web3.eth.contract(
        address=Web3.to_checksum_address("0x1b02da8cb0d097eb8d57a175b88c7d8b47997506"),
        abi=ROUTER_ABI
    ),
    "UniswapV3": web3.eth.contract(
        address=Web3.to_checksum_address("0x1F98431c8aD98523631AE4a59f267346ea31F984"),
        abi=ROUTER_ABI
    ),
}

# === TOKEN ===
WPOL = Web3.to_checksum_address("0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270")
TOKENS = {
    "USDC.e": Web3.to_checksum_address("0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"),
    "USDT":   Web3.to_checksum_address("0xc2132D05D31c914a87C6611C10748AaCbC532aEd"),
    "WETH":   Web3.to_checksum_address("0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619"),
    "DAI":    Web3.to_checksum_address("0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063"),
    "WBTC":   Web3.to_checksum_address("0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6"),
}

MODAL_POL = Web3.to_wei(10, "ether")
SWAP_FEE = 0.003  # 0.3% tiap swap

# === FUNGSI MENDAPATKAN HARGA ===
def get_amount_out(router, amount_in, path):
    try:
        return router.functions.getAmountsOut(amount_in, path).call()[-1]
    except Exception:
        return 0

# === BANGUN SEMUA JALUR ANTAR DEX ===
DEX_NAMES = list(ROUTERS.keys())
token_items = list(TOKENS.items())
ALL_PATHS = []

for (sym_a, addr_a), (sym_b, addr_b) in permutations(token_items, 2):
    for dex_in, dex_mid, dex_out in product(DEX_NAMES, repeat=3):
        name = f"{dex_in}→{dex_mid}→{dex_out}: POL→{sym_a}→{sym_b}→POL"
        path = [WPOL, addr_a, addr_b, WPOL]
        ALL_PATHS.append((name, dex_in, dex_mid, dex_out, path))

print(f"✅ Total kombinasi lintas DEX: {len(ALL_PATHS)}")

# === SCAN 10 RANDOM ===
def scan_10_random():
    sampled = random.sample(ALL_PATHS, 10)
    best_pct = -float("inf")
    best_route = None
    results = []

    for name, dex1, dex2, dex3, path in sampled:
        router1, router2, router3 = ROUTERS[dex1], ROUTERS[dex2], ROUTERS[dex3]

        # POL → A
        a_out = get_amount_out(router1, MODAL_POL, [path[0], path[1]])
        if a_out == 0: continue

        # A → B
        b_out = get_amount_out(router2, a_out, [path[1], path[2]])
        if b_out == 0: continue

        # B → POL
        final_out = get_amount_out(router3, b_out, [path[2], path[3]])
        if final_out == 0: continue

        # Hitung profit & fee
        pct = (final_out - MODAL_POL) / MODAL_POL * 100
        net_pct = pct - (SWAP_FEE * 3 * 100)

        results.append((name, final_out, net_pct))

        if net_pct > best_pct:
            best_pct = net_pct
            best_route = name

    return best_pct, best_route, results

# === LOOP UTAMA ===
print("\n" + "="*60)
print(f"{C.BOLD}🔺 Multi-DEX Arbitrage Scanner (Polygon){C.RESET}")
print(f"Modal: {web3.from_wei(MODAL_POL, 'ether')} POL | DEX: {', '.join(DEX_NAMES)}")
print("="*60 + "\n")

while True:
    ts = time.strftime('%H:%M:%S')
    print(f"{C.CYAN}⏱️ Scan dimulai ({ts}) — 10 jalur acak...{C.RESET}")

    try:
        best_pct, best_route, results = scan_10_random()
    except Exception as e:
        print(f"{C.RED}❌ Error: {e}{C.RESET}")
        time.sleep(30)
        continue

    print(f"\n{C.BOLD}🔍 Hasil 10 Jalur:{C.RESET}")
    for name, out, pct in results:
        color = C.GREEN if pct > 0 else C.RED
        out_fmt = web3.from_wei(out, 'ether')
        print(f"  {color}{name} | {out_fmt:.6f} POL | Net Profit: {pct:.4f}%{C.RESET}")

    print(f"\n{C.BOLD}📊 Ringkasan:{C.RESET}")
    if best_route and best_pct > 0:
        print(f"{C.GREEN}✅ Peluang terbaik: {best_route} | Profit Bersih: {best_pct:.4f}%{C.RESET}")
    else:
        print(f"{C.YELLOW}⚪ Tidak ada peluang profit > 0%{C.RESET}")

    print("\n" + "-"*60)
    time.sleep(30)
  
