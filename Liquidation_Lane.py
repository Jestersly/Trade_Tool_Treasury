import asyncio
import json
import os
import math
from datetime import datetime
import pytz
from websockets import connect, ConnectionClosed
from termcolor import colored, cprint
from colorama import init
import pandas as pd
import xlsxwriter
from tabulate import tabulate
import pyfiglet

# Initialize Colorama
init()
print("🗄️ Libraries successfully loaded")

# Configuration
symbols = [
    'btcusdt', 'ethusdt', 'solusdt', 'bnbusdt', 'dogeusdt', 'usdcusdt',
    'xrpusdt', 'adausdt', 'maticusdt', 'tonusdt', 'linkusdt', 'trxusdt',
    'nearusdt', 'xlmusdt', 'rndrusdt', 'dotusdt', 'uniusdt', 'atomusdt',
    'xmrusdt', 'ldousdt', 'gmxusdt', 'ltcusdt', 'avaxusdt', 'bchusdt',
    'vetusdt', 'filusdt', 'etcusdt', 'algousdt', 'xtzusdt', 'eosusdt',
    'aaveusdt', 'mkrusdt', 'thetausdt', 'axsusdt', 'sandusdt', 'icpusdt',
    'shibusdt', 'aptusdt', 'grtusdt', 'enjusdt', 'chzusdt', 'manausdt',
    'sushiusdt', 'batusdt', 'zecusdt', 'dashusdt', 'neousdt', 'iotausdt',
    'omgusdt', 'cakeusdt', 'stxusdt', 'snxusdt', 'compusdt', 'zilusdt',
    'ksmusdt', 'renusdt',
    'suiusdt', 'seiusdt', 'leousdt', 'taobusdt', 'fetusdt', 'pepeusdt',
    'hbarusdt', 'arusdt', 'kasusdt', 'imxusdt', 'injusdt', 'hexusdt',
    'ftmusdt', 'mntusdt', 'bgbusdt', 'hntusdt', 'qntusdt', 'mogusdt',
    'xecusdt', 'opusdt', 'crousdt', 'runeusdt', 'turbousdt', 'bttusdt',
    'fttusdt', 'pendleusdt', '1inchusdt', 'astrusdt', 'twtusdt', 'oceanusdt',
    'blurusdt', 'nexousdt', 'glmusdt', 'galausdt', 'axlusdt', 'superusdt',
    'mplxusdt', 'rayusdt', 'omusdt', 'flokiusdt', 'mantausdt', 'eigenusdt', 'wldusdt', 'achusdt'
]



# Symbol Mappings for different exchanges
okx_symbol_map = {
    'BTC-USDT': 'btcusdt', 
    'ETH-USDT': 'ethusdt', 
    'SOL-USDT': 'solusdt',  # Add more as needed
    'BNB-USDT': 'bnbusdt',
    'DOGE-USDT': 'dogeusdt',
    'USDC-USDT': 'usdcusdt',
    'XRP-USDT': 'xrpusdt',
    'ADA-USDT': 'adausdt',
    'MATIC-USDT': 'maticusdt',
    'TON-USDT': 'tonusdt',
    'LINK-USDT': 'linkusdt',
    'TRX-USDT': 'trxusdt',
    'NEAR-USDT': 'nearusdt',
    'XLM-USDT': 'xlmusdt',
    'RNDR-USDT': 'rndrusdt',
    'DOT-USDT': 'dotusdt',
    'UNI-USDT': 'uniusdt',
    'ATOM-USDT': 'atomusdt',
    'XMR-USDT': 'xmrusdt',
    'LDO-USDT': 'ldousdt',
    'GMX-USDT': 'gmxusdt',
    'LTC-USDT': 'ltcusdt',
    'AVAX-USDT': 'avaxusdt',
    'BCH-USDT': 'bchusdt',
    'VET-USDT': 'vetusdt',
    'FIL-USDT': 'filusdt',
    'ETC-USDT': 'etcusdt',
    'ALGO-USDT': 'algousdt',
    'XTZ-USDT': 'xtzusdt',
    'EOS-USDT': 'eosusdt',
    'AAVE-USDT': 'aaveusdt',
    'MKR-USDT': 'mkrusdt',
    'THETA-USDT': 'thetausdt',
    'AXS-USDT': 'axsusdt',
    'SAND-USDT': 'sandusdt',
    'ICP-USDT': 'icpusdt',
    'SHIB-USDT': 'shibusdt',
    'APT-USDT': 'aptusdt',
    'GRT-USDT': 'grtusdt',
    'ENJ-USDT': 'enjusdt',
    'CHZ-USDT': 'chzusdt',
    'MANA-USDT': 'manausdt',
    'SUSHI-USDT': 'sushiusdt',
    'BAT-USDT': 'batusdt',
    'ZEC-USDT': 'zecusdt',
    'DASH-USDT': 'dashusdt',
    'NEO-USDT': 'neousdt',
    'IOTA-USDT': 'iotausdt',
    'OMG-USDT': 'omgusdt',
    'CAKE-USDT': 'cakeusdt',
    'STX-USDT': 'stxusdt',
    'SNX-USDT': 'snxusdt',
    'COMP-USDT': 'compusdt',
    'ZIL-USDT': 'zilusdt',
    'KSM-USDT': 'ksmusdt',
    'REN-USDT': 'renusdt',
    'SUI-USDT': 'suiusdt',
    'SEI-USDT': 'seiusdt',
    'LEO-USDT': 'leousdt',
    'TAO-USDT': 'taobusdt',
    'FET-USDT': 'fetusdt',
    'PEPE-USDT': 'pepeusdt',
    'HBAR-USDT': 'hbarusdt',
    'AR-USDT': 'arusdt',
    'KAS-USDT': 'kasusdt',
    'IMX-USDT': 'imxusdt',
    'INJ-USDT': 'injusdt',
    'HEX-USDT': 'hexusdt',
    'FTM-USDT': 'ftmusdt',
    'MNT-USDT': 'mntusdt',
    'BGB-USDT': 'bgbusdt',
    'HNT-USDT': 'hntusdt',
    'QNT-USDT': 'qntusdt',
    'MOG-USDT': 'mogusdt',
    'XEC-USDT': 'xecusdt',
    'OP-USDT': 'opusdt',
    'CRO-USDT': 'crousdt',
    'RUNE-USDT': 'runeusdt',
    'TURBO-USDT': 'turbousdt',
    'BTT-USDT': 'bttusdt',
    'FTT-USDT': 'fttusdt',
    'PENDLE-USDT': 'pendleusdt',
    '1INCH-USDT': '1inchusdt',
    'ASTR-USDT': 'astrusdt',
    'TWT-USDT': 'twtusdt',
    'OCEAN-USDT': 'oceanusdt',
    'BLUR-USDT': 'blurusdt',
    'NEXO-USDT': 'nexousdt',
    'GLM-USDT': 'glmusdt',
    'GALA-USDT': 'galausdt',
    'AXL-USDT': 'axlusdt',
    'SUPER-USDT': 'superusdt',
    'MPLX-USDT': 'mplxusdt',
    'RAY-USDT': 'rayusdt',
    'OM-USDT': 'omusdt',
    'FLOKI-USDT': 'flokiusdt',
    'MANTA-USDT': 'mantausdt',
    'EIGEN-USDT': 'eigenusdt',
    'WLD-USDT': 'wldusdt',
    'ACH-USDT': 'achusdt'
}

bitmex_symbol_map = {
    'XBTUSD': 'btcusdt',
    'ETHUSD': 'ethusdt',  # Add more as needed
    'SOLUSD': 'solusdt',
    'BNBUSD': 'bnbusdt',
    'DOGEUSD': 'dogeusdt',
    'USDCUSD': 'usdcusdt',
    'XRPUSD': 'xrpusdt',
    'ADAUSD': 'adausdt',
    'MATICUSD': 'maticusdt',
    'TONUSD': 'tonusdt',
    'LINKUSD': 'linkusdt',
    'TRXUSD': 'trxusdt',
    'NEARUSD': 'nearusdt',
    'XLMUSD': 'xlmusdt',
    'RNDRUSD': 'rndrusdt',
    'DOTUSD': 'dotusdt',
    'UNIUSD': 'uniusdt',
    'ATOMUSD': 'atomusdt',
    'XMRUSD': 'xmrusdt',
    'LDOUSD': 'ldousdt',
    'GMXUSD': 'gmxusdt',
    'LTCUSD': 'ltcusdt',
    'AVAXUSD': 'avaxusdt',
    'BCHUSD': 'bchusdt',
    'VETUSD': 'vetusdt',
    'FILUSD': 'filusdt',
    'ETCUSD': 'etcusdt',
    'ALGOUSD': 'algousdt',
    'XTZUSD': 'xtzusdt',
    'EOSUSD': 'eosusdt',
    'AAVEUSD': 'aaveusdt',
    'MKRUSD': 'mkrusdt',
    'THETAUSD': 'thetausdt',
    'AXSUSD': 'axsusdt',
    'SANDUSD': 'sandusdt',
    'ICPUSD': 'icpusdt',
    'SHIBUSD': 'shibusdt',
    'APTUSD': 'aptusdt',
    'GRTUSD': 'grtusdt',
    'ENJUSD': 'enjusdt',
    'CHZUSD': 'chzusdt',
    'MANAUSD': 'manausdt',
    'SUSHIUSD': 'sushiusdt',
    'BATUSD': 'batusdt',
    'ZECUSD': 'zecusdt',
    'DASHUSD': 'dashusdt',
    'NEOUSD': 'neousdt',
    'IOTAUSD': 'iotausdt',
    'OMGUSD': 'omgusdt',
    'CAKEUSD': 'cakeusdt',
    'STXUSD': 'stxusdt',
    'SNXUSD': 'snxusdt',
    'COMPUSD': 'compusdt',
    'ZILUSD': 'zilusdt',
    'KSMUSD': 'ksmusdt',
    'RENUSD': 'renusdt',
    'SUIUSD': 'suiusdt',
    'SEIUSD': 'seiusdt',
    'LEOUSD': 'leousdt',
    'TAOUSD': 'taobusdt',
    'FETUSD': 'fetusdt',
    'PEPEUSD': 'pepeusdt',
    'HBARUSD': 'hbarusdt',
    'ARUSD': 'arusdt',
    'KASUSD': 'kasusdt',
    'IMXUSD': 'imxusdt',
    'INJUSD': 'injusdt',
    'HEXUSD': 'hexusdt',
    'FTMUSD': 'ftmusdt',
    'MNTUSD': 'mntusdt',
    'BGBUSD': 'bgbusdt',
    'HNTUSD': 'hntusdt',
    'QNTUSD': 'qntusdt',
    'MOGUSD': 'mogusdt',
    'XECUSD': 'xecusdt',
    'OPUSD': 'opusdt',
    'CROUSD': 'crousdt',
    'RUNEUSD': 'runeusdt',
    'TURBOUSD': 'turbousdt',
    'BTTUSD': 'bttusdt',
    'FTTUSD': 'fttusdt',
    'PENDLEUSD': 'pendleusdt',
    '1INCHUSD': '1inchusdt',
    'ASTRUSD': 'astrusdt',
    'TWTUSD': 'twtusdt',
    'OCEANUSD': 'oceanusdt',
    'BLURUSD': 'blurusdt',
    'NEXOUSD': 'nexousdt',
    'GLMUSD': 'glmusdt',
    'GALAUSD': 'galausdt',
    'AXLUSD': 'axlusdt',
    'SUPERUSD': 'superusdt',
    'MPLXUSD': 'mplxusdt',
    'RAYUSD': 'rayusdt',
    'OMUSD': 'omusdt',
    'FLOKIUSD': 'flokiusdt',
    'MANTAUSD': 'mantausdt',
    'EIGENUSD': 'eigenusdt',
    'WLDUSD': 'wldusdt',
    'ACHUSD': 'achusdt'
}

bybit_symbol_map = {
    'BTCUSDT': 'btcusdt', 
    'ETHUSDT': 'ethusdt',  # Add more as needed
    'SOLUSDT': 'solusdt',
    'BNBUSDT': 'bnbusdt',
    'DOGEUSDT': 'dogeusdt',
    'USDCUSDT': 'usdcusdt',
    'XRPUSDT': 'xrpusdt',
    'ADAUSDT': 'adausdt',
    'MATICUSDT': 'maticusdt',
    'TONUSDT': 'tonusdt',
    'LINKUSDT': 'linkusdt',
    'TRXUSDT': 'trxusdt',
    'NEARUSDT': 'nearusdt',
    'XLMUSDT': 'xlmusdt',
    'RNDRUSDT': 'rndrusdt',
    'DOTUSDT': 'dotusdt',
    'UNIUSDT': 'uniusdt',
    'ATOMUSDT': 'atomusdt',
    'XMRUSDT': 'xmrusdt',
    'LDOUSDT': 'ldousdt',
    'GMXUSDT': 'gmxusdt',
    'LTCUSDT': 'ltcusdt',
    'AVAXUSDT': 'avaxusdt',
    'BCHUSDT': 'bchusdt',
    'VETUSDT': 'vetusdt',
    'FILUSDT': 'filusdt',
    'ETCUSDT': 'etcusdt',
    'ALGOUSDT': 'algousdt',
    'XTZUSDT': 'xtzusdt',
    'EOSUSDT': 'eosusdt',
    'AAVEUSDT': 'aaveusdt',
    'MKRUSDT': 'mkrusdt',
    'THETAUSDT': 'thetausdt',
    'AXSUSDT': 'axsusdt',
    'SANDUSDT': 'sandusdt',
    'ICPUSDT': 'icpusdt',
    'SHIBUSDT': 'shibusdt',
    'APTUSDT': 'aptusdt',
    'GRTUSDT': 'grtusdt',
    'ENJUSDT': 'enjusdt',
    'CHZUSDT': 'chzusdt',
    'MANAUSDT': 'manausdt',
    'SUSHIUSDT': 'sushiusdt',
    'BATUSDT': 'batusdt',
    'ZECUSDT': 'zecusdt',
    'DASHUSDT': 'dashusdt',
    'NEOUSDT': 'neousdt',
    'IOTAUSDT': 'iotausdt',
    'OMGUSDT': 'omgusdt',
    'CAKEUSDT': 'cakeusdt',
    'STXUSDT': 'stxusdt',
    'SNXUSDT': 'snxusdt',
    'COMPUSDT': 'compusdt',
    'ZILUSDT': 'zilusdt',
    'KSMUSDT': 'ksmusdt',
    'RENUSDT': 'renusdt',
    'SUIUSDT': 'suiusdt',
    'SEIUSDT': 'seiusdt',
    'LEOUSDT': 'leousdt',
    'TAOBUSD': 'taobusdt',
    'FETUSDT': 'fetusdt',
    'PEPEUSDT': 'pepeusdt',
    'HBARUSDT': 'hbarusdt',
    'ARUSDT': 'arusdt',
    'KASUSDT': 'kasusdt',
    'IMXUSDT': 'imxusdt',
    'INJUSDT': 'injusdt',
    'HEXUSDT': 'hexusdt',
    'FTMUSDT': 'ftmusdt',
    'MNTUSDT': 'mntusdt',
    'BGBUSDT': 'bgbusdt',
    'HNTUSDT': 'hntusdt',
    'QNTUSDT': 'qntusdt',
    'MOGUSDT': 'mogusdt',
    'XECUSDT': 'xecusdt',
    'OPUSDT': 'opusdt',
    'CROUSDT': 'crousdt',
    'RUNEUSDT': 'runeusdt',
    'TURBOUSDT': 'turbousdt',
    'BTTUSDT': 'bttusdt',
    'FTTUSDT': 'fttusdt',
    'PENDLEUSDT': 'pendleusdt',
    '1INCHUSDT': '1inchusdt',
    'ASTRUSDT': 'astrusdt',
    'TWTUSDT': 'twtusdt',
    'OCEANUSDT': 'oceanusdt',
    'BLURUSDT': 'blurusdt',
    'NEXOUSDT': 'nexousdt',
    'GLMUSDT': 'glmusdt',
    'GALAUSDT': 'galausdt',
    'AXLUSDT': 'axlusdt',
    'SUPERUSDT': 'superusdt',
    'MPLXUSDT': 'mplxusdt',
    'RAYUSDT': 'rayusdt',
    'OMUSDT': 'omusdt',
    'FLOKIUSDT': 'flokiusdt',
    'MANTAUSDT': 'mantausdt',
    'EIGENUSDT': 'eigenusdt',
    'WLDUSDT': 'wldusdt',
    'ACHUSDT': 'achusdt'
}

deribit_symbol_map = {
    'BTC-PERPETUAL': 'btcusdt', 
    'ETH-PERPETUAL': 'ethusdt',  # Add more as needed
    'SOL-PERPETUAL': 'solusdt',
    'BNB-PERPETUAL': 'bnbusdt',
    'DOGE-PERPETUAL': 'dogeusdt',
    'USDC-PERPETUAL': 'usdcusdt',
    'XRP-PERPETUAL': 'xrpusdt',
    'ADA-PERPETUAL': 'adausdt',
    'MATIC-PERPETUAL': 'maticusdt',
    'TON-PERPETUAL': 'tonusdt',
    'LINK-PERPETUAL': 'linkusdt',
    'TRX-PERPETUAL': 'trxusdt',
    'NEAR-PERPETUAL': 'nearusdt',
    'XLM-PERPETUAL': 'xlmusdt',
    'RNDR-PERPETUAL': 'rndrusdt',
    'DOT-PERPETUAL': 'dotusdt',
    'UNI-PERPETUAL': 'uniusdt',
    'ATOM-PERPETUAL': 'atomusdt',
    'XMR-PERPETUAL': 'xmrusdt',
    'LDO-PERPETUAL': 'ldousdt',
    'GMX-PERPETUAL': 'gmxusdt',
    'LTC-PERPETUAL': 'ltcusdt',
    'AVAX-PERPETUAL': 'avaxusdt',
    'BCH-PERPETUAL': 'bchusdt',
    'VET-PERPETUAL': 'vetusdt',
    'FIL-PERPETUAL': 'filusdt',
    'ETC-PERPETUAL': 'etcusdt',
    'ALGO-PERPETUAL': 'algousdt',
    'XTZ-PERPETUAL': 'xtzusdt',
    'EOS-PERPETUAL': 'eosusdt',
    'AAVE-PERPETUAL': 'aaveusdt',
    'MKR-PERPETUAL': 'mkrusdt',
    'THETA-PERPETUAL': 'thetausdt',
    'AXS-PERPETUAL': 'axsusdt',
    'SAND-PERPETUAL': 'sandusdt',
    'ICP-PERPETUAL': 'icpusdt',
    'SHIB-PERPETUAL': 'shibusdt',
    'APT-PERPETUAL': 'aptusdt',
    'GRT-PERPETUAL': 'grtusdt',
    'ENJ-PERPETUAL': 'enjusdt',
    'CHZ-PERPETUAL': 'chzusdt',
    'MANA-PERPETUAL': 'manausdt',
    'SUSHI-PERPETUAL': 'sushiusdt',
    'BAT-PERPETUAL': 'batusdt',
    'ZEC-PERPETUAL': 'zecusdt',
    'DASH-PERPETUAL': 'dashusdt',
    'NEO-PERPETUAL': 'neousdt',
    'IOTA-PERPETUAL': 'iotausdt',
    'OMG-PERPETUAL': 'omgusdt',
    'CAKE-PERPETUAL': 'cakeusdt',
    'STX-PERPETUAL': 'stxusdt',
    'SNX-PERPETUAL': 'snxusdt',
    'COMP-PERPETUAL': 'compusdt',
    'ZIL-PERPETUAL': 'zilusdt',
    'KSM-PERPETUAL': 'ksmusdt',
    'REN-PERPETUAL': 'renusdt',
    'SUI-PERPETUAL': 'suiusdt',
    'SEI-PERPETUAL': 'seiusdt',
    'LEO-PERPETUAL': 'leousdt',
    'TAO-PERPETUAL': 'taobusdt',
    'FET-PERPETUAL': 'fetusdt',
    'PEPE-PERPETUAL': 'pepeusdt',
    'HBAR-PERPETUAL': 'hbarusdt',
    'AR-PERPETUAL': 'arusdt',
    'KAS-PERPETUAL': 'kasusdt',
    'IMX-PERPETUAL': 'imxusdt',
    'INJ-PERPETUAL': 'injusdt',
    'HEX-PERPETUAL': 'hexusdt',
    'FTM-PERPETUAL': 'ftmusdt',
    'MNT-PERPETUAL': 'mntusdt',
    'BGB-PERPETUAL': 'bgbusdt',
    'HNT-PERPETUAL': 'hntusdt',
    'QNT-PERPETUAL': 'qntusdt',
    'MOG-PERPETUAL': 'mogusdt',
    'XEC-PERPETUAL': 'xecusdt',
    'OP-PERPETUAL': 'opusdt',
    'CRO-PERPETUAL': 'crousdt',
    'RUNE-PERPETUAL': 'runeusdt',
    'TURBO-PERPETUAL': 'turbousdt',
    'BTT-PERPETUAL': 'bttusdt',
    'FTT-PERPETUAL': 'fttusdt',
    'PENDLE-PERPETUAL': 'pendleusdt',
    '1INCH-PERPETUAL': '1inchusdt',
    'ASTR-PERPETUAL': 'astrusdt',
    'TWT-PERPETUAL': 'twtusdt',
    'OCEAN-PERPETUAL': 'oceanusdt',
    'BLUR-PERPETUAL': 'blurusdt',
    'NEXO-PERPETUAL': 'nexousdt',
    'GLM-PERPETUAL': 'glmusdt',
    'GALA-PERPETUAL': 'galausdt',
    'AXL-PERPETUAL': 'axlusdt',
    'SUPER-PERPETUAL': 'superusdt',
    'MPLX-PERPETUAL': 'mplxusdt',
    'RAY-PERPETUAL': 'rayusdt',
    'OM-PERPETUAL': 'omusdt',
    'FLOKI-PERPETUAL': 'flokiusdt',
    'MANTA-PERPETUAL': 'mantausdt',
    'EIGEN-PERPETUAL': 'eigenusdt',
    'WLD-PERPETUAL': 'wldusdt',
    'ACH-PERPETUAL': 'achusdt'
}


# Placeholder for user-selected symbols
selected_symbols = []

# Initialize cumulative sum maps and trade count maps
cumulative_sum_map_liq = {}
trade_count_map = {}
liquidations_data = []
# Threshold for liquidation size
liquidation_threshold = 0

connection_closed_logged = set()
# WebSocket URLs for different exchanges
websocket_url_liq_binance = 'wss://fstream.binance.com/ws/!forceOrder@arr'
websocket_url_liq_okx = 'wss://ws.okx.com:8443/ws/v5/public'
websocket_url_liq_bitmex = 'wss://www.bitmex.com/realtime'
websocket_url_liq_bybit = 'wss://stream.bybit.com/v5/public/linear'
websocket_url_liq_deribit = 'wss://www.deribit.com/ws/api/v2'

# Column names for the Excel export
liquidations_columns = ['symbol', 'used_trade_time', 'liquidation_type', 'usd_size']


output_directory = "/home/jestersly/Schreibtisch/Codes/_Algo_Trade_Edge/Data_Streams/Liqs_and_Trades_Archive/" #Change this
print("📡 Configuration loaded")

# Ensure the output directory exists
os.makedirs(output_directory, exist_ok=True)

# Initialize Maps and Variables
# Initialize Variables
name_map = {
    'BTC': '🟡BTC ', 'ETH': '💠ETH ', 'SOL': '👾SOL ', 'BNB': '🔶BNB ', 'DOGE': '🐶DOGE',
    'USDC': '💵USDC', 'XRP': '⚫XRP ', 'ADA': '🔵ADA ', 'MATIC': '🟣MATIC',
    'TON': '🎮TON ', 'LINK': '🔗LINK', 'TRX': '⚙️TRX ', 'NEAR': '🔍NEAR', 'XLM': '🌟XLM ',
    'RNDR': '🎨RNDR', 'DOT': '⚪DOT ', 'UNI': '🦄UNI ', 'ATOM': '⚛️ATOM', 'XMR': '👽XMR ',
    'LDO': '🧪LDO ', 'GMX': '🌀GMX ', 'LTC': '🌕LTC ', 'AVAX': '🏔️AVAX', 'BCH': '💰BCH ',
    'VET': '♻️VET ', 'FIL': '📁FIL ', 'ETC': '⛏️ETC ', 'ALGO': '🔺ALGO', 'XTZ': '🏺XTZ ',
    'EOS': '🌐EOS ', 'AAVE': '🏦AAVE', 'MKR': '🏭MKR ', 'THETA': '📺THET', 'AXS': '🕹️AXS ',
    'SAND': '🏖️SAND', 'ICP': '🌐ICP ', 'SHIB': '🐾SHIB', 'APT': '🚀APT ', 'GRT': '📊GRT ',
    'ENJ': '🎮ENJ ', 'CHZ': '⚽CHZ ', 'MANA': '🌐MANA', 'SUSHI': '🍣SUSH', 'BAT': '🦇BAT ',
    'ZEC': '💰ZEC ', 'DASH': '⚡DASH', 'NEO': '💹NEO ', 'IOTA': '🔗IOTA', 'OMG': '😮OMG ',
    'CAKE': '🍰CAKE', 'STX': '📚STX ', 'SNX': '💎SNX ', 'COMP': '🏦COMP', 'ZIL': '💠ZIL ',
    'KSM': '🪶KSM ', 'REN': '🔄REN ',
    'SUI': '🌊SUI ', 'SEI': '🏝️SEI ', 'LEO': '🦁LEO ', 'TAO': '☯️TAO ', 'FET': '🤖FET ',
    'PEPE': '🐸PEPE', 'HBAR': '🌐HBAR', 'AR': '🕸️AR ', 'KAS': '🔷KAS ', 'IMX': '🖼️IMX ',
    'INJ': '💉INJ ', 'HEX': '🔷HEX ', 'FTM': '👻FTM ', 'MNT': '🛡️MNT ', 'BGB': '💎BGB ',
    'HNT': '📡HNT ', 'QNT': '🔢QNT ', 'MOG': '🐶MOG ', 'XEC': '💱XEC ', 'OP': '⚙️OP  ',
    'CRO': '🐾CRO ', 'RUNE': '🪄RUNE', 'TURBO': '🚀TURB', 'BTT': '🔺BTT ', 'FTT': '🪙FTT ',
    'PENDLE': '🎛️PEND', '1INCH': '🐎1IN ', 'ASTR': '🌌ASTR', 'TWT': '🔑TWT ', 'OCEAN': '🌊OCEA',
    'BLUR': '💨BLUR', 'NEXO': '🏦NEXO', 'GLM': '⚡GLM ', 'GALA': '🎉GALA', 'AXL': '🔗AXL ',
    'SUPER': '🦸SUPE', 'MPLX': '🛰️MPLX', 'RAY': '☀️RAY ', 'OM': '🕉️OM  ', 'FLOKI': '🐶FLOK',
    'MANTA': '🦈MANT', 'EIGEN': '🪞EIGE', 'WLD': '🌎WLD ', 'ACH': '🧪ACH '
}


def initialize_maps():
    """
    Initializes cumulative sum maps for selected symbols.
    """
    global cumulative_sum_map_liq
    cumulative_sum_map_liq = {symbol.upper().replace('USDT', ''): 0 for symbol in selected_symbols}


def format_trade_time(trade_time):
    """Formats the trade time to a readable format based on Berlin timezone."""
    berlin = pytz.timezone("Europe/Berlin")
    return datetime.fromtimestamp(trade_time / 1000, berlin).strftime('%H:%M:%S')

def format_usd_size(usd_size):
    """
    Formats the 'usd_size' value with green color if positive and red color if negative.
    """
    if usd_size > 0:
        return colored(f"{usd_size:,.2f}$", 'green')
    else:
        return colored(f"{usd_size:,.2f}$", 'red')

def add_cumulative_sum_column(df):
    """
    Adds a cumulative sum column to the DataFrame.
    The cumulative sum is added or subtracted based on 'trade_type' or 'liquidation_type'.
    If 'trade_type' or 'liquidation_type' is '📈 ', the value is added; if '📉 ', it is subtracted.
    """
    cumulative_sum = 0
    cumulative_sums = []

    for index, row in df.iterrows():
        if 'liquidation_type' in df.columns and row['liquidation_type'] == '📈 ':
            cumulative_sum += row['usd_size']
        elif 'liquidation_type' in df.columns and row['liquidation_type'] == '📉 ':
            cumulative_sum -= row['usd_size']

        cumulative_sums.append(cumulative_sum)

    df['cumulative_sum'] = cumulative_sums
    return df

def export_to_excel(data, columns, output_filename, directory):
    """
    Exports the specified columns of the DataFrame to Excel with a cumulative sum column.
    The output file is saved in the specified directory. If the file does not exist, it is created first.
    """
    os.makedirs(directory, exist_ok=True)
    full_path = os.path.join(directory, output_filename)

    if not os.path.isfile(full_path):
        empty_df = pd.DataFrame(columns=columns)
        with pd.ExcelWriter(full_path, engine='xlsxwriter') as writer:
            empty_df.to_excel(writer, index=False, sheet_name='Sheet1')
        print(f"Neue Datei erstellt: {full_path}")

    df = pd.DataFrame(data, columns=columns)

    if 'usd_size' in df.columns:
        df['usd_size'] = df['usd_size'].astype(float)

    if not df.empty:
        df = add_cumulative_sum_column(df)

    with pd.ExcelWriter(full_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        worksheet = writer.sheets['Sheet1']
        worksheet.set_column('A:F', 18)  # Set column width for better readability

        green_format = writer.book.add_format({'font_color': 'green'})
        red_format = writer.book.add_format({'font_color': 'red'})
        positive_bg_format = writer.book.add_format({'bg_color': '#C6EFCE'})  # Light green background
        negative_bg_format = writer.book.add_format({'bg_color': '#FFC7CE'})  # Light red background

        worksheet.conditional_format('D2:D{}'.format(len(df) + 1), {
            'type': 'formula',
            'criteria': '=$C2="📈 "',
            'format': green_format
        })
        worksheet.conditional_format('D2:D{}'.format(len(df) + 1), {
            'type': 'formula',
            'criteria': '=$C2="📉 "',
            'format': red_format
        })

        worksheet.conditional_format('E2:E{}'.format(len(df) + 1), {
            'type': 'cell',
            'criteria': '>',
            'value': 0,
            'format': positive_bg_format
        })
        worksheet.conditional_format('E2:E{}'.format(len(df) + 1), {
            'type': 'cell',
            'criteria': '<',
            'value': 0,
            'format': negative_bg_format
        })
    


def calculate_time_difference(start_time, used_trade_time):
    """
    Calculates the time difference between start_time and used_trade_time.
    Assumes used_trade_time is just a time (HH:MM:SS) format and appends it to the start date.
    """
    # Convert start_time to datetime
    start_datetime = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    
    # Convert used_trade_time to datetime assuming the same date as start_time
    # Adding the time component from used_trade_time to start_datetime's date
    used_time = datetime.strptime(used_trade_time, '%H:%M:%S').time()
    used_datetime = datetime.combine(start_datetime.date(), used_time)
    
    # Calculate the time difference
    time_difference = used_datetime - start_datetime
    
    # Return time difference in a readable format
    return time_difference


async def periodic_export(interval, liquidation_threshold, start_time):
    """
    Periodically exports the collected trade and liquidation data to Excel files.
    """
    # Initialize cumulative values and counts
    total_liquidations_above_threshold = 0
    total_usd_size_liq = 0

    while True:
        try:
            await asyncio.sleep(interval)
            total_intervals += 1
            # Stars counting dictionaries for trades and liquidations
            stars_count_liquidations = {}

            liquidations_above_threshold = sum(1 for liquidation in liquidations_data if liquidation[3] >= liquidation_threshold)

            usd_size_sum_liq = sum(liquidation[3] if liquidation[2] == '📈 ' else -liquidation[3] for liquidation in liquidations_data)

            total_liquidations_above_threshold += liquidations_above_threshold
            total_usd_size_liq += usd_size_sum_liq


            # Iterate over liquidations to count stars occurrences and accumulate usd_size
            for liquidation in liquidations_data:
                usd_size = liquidation[3]
                stars = get_liq_stars(usd_size)
                liquidation_type = liquidation[2]
                if stars not in stars_count_liquidations:
                    stars_count_liquidations[stars] = {'📈 ': {'count': 0, 'total_usd_size': 0}, '📉 ': {'count': 0, 'total_usd_size': 0}}
                stars_count_liquidations[stars][liquidation_type]['count'] += 1
                stars_count_liquidations[stars][liquidation_type]['total_usd_size'] += usd_size

            # Calculate averages
            avg_liquidations_per_minute = total_liquidations_above_threshold / total_intervals if total_intervals > 0 else 0
            avg_usd_size_per_minute_liq = total_usd_size_liq / total_intervals if total_intervals > 0 else 0

            usd_size_color_liq = 'green' if avg_usd_size_per_minute_liq > 0 else 'red'

            # Calculate counts for liquidations
            liquidations_count = len(liquidations_data)
            liquidations_long_count = sum(1 for liquidation in liquidations_data if liquidation[2] == '📈 ')
            liquidations_short_count = sum(1 for liquidation in liquidations_data if liquidation[2] == '📉 ')

            # Calculate total usd_size for liquidations
            total_usd_size_long_liq = sum(liquidation[3] for liquidation in liquidations_data if liquidation[2] == '📈 ')
            total_usd_size_short_liq = sum(liquidation[3] for liquidation in liquidations_data if liquidation[2] == '📉 ')

            usd_size_difference_liq = total_usd_size_long_liq - total_usd_size_short_liq

            difference_color_liq = 'green' if usd_size_difference_liq > 0 else 'red'

            print(f"\n🌊 A total of {liquidations_count} Liquidations above {liquidation_threshold}$")
            print(colored(f"📈Total Count: {liquidations_long_count}  | 📈Total Size: {total_usd_size_long_liq:,.2f}$", 'white', 'on_green'))
            print(colored(f"📉Total Count: {liquidations_short_count} | 📉Total Size: {total_usd_size_short_liq:,.2f}$", 'white', 'on_red'))
            print("🔍 Liquidation Sizes:")
            # Sort and display liquidations with 📈 first and 📉 second
            for liquidation_type in ['📈 ', '📉 ']:
                for stars, data in stars_count_liquidations.items():
                    if data[liquidation_type]['count'] > 0:
                        usd_size_color_liq = 'green' if liquidation_type == '📈 ' else 'red'
                        print(f"  {stars}: {liquidation_type}{data[liquidation_type]['count']} Liquidations | Total USD Size: {colored(f'{data[liquidation_type]['total_usd_size']:,.2f}$', usd_size_color_liq)}")
            print(colored(f"Difference: {usd_size_difference_liq:,.2f}$", difference_color, attrs=['bold']))
            print(colored(f"📊 Avg. Liquidations per interval: {avg_liquidations_per_minute:.2f}", 'black', 'on_white'))
            print(colored(f"📊Avg. USD Size per interval: {avg_usd_size_per_minute_liq:.2f}$", usd_size_color_liq, 'on_white', attrs=['bold']))
            print(f"\n--------------------------------------------------------------------")

            # Generate filenames that include the threshold values
            liquidations_filename = f"Liquidations_threshold_{liquidation_threshold}.xlsx"

            # Export to Excel with the generated filenames
            export_to_excel(liquidations_data, liquidations_columns, liquidations_filename, output_directory)

        except Exception as e:
            print(f"Error during export: {e}")



def collect_liquidation_data(symbol, used_trade_time, liquidation_type, usd_size):
    """
    Collects liquidation data and appends it to the liquidations_data list.
    """
    liquidations_data.append([symbol, used_trade_time, liquidation_type, usd_size])

def add_color_border(text, color):
    lines = text.split('\n')
    width = max(len(line) for line in lines)
    top_border = colored('+' + '-' * (68) + '+', color)
    bottom_border = colored('+' + '-' * (68) + '+', color)
    bordered_text = top_border + '\n'
    for line in lines:
        bordered_text += colored('|', color) + ' ' + line + ' ' * (width - len(line)) + colored('|', color) + '\n'
    bordered_text += bottom_border
    return bordered_text

def get_liq_stars(usd_size):
    if usd_size > 46368000:
        return '🌊💰♒💰🌊'
    elif usd_size > 28657000:
        return '  ♒♒♒  '
    elif usd_size > 17711000:
        return '   ♒♒   '
    elif usd_size > 10946000:
        return '    ♒    '
    elif usd_size > 6765000:
        return '  🌊🌊🌊  '
    elif usd_size > 4181000:
        return '   🌊🌊   '
    elif usd_size > 2584000:
        return '    🌊    '
    elif usd_size > 1597000:
        return '  ⛲⛲⛲  '
    elif usd_size > 987000:
        return '   ⛲⛲   '
    elif usd_size > 610000:
        return '    ⛲    '
    elif usd_size > 377000:
        return '  🪣🪣🪣  '
    elif usd_size > 233000:
        return '   🪣🪣   '
    elif usd_size > 144000:
        return '    🪣    '
    elif usd_size > 89000:
        return '💦💦💦💦💦'
    elif usd_size > 55000:
        return ' 💦💦💦💦 '
    elif usd_size > 34000:
        return '  💦💦💦  '
    elif usd_size > 21000:
        return '   💦💦   '
    elif usd_size > 13000:
        return '    💦    '
    elif usd_size > 8000:
        return '💧💧💧💧💧'
    elif usd_size > 5000:
        return ' 💧💧💧💧 '
    elif usd_size > 3000:
        return '  💧💧💧  '
    elif usd_size > 2000:
        return '   💧💧   '
    elif usd_size > 1000:
        return '    💧    '
    else:
        return '          '


def get_attrs_liquidations(usd_size):
    if usd_size >= 1000000:
        return ['bold', 'blink']
    elif usd_size >= 500000:
        return ['bold']
    else:
        return []



def update_cumulative_sum_liq(symbol, usd_size, liquidation_type):
    if liquidation_type == '📉':
        cumulative_sum_map_liq[symbol] -= usd_size
    else:
        cumulative_sum_map_liq[symbol] += usd_size
    return cumulative_sum_map_liq[symbol]

def format_cumulative_sum(cumulative_sum):
    cumulative_sum_color = 'green' if cumulative_sum > 0 else 'red'
    return colored(f"{cumulative_sum:,.0f}$", cumulative_sum_color, attrs=['bold'])

def format_usd_size(usd_size, trade_type):
    usd_size_color = 'green' if trade_type == '📈 ' else 'red'
    return colored(f"{usd_size:,.0f}$", usd_size_color)

def get_stars_padding(usd_size, max_price):
    max_usd_size_length = len(f"{max_price:,.0f}$")
    return ' ' * (max_usd_size_length - len(f"{usd_size:,.0f}$"))

def update_trade_count(formatted_symbol, stars, trade_type):
    key = (formatted_symbol, stars, trade_type)
    if key not in trade_count_map:
        trade_count_map[key] = 0
    trade_count_map[key] += 1
# Process Liquidation Function
# Process Liquidation Function
async def process_liquidation(symbol, side, timestamp, usd_size):
    global liquidation_threshold
    berlin = pytz.timezone("Europe/Berlin")
    used_trade_time = format_trade_time(timestamp)
    liquidation_type = '📉 ' if side == 'SELL' else '📈 '
    max_price = 1000000000

    # If selected_symbols is not 'ALL', filter symbols
    if selected_symbols != 'ALL' and (symbol.lower() + "usdt") not in selected_symbols:
        return  # Ignore if the symbol is not in the selected symbols

    formatted_symbol = symbol.ljust(6)[:6]

    if usd_size >= liquidation_threshold:
        if formatted_symbol not in cumulative_sum_map_liq:
            cumulative_sum_map_liq[formatted_symbol] = 0

        stars = get_liq_stars(usd_size)

        # Collect data
        collect_liquidation_data(formatted_symbol, used_trade_time, liquidation_type, usd_size)

        cumulative_sum = update_cumulative_sum_liq(formatted_symbol, usd_size, liquidation_type)
        cumulative_sum_str = format_cumulative_sum(cumulative_sum)
        usd_size_str = format_usd_size(usd_size, liquidation_type)
        attrs = get_attrs_liquidations(usd_size)
        stars_padding = get_stars_padding(usd_size, max_price)
        output = f"{name_map.get(formatted_symbol.strip(), formatted_symbol)}{'|'}{stars}{'|'}{used_trade_time}{'|'}{liquidation_type}{usd_size_str}{stars_padding}{'|'} 💧🟰 {cumulative_sum_str}"

        if usd_size > 10000000:
            output = add_color_border(output, 'green')
        elif usd_size < -10000000:
            output = add_color_border(output, 'red')

        cprint(output, 'white', attrs=attrs)
        update_trade_count(formatted_symbol, stars, liquidation_type)

# Binance Liquidation Stream
async def binance_liquidation(uri):
    while True:
        try:
            print(f"📶  Binance Liquidation » {uri}")
            async with connect(uri, max_size=None) as websocket:
                while True:
                    msg = await websocket.recv()
                    order_data = json.loads(msg)['o']
                    symbol = order_data['s'].replace('USDT', '')
                    side = order_data['S']
                    timestamp = int(order_data['T'])
                    filled_quantity = float(order_data['z'])
                    price = float(order_data['p'])
                    usd_size = filled_quantity * price

                    # Check if the symbol is in the selected symbols if not 'ALL'
                    if selected_symbols == 'ALL' or (symbol.lower() + "usdt") in selected_symbols:
                        if usd_size >= liquidation_threshold:
                            await process_liquidation(symbol, side, timestamp, usd_size)
        except ConnectionClosed as e:
            print(f"📡 ❗ 🛰️: {e}.  5 Seconds 🔃")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"❗Error❗: {e}.  5 Seconds 🔃")
            await asyncio.sleep(5)

# WebSocket function for OKX
async def okx_liquidation(uri):
    while True:
        try:
            async with connect(uri) as websocket:
                subscribe_msg = {"op": "subscribe", "args": ["liquidation"]}  # Adjust subscription as needed
                await websocket.send(json.dumps(subscribe_msg))
                while True:
                    msg = await websocket.recv()
                    data = json.loads(msg)
                    if "data" in data:
                        for item in data["data"]:
                            symbol = okx_symbol_map.get(item['instId'], None)
                            if symbol:
                                side = item['side']
                                timestamp = int(item['ts'])
                                usd_size = float(item['sz']) * float(item['px'])
                                await process_liquidation(symbol, side, timestamp, usd_size, exchange="OKX")
        except ConnectionClosed:
            await asyncio.sleep(5)

# WebSocket function for BitMEX
async def bitmex_liquidation(uri):
    while True:
        try:
            async with connect(uri) as websocket:
                subscribe_msg = {"op": "subscribe", "args": ["liquidation"]}
                await websocket.send(json.dumps(subscribe_msg))
                while True:
                    msg = await websocket.recv()
                    data = json.loads(msg)
                    if 'table' in data and data['table'] == 'liquidation':
                        for item in data['data']:
                            symbol = bitmex_symbol_map.get(item['symbol'], None)
                            if symbol:
                                side = item['side']
                                timestamp = int(datetime.strptime(item['timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp() * 1000)
                                usd_size = float(item['leavesQty']) * float(item['price'])
                                await process_liquidation(symbol, side, timestamp, usd_size, exchange="BitMEX")
        except ConnectionClosed:
            await asyncio.sleep(5)

# WebSocket function for Bybit
async def bybit_liquidation(uri):
    while True:
        try:
            async with connect(uri) as websocket:
                # Subscription für Liquidationen auf Bybit
                subscribe_msg = {
                    "op": "subscribe",
                    "args": ["liquidation.BTCUSDT"]  # Hier symbolbezogene Liquidation
                }
                await websocket.send(json.dumps(subscribe_msg))
                while True:
                    msg = await websocket.recv()
                    data = json.loads(msg)
                    if 'topic' in data and data['topic'] == 'liquidation':
                        for item in data['data']:
                            symbol = bybit_symbol_map.get(item['symbol'], None)
                            if symbol:
                                side = item['side']
                                timestamp = int(item['time'] * 1000)
                                usd_size = float(item['qty']) * float(item['price'])
                                await process_liquidation(symbol, side, timestamp, usd_size, exchange="Bybit")
        except ConnectionClosed:
            await asyncio.sleep(5)



# WebSocket function for Deribit
async def deribit_liquidation(uri):
    while True:
        try:
            async with connect(uri) as websocket:
                subscribe_msg = {
                    "jsonrpc": "2.0",
                    "method": "public/subscribe",
                    "params": {"channels": ["trades.BTC-PERPETUAL.raw", "trades.ETH-PERPETUAL.raw"]},
                    "id": 1
                }
                await websocket.send(json.dumps(subscribe_msg))
                while True:
                    msg = await websocket.recv()
                    data = json.loads(msg)
                    if 'params' in data and 'data' in data['params']:
                        for item in data['params']['data']:
                            if item.get('liquidation'):
                                symbol = deribit_symbol_map.get(item['instrument_name'], None)
                                if symbol:
                                    side = item['direction']
                                    timestamp = int(item['timestamp'])
                                    usd_size = float(item['amount']) * float(item['price'])
                                    await process_liquidation(symbol, side, timestamp, usd_size, exchange="Deribit")
        except ConnectionClosed:
            await asyncio.sleep(5)


# Adjust select_symbols to allow 'ALL' selection
def select_symbols():
    """
    Allows the user to select which symbols to include in the query.
    """
    title = ' Trade Trail '

    # Färbe den ASCII-Text blau-weiß (blau als Textfarbe, weiß als Hintergrund)
    ascii_title = '🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏\n' + pyfiglet.figlet_format(title) + '🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏'
    print(colored(ascii_title, 'red', 'on_white', attrs=['bold']))

    # Verwende pyfiglet, um den Titel in ASCII-Kunstform darzustellen
    print("""+------------------------------------------------+
|🌊🌊🪙🌊🌊🌊🌊🌊🪙🌊🌊🌊🌊🌊🌊🪙🌊🌊🌊🌊🌊🪙🌊🌊|
|📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉|
|💦🪙💦🪙💦💦💦🪙💦🪙💦💦💦💦🪙💦🪙💦💦💦🪙💦🪙💦|
|📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉|
|🪙💧💧💧🪙💧🪙💧💧💧🪙💧💧🪙💧💧💧🪙💧🪙💧💧💧🪙|
|📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉|
|🐟💵🐟💶🐟💴🐟💷🐟💵🐟💶🐟💴🐟💷🐟💵🐟💶🐟💴🐟💷|
|📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉|
|🪙🐠🐠🐠🪙🐠🪙🐠🐠🐠🪙🐠🐠🪙🐠🐠🐠🪙🐠🪙🐠🐠🐠🪙|
|📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉|
|🦑🪙🦑🪙🦑🦑🦑🪙🦑🪙🦑🦑🦑🦑🪙🦑🪙🦑🦑🦑🪙🦑🪙🦑|
|📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉|
|🐳🐳🪙🐳🐳🐳🐳🐳🪙🐳🐳🐳🐳🐳🐳🪙🐳🐳🐳🐳🐳🪙🐳🐳|
+------------------------------------------------+
         """)
    print("🛤️Trade Trail is ready to get explored 🐟🐠🦑🐳")
    
    print(colored("\n♠️♦️Choose your symbols♣️♥️", 'black', 'on_white'))

    # Erstelle eine Liste der Namenf
    name_list = [value.strip() for value in name_map.values()]

    # Teile die Liste in mehrere Spalten auf (z.B. 10 Elemente pro Spalte)
    num_rows = 10  # Anzahl der Zeilen pro Spalte
    num_columns = math.ceil(len(name_list) / num_rows)  # Berechne die Anzahl der Spalten

    # Erstelle ein 2D-Array für die Tabellendarstellung
    table_data = []
    for row_idx in range(num_rows):
        row = []
        for col_idx in range(num_columns):
            idx = row_idx + col_idx * num_rows
            if idx < len(name_list):
                row.append(name_list[idx])
            else:
                row.append("")  # Füge leere Felder hinzu, wenn die Liste nicht gleichmäßig ist
        table_data.append(row)

    # Verwende tabulate, um die Namen in Tabellenform darzustellen (ohne Symbole)
    headers = [""] * num_columns  # Keine Header für diese Darstellung
    print(tabulate(table_data, headers, tablefmt="grid"))

    print("ALL: all of them.")
    print("Type 'DONE' when you are finished.")

    global selected_symbols, selected_symbols_formatted
    selected_symbols = []

    while True:
        user_input = input("Select symbol: ").strip().upper()
        if user_input == 'ALL':
            selected_symbols = 'ALL'  # No filtering if 'ALL' is selected
            break
        elif user_input == 'DONE':
            break
        elif user_input in name_map:
            formatted_symbol = user_input.lower() + "usdt"
            if formatted_symbol not in selected_symbols:
                selected_symbols.append(formatted_symbol)
                print(f"{user_input} added.")
            else:
                print(f"{user_input} is already selected.")
        else:
            print("Invalid symbol. Please enter a valid symbol from the list above.")

async def main():
    """
    Main function that initializes thresholds, selects symbols, and starts WebSocket streams.
    """
    global liquidation_threshold
    print("⚙️ Start main function ⚙️")

    # Symbol selection
    select_symbols()  # Populate selected_symbols globally
    initialize_maps()  # Initialize the maps for cumulative sums

    # Prompt user for threshold values
    liquidation_threshold = float(input("🔧Please enter the threshold value for 'usd_size' on liquidations: "))
    interval = int(input("🔧Please enter the interval for exportation and calculation in seconds: "))

    # Capture the start time in a readable format
    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    tasks = [
        binance_liquidation(websocket_url_liq_binance),
        okx_liquidation(websocket_url_liq_okx),
        bitmex_liquidation(websocket_url_liq_bitmex),
        bybit_liquidation(websocket_url_liq_bybit),
        deribit_liquidation(websocket_url_liq_deribit)
    ]
    await asyncio.gather(*tasks)

    tasks.append(periodic_export(interval, liquidation_threshold, start_time))

    print("⚙️ asyncio.gather is running ⚙️")
    await asyncio.gather(*tasks)

# Start the main function properly
print("⚙️ asyncio.run(main()) is running ⚙️")
asyncio.run(main())
print("✅⚙️ Program is done ⚙✅️")