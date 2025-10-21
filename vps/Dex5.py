#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔺 Polygon Cross-DEX Arbitrage Scanner
--------------------------------------
- DEX: QuickSwap, SushiSwap, Dfyn
- Pair: POL / USDC (otomatis coba lewat WETH)
- Interval: 30 detik
- Tujuan: Cek peluang arbitrase antar DEX

by Babypol Project 🚀
"""

import time
from web3 import Web3

# === RPC Polygon ===
RPC_URL = "https://polygon-rpc.com"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    raise Exception("❌ Tidak bisa terhubung ke Polygon RPC")

# === Token Address ===
POL  = Web3.to_checksum_address("0x0000000000000000000000000000000000001010")  # Native POL (MATIC)
WETH = Web3.to_checksum_address("0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619")
USDC = Web3.to_checksum_address("0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174")

# === Router DEX ===
ROUTERS = {
    "QuickSwap": Web3.to_checksum_address("0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff"),
    "SushiSwap": Web3.to_checksum_address("0x1b02da8cb0d097eb8d57a175b88c7d8b47997506"),
    "Dfyn":      Web3.to_checksum_address("0xA102072A4C07F06EC3B4900FDC4C7B80b6c57429"),
}

# === ABI Minimal (getAmountsOut) ===
ABI = '''
[{
  "inputs": [
    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
    {"internalType": "address[]", "name": "path", "type": "address[]"}
  ],
  "name": "getAmountsOut",
  "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
  "stateMutability": "view",
  "type": "function"
}]
'''

# === Fungsi ambil harga dari DEX ===
def get_price(router_addr, token_in, token_out, amount_in_wei):
    contract = w3.eth.contract(address=router_addr, abi=ABI)
    # Coba jalur langsung (POL -> USDC)
    try:
        out = contract.functions.getAmountsOut(amount_in_wei, [token_in, token_out]).call()
        return out[-1]
    except:
        pass
    # Coba jalur dua hop (POL -> WETH -> USDC)
    try:
        out = contract.functions.getAmountsOut(amount_in_wei, [token_in, WETH, token_out]).call()
        return out[-1]
    except Exception as e:
        print(f"Error {router_addr}: {e}")
        return 0

# === Fungsi utama cek arbitrase ===
def check_arbitrage():
    amount_in = w3.to_wei(1, "ether")  # 1 POL
    print("\n🔍 Mengecek harga POL/USDC di beberapa DEX...\n")

    prices = {}
    for name, router in ROUTERS.items():
        out = get_price(router, POL, USDC, amount_in)
        if out > 0:
            usdc_value = out / (10 ** 6)
            prices[name] = usdc_value
            print(f"{name:10s}: 1 POL = {usdc_value:.6f} USDC")

    if len(prices) < 2:
        print("⚠️  Tidak cukup data harga untuk membandingkan.")
        return

    print("\n📊 Analisis spread:")
    names = list(prices.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            dex_a, dex_b = names[i], names[j]
            pa, pb = prices[dex_a], prices[dex_b]
            spread = (pb - pa) / pa * 100
            fee = 0.6  # 0.3% per swap × 2
            net = spread - fee
            if net > 0:
                print(f"✅ {dex_a} → {dex_b}: Spread {spread:.3f}%, Profit {net:.3f}% 🚀")
            else:
                print(f"❌ {dex_a} → {dex_b}: Spread {spread:.3f}%, Fee {fee:.2f}% (no profit)")

# === MAIN LOOP ===
if __name__ == "__main__":
    print("=== Polygon Cross-DEX Arbitrage Scanner ===")
    print("DEX: QuickSwap, SushiSwap, Dfyn | Pair: POL/USDC\n")

    while True:
        try:
            check_arbitrage()
        except Exception as e:
            print(f"Error utama: {e}")
        print("\n⏳ Tunggu 30 detik...\n" + "="*50)
        time.sleep(30)
