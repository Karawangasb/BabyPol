#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔺 Polygon Arbitrage Scanner — 10 Jalur Acak dari Semua Kemungkinan
------------------------------------------------------------------
- Jaringan: Polygon Mainnet
- DEX: QuickSwap V2
- Modal: 10 POL
- Interval: 30 detik
- Token non-POL: 7 → total jalur triangular = 7 × 6 = 42
- Tiap scan: pilih 10 jalur acak dari 42
"""

import time
import random
from itertools import permutations
from web3 import Web3

# === WARNA TERMINAL ===
class C:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

# === KONEKSI KE POLYGON ===
RPC_URL = "https://polygon-rpc.com"
web3 = Web3(Web3.HTTPProvider(RPC_URL))

if not web3.is_connected():
    raise Exception("❌ Gagal terhubung ke jaringan Polygon.")

# === QUICKSWAP V2 ROUTER ===
ROUTER_ADDR = Web3.to_checksum_address("0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff")
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
router = web3.eth.contract(address=ROUTER_ADDR, abi=ROUTER_ABI)

# === TOKEN (7 token non-POL) ===
WPOL = Web3.to_checksum_address("0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270")
TOKENS = {
    "USDC.e": Web3.to_checksum_address("0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"),
    "WETH":   Web3.to_checksum_address("0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619"),
    "GOON":   Web3.to_checksum_address("0x433cDE5a82b5e0658dA3543b47A375dffd126Eb6"),
    "AI":     Web3.to_checksum_address("0x2598c30330D5771AE9F983979209486aE26dE875"),
    "DADS":   Web3.to_checksum_address("0x04B48c9707fE5091Ee772d92941F745BC0AD2b8F"),
    "PAT":    Web3.to_checksum_address("0xe1FA488cEC250c4D7566a02a6B7f092196c81d11"),
    "CONE":   Web3.to_checksum_address("0xbA777aE3a3C91fCD83EF85bfe65410592Bdd0f7c"),
}

MODAL_POL = Web3.to_wei(10, "ether")

# === BUAT SEMUA JALUR TRIANGULAR: POL → A → B → POL ===
ALL_PATHS = []
token_items = list(TOKENS.items())
for (sym_a, addr_a), (sym_b, addr_b) in permutations(token_items, 2):
    name = f"POL → {sym_a} → {sym_b} → POL"
    path = [WPOL, addr_a, addr_b, WPOL]
    ALL_PATHS.append((name, path))

# Validasi otomatis: n token → n*(n-1) jalur
n = len(TOKENS)
expected = n * (n - 1)
assert len(ALL_PATHS) == expected, f"Expected {expected} paths, got {len(ALL_PATHS)}"
print(f"✅ Total jalur triangular tersedia: {len(ALL_PATHS)}")

def get_amount_out(amount_in, path):
    try:
        return router.functions.getAmountsOut(amount_in, path).call()[-1]
    except Exception:
        return 0

def scan_10_random():
    sampled = random.sample(ALL_PATHS, 10)
    best_pct = -float('inf')
    best_route = None
    results = []

    for name, path in sampled:
        final_pol = get_amount_out(MODAL_POL, path)
        if final_pol == 0:
            pct = -100.0
        else:
            pct = (final_pol - MODAL_POL) / MODAL_POL * 100
        results.append((name, final_pol, pct))

        if pct > best_pct:
            best_pct = pct
            best_route = name

    return best_pct, best_route, results

# === MAIN LOOP ===
print("\n" + "="*60)
print(f"{C.BOLD}🔺 Polygon Arbitrage: 10 dari {len(ALL_PATHS)} Jalur{C.RESET}")
print(f"Modal: {web3.from_wei(MODAL_POL, 'ether')} POL | DEX: QuickSwap V2")
print("="*60 + "\n")

while True:
    ts = time.strftime('%H:%M:%S')
    print(f"{C.CYAN}⏱️  Scan dimulai ({ts}) — Memilih 10 jalur acak...{C.RESET}")

    try:
        best_pct, best_route, results = scan_10_random()
    except Exception as e:
        print(f"{C.RED}❌ Error saat scan: {e}{C.RESET}")
        time.sleep(30)
        continue

    print(f"\n{C.BOLD}🔍 Hasil 10 Jalur Acak:{C.RESET}")
    for name, out, pct in results:
        color = C.GREEN if pct > 0 else C.RED
        out_fmt = web3.from_wei(out, 'ether') if out > 0 else 0.0
        print(f"  {color}{name} | Hasil: {out_fmt:.6f} POL | Profit: {pct:.4f}%{C.RESET}")

    print(f"\n{C.BOLD}📊 Ringkasan:{C.RESET}")
    if best_route and best_pct > 0:
        print(f"{C.GREEN}✅ Peluang terbaik: {best_route} | Profit: {best_pct:.4f}%{C.RESET}")
    else:
        print(f"{C.YELLOW}⚪ Tidak ada peluang profit > 0%{C.RESET}")

    print("\n" + "-"*60)
    time.sleep(30)
