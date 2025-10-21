from web3 import Web3

# RPC Polygon
w3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))

# Token address
USDC = Web3.to_checksum_address("0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174")
POL = Web3.to_checksum_address("0x0000000000000000000000000000000000001010")  # Wrapped MATIC/POL

# Router DEX
ROUTERS = {
    "QuickSwap": Web3.to_checksum_address("0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff"),
    "SushiSwap": Web3.to_checksum_address("0x1b02da8cb0d097eb8d57a175b88c7d8b47997506")
}

# ABI minimal untuk getAmountsOut
ABI = '[{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"}]'

def get_price(router_addr, token_in, token_out, amount_in_wei):
    contract = w3.eth.contract(address=router_addr, abi=ABI)
    try:
        amounts = contract.functions.getAmountsOut(amount_in_wei, [token_in, token_out]).call()
        return amounts[-1]
    except Exception as e:
        print(f"Error {router_addr}: {e}")
        return 0

def check_arbitrage():
    amount_in = w3.to_wei(1, "ether")  # 1 POL
    print("🔍 Mengecek harga POL/USDC di 2 DEX...\n")

    price_data = {}
    for name, router in ROUTERS.items():
        out = get_price(router, POL, USDC, amount_in)
        if out > 0:
            usdc_value = out / (10 ** 6)
            price_data[name] = usdc_value
            print(f"{name:10s}: 1 POL = {usdc_value:.6f} USDC")

    if len(price_data) == 2:
        dex_a, dex_b = list(price_data.keys())
        price_a, price_b = price_data[dex_a], price_data[dex_b]
        spread = (price_b - price_a) / price_a * 100

        print("\n--- Analisis ---")
        print(f"Selisih harga: {spread:.3f}%")

        # Fee DEX total (beli + jual)
        fee_total = 0.6
        net_profit = spread - fee_total

        if net_profit > 0:
            print(f"🚀 Peluang arbitrase! Net profit ≈ {net_profit:.3f}%")
            print(f"Beli di {dex_a} -> Jual di {dex_b}")
        else:
            print(f"❌ Tidak ada peluang profit. (Spread {spread:.2f}%, Fee {fee_total}%)")

if __name__ == "__main__":
    check_arbitrage()
