from web3 import Web3

# === KONEKSI KE POLYGON ===
web3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))

if not web3.is_connected():
    raise Exception("❌ Gagal terhubung ke jaringan Polygon!")

# === TOKEN ===
WMATIC = Web3.to_checksum_address("0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270")
USDC   = Web3.to_checksum_address("0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174")
USDT   = Web3.to_checksum_address("0xc2132D05D31c914a87C6611C10748AEb04B58e8F")

# === ABI ===
pair_abi = [
    {
        "constant": True,
        "inputs": [],
        "name": "getReserves",
        "outputs": [
            {"internalType": "uint112", "name": "_reserve0", "type": "uint112"},
            {"internalType": "uint112", "name": "_reserve1", "type": "uint112"},
            {"internalType": "uint32", "name": "_blockTimestampLast", "type": "uint32"}
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "token0",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "token1",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

erc20_abi = [
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

factory_abi = [
    {
        "constant": True,
        "inputs": [{"type": "address"}, {"type": "address"}],
        "name": "getPair",
        "outputs": [{"type": "address"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

# === DEX ===
dex_factories = {
    "SushiSwap": "0xc35DADB65012eC5796536bD9864eD8773aBc74C4",
    "Dfyn": "0xE7Fb3e833eFE5F9c441105EB65Ef8b261266423B",
    "ApeSwap": "0xCf083Be4164828f00cAE704EC15a36D711491284",
    "DFYN V2": "0xE7Fb3e833eFE5F9c441105EB65Ef8b261266423B",
    "KakiDex": "0xb9dC833A87a61ee4590F189d8Fa7282031F4d7fF",
    "QuickSwap V2": "0x5757371414417b8C6CAad45bAeF941aBc7d3Ab32"
}

FEE = 0.003  # 0.3%
MIN_LIQUIDITY_USD = 50.0  # Minimal likuiditas

# === FUNGSI BANTU ===
def get_decimals(token_addr):
    contract = web3.eth.contract(address=token_addr, abi=erc20_abi)
    return contract.functions.decimals().call()

def get_pair_address(factory_addr, token_a, token_b):
    factory = web3.eth.contract(address=factory_addr, abi=factory_abi)
    return factory.functions.getPair(token_a, token_b).call()

def analyze_pair(pair_address, stablecoin_symbol):
    pair = web3.eth.contract(address=pair_address, abi=pair_abi)
    r0, r1, _ = pair.functions.getReserves().call()
    t0 = pair.functions.token0().call()
    t1 = pair.functions.token1().call()

    dec0 = get_decimals(t0)
    dec1 = get_decimals(t1)

    adj0 = r0 / (10 ** dec0)
    adj1 = r1 / (10 ** dec1)

    if t0 == WMATIC and t1 in (USDC, USDT):
        wmatic_res = adj0
        stable_res = adj1
    elif t0 in (USDC, USDT) and t1 == WMATIC:
        wmatic_res = adj1
        stable_res = adj0
    else:
        raise ValueError("Pair bukan WMATIC/stablecoin")

    if wmatic_res == 0 or stable_res == 0:
        raise ValueError("Reserve nol")

    mid_price = stable_res / wmatic_res
    buy_price  = mid_price / (1 - FEE)   # Harga beli 1 WMATIC (dalam stablecoin)
    sell_price = mid_price * (1 - FEE)   # Harga jual 1 WMATIC (dalam stablecoin)
    liquidity_usd = 2 * stable_res       # Karena stablecoin ≈ $1

    return buy_price, sell_price, liquidity_usd

# === DAFTAR STABLECOIN ===
stablecoins = {
    "USDC": USDC,
    "USDT": USDT
}

# === AMBIL DATA ===
print("🔍 Mendapatkan pair WMATIC/USDC dan WMATIC/USDT dari DEX...\n")

all_dex_data = {}  # { "QuickSwap V2 | USDC": { ... }, ... }

for dex_name, factory_addr_str in dex_factories.items():
    factory_addr = Web3.to_checksum_address(factory_addr_str)
    for stable_name, stable_addr in stablecoins.items():
        key = f"{dex_name} | {stable_name}"
        try:
            pair = get_pair_address(factory_addr, WMATIC, stable_addr)
            if pair == "0x0000000000000000000000000000000000000000":
                continue
            pair = Web3.to_checksum_address(pair)

            buy, sell, liq = analyze_pair(pair, stable_name)

            if liq < MIN_LIQUIDITY_USD:
                continue

            all_dex_data[key] = {
                "dex": dex_name,
                "stablecoin": stable_name,
                "buy": buy,
                "sell": sell,
                "liquidity": liq,
                "pair_address": pair
            }

            print(f"✅ {key}")
            print(f"   Beli: {buy:.6f} {stable_name} | Jual: {sell:.6f} {stable_name} | Likuiditas: ${liq:,.2f}")
        except Exception as e:
            # Opsional: uncomment untuk debug
            # print(f"  ⚠️ {key}: {e}")
            pass

print(f"\n📊 Ditemukan {len(all_dex_data)} pair dengan likuiditas ≥ ${MIN_LIQUIDITY_USD}\n")

# === ANALISIS ARBITRAGE ===
if len(all_dex_data) >= 2:
    print("="*80)
    print("🔍 ANALISIS ARBITRAGE ANTAR DEX (WMATIC vs Stablecoin)")
    print("="*80)

    best_buy_key = min(all_dex_data, key=lambda k: all_dex_data[k]["buy"])
    best_sell_key = max(all_dex_data, key=lambda k: all_dex_data[k]["sell"])

    buy_data = all_dex_data[best_buy_key]
    sell_data = all_dex_data[best_sell_key]

    profit = sell_data["sell"] - buy_data["buy"]

    print(f"Beli di: {best_buy_key} @ {buy_data['buy']:.6f} {buy_data['stablecoin']}")
    print(f"Jual di: {best_sell_key} @ {sell_data['sell']:.6f} {sell_data['stablecoin']}")
    print("-"*80)
    if profit > 0:
        print(f"✅ POTENSI PROFIT: {profit:.6f} USD per WMATIC")
        print("💡 Catatan: Gas di Polygon sangat murah (~$0.001–$0.01). Bisa profit jika slippage rendah!")
    else:
        print(f"❌ TIDAK ADA ARBITRAGE: Rugi {abs(profit):.6f} USD")
    print("="*80)
else:
    print("ℹ️  Kurang dari 2 pair valid — arbitrase tidak mungkin.")

print("\n✅ Selesai.")
