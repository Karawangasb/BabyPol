from web3 import Web3

# === KONEKSI KE POLYGON ===
web3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))

if not web3.is_connected():
    raise Exception("❌ Gagal terhubung ke jaringan Polygon!")

# === TOKEN ===
WMATIC = Web3.to_checksum_address("0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270")
USDC   = Web3.to_checksum_address("0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174")

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
    "ApeSwap": "0xCf083Be4164828f00cAE704EC15a36D711491284",
    "KakiDex": "0xb9dC833A87a61ee4590F189d8Fa7282031F4d7fF",
    "QuickSwap V2": "0x5757371414417b8C6CAad45bAeF941aBc7d3Ab32"
}

FEE = 0.003  # 0.3%

# === FUNGSI BANTU ===
def get_decimals(token_addr):
    contract = web3.eth.contract(address=token_addr, abi=erc20_abi)
    return contract.functions.decimals().call()

def get_pair_address(factory_addr, token_a, token_b):
    factory = web3.eth.contract(address=factory_addr, abi=factory_abi)
    return factory.functions.getPair(token_a, token_b).call()

def get_buy_sell_prices_and_liquidity(pair_address):
    pair = web3.eth.contract(address=pair_address, abi=pair_abi)
    r0, r1, _ = pair.functions.getReserves().call()
    t0 = pair.functions.token0().call()
    t1 = pair.functions.token1().call()

    dec0 = get_decimals(t0)
    dec1 = get_decimals(t1)

    adj0 = r0 / (10 ** dec0)
    adj1 = r1 / (10 ** dec1)

    if t0 == WMATIC and t1 == USDC:
        wmatic_res = adj0
        usdc_res = adj1
    elif t0 == USDC and t1 == WMATIC:
        wmatic_res = adj1
        usdc_res = adj0
    else:
        raise ValueError("Pair bukan WMATIC/USDC")

    mid_price = usdc_res / wmatic_res
    buy_price  = mid_price / (1 - FEE)   # Harga beli (kamu bayar lebih)
    sell_price = mid_price * (1 - FEE)   # Harga jual (kamu dapat lebih sedikit)

    # Likuiditas ≈ 2 * USDC_res (karena USDC ≈ $1)
    liquidity_usd = 2 * usdc_res

    return buy_price, sell_price, liquidity_usd

# === AMBIL DATA ===
print("🔍 Mendapatkan pair WMATIC/USDC dari DEX...")
dex_pairs = {}
for name, factory in dex_factories.items():
    factory_addr = Web3.to_checksum_address(factory)
    try:
        pair = get_pair_address(factory_addr, WMATIC, USDC)
        if pair != "0x0000000000000000000000000000000000000000":
            dex_pairs[name] = Web3.to_checksum_address(pair)
            print(f"  ✅ {name}: {pair}")
        else:
            print(f"  ⚠️  {name}: Pair tidak ditemukan")
    except Exception as e:
        print(f"  ❌ {name}: Error - {e}")

print("\n💰 Mengambil harga BELI, JUAL, dan LIKUIDITAS...")
dex_data = {}
MIN_LIQUIDITY_USD = 100  # Abaikan DEX dengan likuiditas < $1,00

for name, addr in dex_pairs.items():
    try:
        buy, sell, liq = get_buy_sell_prices_and_liquidity(addr)
        if liq < MIN_LIQUIDITY_USD:
            print(f"  ⚠️  {name}: Likuiditas terlalu rendah (${liq:,.2f}) — dilewati")
            continue
        dex_data[name] = {"buy": buy, "sell": sell, "liquidity": liq}
        print(f"  {name}:")
        print(f"    Beli 1 WMATIC = {buy:.6f} USDC")
        print(f"    Jual 1 WMATIC = {sell:.6f} USDC")
        print(f"    Likuiditas     = ${liq:,.2f}")
    except Exception as e:
        print(f"  ❌ {name}: Error - {e}")

# === ANALISIS ARBITRAGE ANTAR DEX ===
if len(dex_data) >= 2:
    print("\n" + "="*70)
    print("🔍 ANALISIS ARBITRAGE ANTAR DEX (WMATIC/USDC)")
    print("="*70)

    best_buy_dex = min(dex_data, key=lambda x: dex_data[x]["buy"])
    best_buy_price = dex_data[best_buy_dex]["buy"]

    best_sell_dex = max(dex_data, key=lambda x: dex_data[x]["sell"])
    best_sell_price = dex_data[best_sell_dex]["sell"]

    profit_per_wmatic = best_sell_price - best_buy_price
    print(f"Beli WMATIC di: {best_buy_dex} @ {best_buy_price:.6f} USDC")
    print(f"Jual WMATIC di: {best_sell_dex} @ {best_sell_price:.6f} USDC")
    print("-"*70)
    if profit_per_wmatic > 0:
        print(f"✅ POTENSI PROFIT: {profit_per_wmatic:.6f} USDC per WMATIC")
        print("   💡 Catatan: Pastikan gas fee < profit! (Polygon: ~$0.001–$0.01)")
    else:
        print(f"❌ TIDAK ADA ARBITRAGE: Rugi {abs(profit_per_wmatic):.6f} USDC")
    print("="*70)
elif len(dex_data) == 1:
    print("\nℹ️  Hanya 1 DEX dengan likuiditas memadai — tidak bisa arbitrase.")
else:
    print("\n⚠️  Tidak ada DEX dengan likuiditas memadai untuk analisis.")

print("\n✅ Selesai.")


