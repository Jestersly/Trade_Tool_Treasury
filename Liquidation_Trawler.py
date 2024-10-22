import asyncio
import json
from datetime import datetime
import pytz
from websockets import connect, ConnectionClosed
from termcolor import colored
from colorama import init
from rich.live import Live
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.layout import Layout
from tabulate import tabulate
import pyfiglet
import math
import os
import pandas as pd
import random

# Initialize Colorama
init()
console = Console()

# Data Collection Dictionary for Liquidations
liquidations_data = {}
liquidations_data_lock = asyncio.Lock()  # Lock for concurrent access

# Placeholder for user-selected symbols
selected_symbols = []
selected_symbols_formatted = []
kraken_symbols_selected = []
bitfinex_symbols_selected = []
okx_symbols_selected = []
coincap_symbols_selected = []

# Liquidation WebSocket URLs
websocket_url_liq_binance = 'wss://fstream.binance.com/ws/!forceOrder@arr'
websocket_url_liq_okx = 'wss://ws.okx.com:8443/ws/v5/public'
websocket_url_liq_bitmex = 'wss://www.bitmex.com/realtime'
websocket_url_liq_bybit = 'wss://stream.bybit.com/v5/public/linear'
websocket_url_liq_deribit = 'wss://www.deribit.com/ws/api/v2'

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

# Initialize Variables
name_map = {
    'BTC': '🟡BTC ', 'ETH': '💠ETH ', 'SOL': '👾SOL ', 'BNB': '🔶BNB ', 'DOGE': '🐶DOGE',
    'USDC': '💵USDC', 'XRP': '⚫XRP ', 'ADA': '🔵ADA ', 'MATIC': '🟣MATI',
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
    'SUPER': '🦸SUPER', 'MPLX': '🛰️MPLX', 'RAY': '☀️RAY ', 'OM': '🕉️OM  ', 'FLOKI': '🐶FLOK',
    'MANTA': '🦈MANTA', 'EIGEN': 'EIGEN🪞', 'WLD': 'WLD🌎', 'ACH': 'ACH🧪'
}

# Threshold lists (use appropriate thresholds for liquidations)
stars_thresholds = [
    (46368000, '⁉️💰🃏💰⁉️'),
    (28680000, '  ♒♒♒  '),
    (17711000, '   ♒♒   '),
    (10946000, '    ♒    '),
    (6765000, '  🌊🌊🌊  '),
    (4181000, '   🌊🌊   '),
    (2584000, '    🌊    '),
    (1597000, '  ⛲⛲⛲  '),
    (987000, '   ⛲⛲   '),
    (610000, '    ⛲    '),
    (377000, '  🪣🪣🪣  '),
    (233000, '   🪣🪣   '),
    (144000, '    🪣    '),
    (89000, '💦💦💦💦💦'),
    (55000, ' 💦💦💦💦 '),
    (34000, '  💦💦💦  '),
    (21000, '   💦💦   '),
    (13000, '    💦    '),
    (8000, '💧💧💧💧💧'),
    (5000, ' 💧💧💧💧 '),
    (3000, '  💧💧💧  '),
    (2000, '   💧💧   '),
    (1000, '    💧    '),
    (0, '          ')
]


stars_thresholds_2 = [
    (317811000, '⁉️💰🃏💰⁉️'),
    (196418000, '  ♒♒♒  '),
    (121393000, '   ♒♒   '),
    (75025000,  '    ♒    '),
    (46368000,  '  🌊🌊🌊  '),
    (28657000,  '   🌊🌊   '),
    (17711000,  '    🌊    '),
    (10946000,  '⛲⛲⛲⛲⛲'),
    (6765000,   ' ⛲⛲⛲⛲ '),
    (4181000,   '  ⛲⛲⛲  '),
    (2584000,   '   ⛲⛲   '),
    (1597000,   '    ⛲    '),
    (987000,    '🪣🪣🪣🪣🪣'),
    (610000,    ' 🪣🪣🪣🪣 '),
    (377000,    '  🪣🪣🪣  '),
    (233000,    '   🪣🪣   '),
    (144000,    '    🪣    '),
    (89000,     '💦💦💦💦💦'),
    (55000,     ' 💦💦💦💦 '),
    (34000,     '  💦💦💦  '),
    (21000,     '   💦💦   '),
    (13000,     '    💦    '),
    (8000,      '💧💧💧💧💧'),
    (5000,      ' 💧💧💧💧 '),
    (3000,      '  💧💧💧  '),
    (2000,      '   💧💧   '),
    (1000,      '    💧    '),
    (0,         '          ')
]

stars_thresholds_3 = [
    (262144000, '⁉️💰🃏💰⁉️'),
    (131072000, '  ♒♒♒  '),
    (65536000,  '   ♒♒   '),
    (32768000,  '    ♒    '),
    (16384000,  '  🌊🌊🌊  '),
    (8192000,   '   🌊🌊   '),
    (4096000,   '    🌊    '),
    (2048000,   '  ⛲⛲⛲  '),
    (1024000,   '   ⛲⛲   '),
    (512000,    '    ⛲    '),
    (256000,    '  🪣🪣🪣  '),
    (128000,    '   🪣🪣   '),
    (64000,     '    🪣    '),
    (32000,     '  💦💦💦  '),
    (16000,     '   💦💦   '),
    (8000,      '    💦    '),
    (4000,      '  💧💧💧  '),
    (2000,      '   💧💧   '),
    (1000,      '    💧    '),
    (0,         '          ')
]

stars_thresholds_4 = [
    (100000000, '    ♒    '),
    (10000000,  '    🏄🏻‍♂️    '),
    (1000000,   '    🌊    '),
    (100000,    '    ⛲    '),
    (10000,     '    🪣    '),
    (1000,      '    💦    '),
    (100,       '    💧    '),
    (0,         '          ')
]

stars_thresholds_5 = [
    (5000000,     '⁉️💰🃏💰⁉️'),
    (1925000,     '♒♒♒♒♒'),
    (1775000,     ' ♒♒♒♒ '),
    (1633000,     '  ♒♒♒  '),
    (1499000,     '   ♒♒   '),
    (1373000,     '    ♒    '),
    (1255000,     '⛵⛵⛵⛵⛵'),
    (1145000,     ' ⛵⛵⛵⛵ '),
    (1043000,     '  ⛵⛵⛵  '),
    (949000,      '   ⛵⛵   '),
    (863000,      '    ⛵    '),
    (785000,      '🏄🏻‍♂️🏄🏻‍♂️🏄🏻‍♂️🏄🏻‍♂️🏄🏻‍♂️'),
    (715000,      ' 🏄🏻‍♂️🏄🏻‍♂️🏄🏻‍♂️🏄🏻‍♂️ '),
    (649000,      '  🏄🏻‍♂️🏄🏻‍♂️🏄🏻‍♂️  '),
    (587000,      '   🏄🏻‍♂️🏄🏻‍♂️   '),
    (529000,      '    🏄🏻‍♂️    '),
    (475000,      '🌊🌊🌊🌊🌊'),
    (425000,      ' 🌊🌊🌊🌊 '),
    (379000,      '  🌊🌊🌊  '),
    (337000,      '   🌊🌊   '),
    (299000,      '    🌊    '),
    (265000,      '⛲⛲⛲⛲⛲'),
    (235000,      ' ⛲⛲⛲⛲ '),
    (207000,      '  ⛲⛲⛲  '),
    (181000,      '   ⛲⛲   '),
    (157000,      '    ⛲    '),
    (135000,      '🪣🪣🪣🪣🪣'),
    (115000,      ' 🪣🪣🪣🪣 '),
    (97000,       '  🪣🪣🪣  '),
    (81000,       '   🪣🪣   '),
    (67000,       '    🪣    '),
    (55000,       '💦💦💦💦💦'),
    (45000,       ' 💦💦💦💦 '),
    (36000,       '  💦💦💦  '),
    (28000,       '   💦💦   '),
    (21000,       '    💦    '),
    (15000,       '💧💧💧💧💧'),
    (10000,       ' 💧💧💧💧 '),
    (6000,        '  💧💧💧  '),
    (3000,        '   💧💧   '),
    (1000,        '    💧    '),
    (0,           '          ')
]


# Initialize global variables
stars_thresholds = None
num_columns = None
num_rows = None



def select_thresholds():
    global stars_thresholds, num_columns, num_rows
    print("\nPlease select the threshold list to use:")
    print("1: Fibonacci Thresholds")
    print("2: Fibonacci Thresholds (Extended)")
    print("3: Squared Thresholds")
    print("4: Exponential Thresholds")
    print("5: Linear Increase Thresholds")

    choice = input("Enter your choice: ").strip()
    if choice == '1':
        stars_thresholds = stars_thresholds_1
        num_columns = 4
        num_rows = 6
    elif choice == '2':
        stars_thresholds = stars_thresholds_2
        num_columns = 4
        num_rows = 7
    elif choice == '3':
        stars_thresholds = stars_thresholds_3
        num_columns = 4
        num_rows = 5
    elif choice == '4':
        stars_thresholds = stars_thresholds_4
        num_columns = 4
        num_rows = 2
    elif choice == '5':
        stars_thresholds = stars_thresholds_5
        num_columns = 6
        num_rows = 7
    else:
        print("Invalid choice, defaulting to Detailed Thresholds.")
        stars_thresholds = stars_thresholds_1
        num_columns = 4
        num_rows = 6
        
class ThresholdConsoleManager:
    def __init__(self, num_columns, num_rows, start_time, start_timestamp, time_window_seconds, selected_symbols_display):
        self.num_columns = num_columns
        self.num_rows = num_rows
        self.start_time = start_time
        self.start_timestamp = start_timestamp
        self.time_window_seconds = time_window_seconds
        self.selected_symbols_display = selected_symbols_display
        self.layout = self.make_layout()
        self.footer_messages = []


    def make_layout(self) -> Layout:
        """Creates a layout with specified number of columns and rows of panels."""
        layout = Layout()
        # Create a header, body, and footer
        layout.split_column(
            Layout(name="header", size=4),
            Layout(name="body"),
            Layout(name="footer", size=5)
        )
        # Create column names
        col_names = [f"col{i+1}" for i in range(self.num_columns)]
        # Split the body into columns
        layout["body"].split_row(
            *[Layout(name=col_name) for col_name in col_names]
        )
        # In each column, split into rows
        for col_name in col_names:
            layout[col_name].split_column(
                *[Layout(name=f"{col_name}_row{j+1}") for j in range(self.num_rows)]
            )
        return layout

    def update_layout(self, metrics):
        """Updates the layout with the latest metrics and header information."""
        # Update header
        current_time = datetime.now().strftime("%H:%M:%S")
        total_elapsed_time = datetime.now() - datetime.strptime(self.start_time, '%Y-%m-%d %H:%M:%S')
        time_window_minutes = self.time_window_seconds / 60

        header_text = Text()
        header_text.append(f"📅 Start Time: {self.start_time}    |   ", style="bold cyan")
        header_text.append(f"⏰ Current Time: {current_time}   |   ", style="bold yellow")
        header_text.append(f"⌛ Elapsed Time: {str(total_elapsed_time).split('.')[0]}   |   ", style="bold magenta")
        header_text.append(f"🕒 Time Window: Last {time_window_minutes:.1f} minutes\n", style="bold green")
        header_text.append(f"⭐ Symbols: {self.selected_symbols_display}", style="bold green")
        self.layout["header"].update(Panel(header_text, title="Trade Trawler", border_style="magenta"))

        # Sammeln der Panels basierend auf den Metriken
        panels = []
        for stars in stars_thresholds:
            threshold, star_label = stars
            if star_label in metrics:
                panel = self.create_panel(f"{star_label}", metrics[star_label], threshold)
                total_usd_size_percentage = metrics[star_label].get('total_usd_size_percentage', 0)
                panels.append((panel, total_usd_size_percentage))

        # Sortiere die Panels nach total_usd_size_percentage absteigend
        panels.sort(key=lambda x: x[1], reverse=True)

        # Anordnung der Panels im Grid
        total_panels = self.num_columns * self.num_rows
        for i, (panel, _) in enumerate(panels[:total_panels]):
            col_num = i // self.num_rows + 1  # Spaltennummer
            row_num = i % self.num_rows + 1   # Zeilennummer
            self.layout[f"col{col_num}_row{row_num}"].update(panel)

        # Fülle restliche Layoutzellen, falls weniger Panels vorhanden sind
        for i in range(len(panels), total_panels):
            col_num = i // self.num_rows + 1
            row_num = i % self.num_rows + 1
            self.layout[f"col{col_num}_row{row_num}"].update(Panel("No Data", title="No Threshold", border_style="grey"))
        total_trades_all = metrics.get('total_trades_all', 0)
        total_trades_all_per_minute = metrics.get('total_trades_all_per_minute', 0)
        total_usd_size_all = metrics.get('total_usd_size_all', 0)
        total_usd_size_all_per_minute = metrics.get('total_usd_size_all_per_minute', 0)
        total_usd_size_all_long = metrics.get('total_usd_size_all_long', 0)
        total_usd_size_all_short = metrics.get('total_usd_size_all_short', 0)
        total_usd_size_all_long_percentage = metrics.get('total_usd_size_all_long_percentage', 0)
        total_usd_size_all_short_percentage = metrics.get('total_usd_size_all_short_percentage', 0)
        total_usd_size_all_difference = metrics.get('total_usd_size_all_difference', 0)
        total_usd_size_all_difference_percentage = metrics.get('total_usd_size_all_difference_percentage', 0)
        if total_usd_size_all_difference_percentage > 0:
            circle_usd_size = "🟢"
        else:
            circle_usd_size = "🔴"
        # Aktualisiere Footer mit Nachrichten
        footer_text = Text()
        footer_text.append(f"🎣Total🎣: {total_trades_all}{self.calculate_padding(str(total_trades_all), 20)}🎣Total/min🎣: {total_trades_all_per_minute:.2f}{self.calculate_padding(f"{total_trades_all_per_minute:,.2f}", 20)} 📈{total_usd_size_all_long:,.2f}${self.calculate_padding(f"{total_usd_size_all_long:,.2f}", 15)}📈{total_usd_size_all_long_percentage:,.2f}%{self.calculate_padding(f"{total_usd_size_all_long_percentage:,.2f}", 10)}🔰{circle_usd_size}{total_usd_size_all_difference_percentage:,.2f}%\n", style="bold")
        footer_text.append(f"💵Total💵: {total_usd_size_all:,.2f}{self.calculate_padding(f"{total_usd_size_all:,.2f}", 20)}💵Total/min💵: {total_usd_size_all_per_minute:,.2f}{self.calculate_padding(f"{total_usd_size_all_per_minute:,.2f}", 20)} 📉{total_usd_size_all_short:,.2f}${self.calculate_padding(f"{total_usd_size_all_short:,.2f}", 15)}📉{total_usd_size_all_short_percentage:,.2f}%{self.calculate_padding(f"{total_usd_size_all_short_percentage:,.2f}", 10)}🔰{circle_usd_size}{total_usd_size_all_difference:,.2f}$\n", style="bold")
        footer_text.append("📜 Recent Messages:     ", style="bold red")
        for msg in self.footer_messages[-3:]:
            footer_text.append(f"{msg}\n")
        self.layout["footer"].update(Panel(footer_text, title="Info Bar", border_style="blue"))

    def calculate_padding(self, first_param: str, target_length: int) -> str:
        """
        Calculates the padding needed to ensure a constant space between two parameters.
        The target_length specifies the desired fixed width for the first parameter, including padding.
        """
        first_param_length = len(first_param)
        padding_length = max(target_length - first_param_length, 0)
        return ' ' * padding_length

    def get_gradient_color(self, value: float, min_value: float, max_value: float) -> str:
        """
        Returns a color that represents a gradient between red, yellow, and green.
        - value: the input value that determines the color.
        - min_value: the minimum value for the gradient (corresponds to full red).
        - max_value: the maximum value for the gradient (corresponds to full green).
        """
        if value <= min_value:
            return "red"
        elif value >= max_value:
            return "green"
        elif value == 0:
            return "white"
        else:
            # Normalize the value to a range between 0 (red) and 1 (green)
            normalized_value = (value - min_value) / (max_value - min_value)
            
            # Interpolation for color gradient
            if normalized_value < 0.5:
                # Red to Yellow
                red_intensity = 255
                green_intensity = int(255 * (normalized_value * 2))
            else:
                # Yellow to Green
                red_intensity = int(255 * (2 * (1 - normalized_value)))
                green_intensity = 255
            
            # Convert to hex color code
            return f"#{red_intensity:02x}{green_intensity:02x}00"

    def create_panel(self, title: str, metrics: dict, threshold: int) -> Panel:
        """Creates a panel for displaying cumulative trade metrics since the start."""
        total_trades = metrics.get('total_trades', 0)
        long_trades = metrics.get('trades_long_count', 0)
        long_trades_percentage = metrics.get('trades_long_count_percentage', 0.0)
        short_trades = metrics.get('trades_short_count', 0)
        short_trades_percentage = metrics.get('trades_short_count_percentage', 0.0)
        trades_difference = metrics.get('trades_difference_count', 0)
        usd_size_total = metrics.get('total_usd_size', 0.0)
        usd_size_long = metrics.get('total_usd_size_long', 0.0)
        usd_size_long_percentage = metrics.get('total_usd_size_long_percentage', 0.0)
        usd_size_short = metrics.get('total_usd_size_short', 0.0)
        usd_size_short_percentage = metrics.get('total_usd_size_short_percentage', 0.0)
        usd_size_difference = metrics.get('usd_size_difference', 0.0)
        avg_trades_per_minute = metrics.get('avg_trades_per_minute', 0.0)
        avg_usd_size_per_minute = metrics.get('avg_usd_size_per_minute', 0.0)
        total_usd_size_percentage = metrics.get('total_usd_size_percentage', 0.0)
        total_trades_percentage = metrics.get('total_trades_percentage', 0.0)
        trade_count_difference_percentage = metrics.get('trade__count_difference_percentage', 0.0)
        usd_size_difference_percentage = metrics.get('usd_size_difference_percentage', 0.0)


        # Determine border color using gradient from red (-50) to yellow (0) to green (50)
        border_color = self.get_gradient_color(usd_size_difference_percentage, -50, 50)
        Circle_usd_size = "🟢" if usd_size_difference_percentage > 0 else "🔴"
        Circle_trade_count = "🟢" if trade_count_difference_percentage > 0 else "🔴"

        # Define a fixed width for the first parameter (e.g., 15 characters)
        target_length = 15

        # Panel creation and text formatting
        panel_content = Text()

        # Format each line with padding
        panel_content.append(f"🎣 Total Trades:      {total_trades}{self.calculate_padding(str(total_trades), target_length)}🧩{total_trades_percentage:.2f}%\n")
        panel_content.append(f"📈 Long Trades:       {long_trades}{self.calculate_padding(str(long_trades), target_length)}📈{long_trades_percentage:.2f}%\n")
        panel_content.append(f"📉 Short Trades:      {short_trades}{self.calculate_padding(str(short_trades), target_length)}📉{short_trades_percentage:.2f}%\n")
        panel_content.append(f"🔰 Trades Difference: {trades_difference}{self.calculate_padding(f'{trades_difference:,.2f}', target_length)}   {Circle_trade_count}{trade_count_difference_percentage:.2f}%\n")
        panel_content.append(f"📊 Avg. Trades/min:   {avg_trades_per_minute:,.2f}\n")
        panel_content.append(f"💵 USD Size:          {usd_size_total:,.2f}${self.calculate_padding(f'{usd_size_total:,.2f}$', target_length)}🧩{total_usd_size_percentage:.2f}%\n")
        panel_content.append(f"📈 Long USD Size:     {usd_size_long:,.2f}${self.calculate_padding(f'{usd_size_long:,.2f}$', target_length)}📈{usd_size_long_percentage:.2f}%\n")
        panel_content.append(f"📉 Short USD Size:    {usd_size_short:,.2f}${self.calculate_padding(f'{usd_size_short:,.2f}$', target_length)}📉{usd_size_short_percentage:.2f}%\n")
        panel_content.append(f"🔰 USD Difference:    {usd_size_difference:,.2f}${self.calculate_padding(f'{usd_size_difference:,.2f}$', target_length)}{Circle_usd_size}{usd_size_difference_percentage:.2f}%\n")
        panel_content.append(f"📊 Avg. USD/min:      {(avg_usd_size_per_minute):,.2f}$\n")

        return Panel(panel_content, title=f"{title} (≥ {threshold}$)", border_style=border_color)


    async def live_display(self):
        """Asynchronous function to update the live display."""
        with Live(self.layout, refresh_per_second=2, screen=True):
            while True:
                metrics = calculate_metrics_with_stars(liquidations_data, self.start_timestamp)
                self.update_layout(metrics)
                await asyncio.sleep(0.5)

    def print_error(self, message):
        """
        Adds an error message with timestamp and updates the layout.
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.footer_messages.append(f"[{timestamp}] {message}")
        self.update_layout()

    def print_warning(self, message):
        """
        Adds a warning message with timestamp and updates the layout.
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.footer_messages.append(f"[{timestamp}] {message}")
        self.update_layout()

    def print_info(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.footer_messages.append(f"[{timestamp}] {message}")
        self.update_layout()

def calculate_time_difference(start_time, current_time):
    # Function remains the same
    pass

def format_trade_time(trade_time):
    """Formats the trade time to a readable format based on Berlin timezone."""
    berlin = pytz.timezone("Europe/Berlin")
    return datetime.fromtimestamp(trade_time / 1000, berlin).strftime('%H:%M:%S')

async def collect_liquidation_data(symbol, used_trade_time, liquidation_type, usd_size, timestamp, threshold_console_manager):
    try:
        usd_size = float(usd_size)  # Ensure usd_size is stored as a float
    except ValueError:
        threshold_console_manager.print_error(f"Error: Invalid usd_size '{usd_size}' for liquidation.")
        return

    stars = get_stars(usd_size, threshold_console_manager)
    
    # Store the liquidation based on the threshold (as before)
    async with liquidations_data_lock:
        if stars not in liquidations_data:
            liquidations_data[stars] = []
        liquidations_data[stars].append([symbol, used_trade_time, liquidation_type, usd_size, timestamp])
        
        # Store the liquidation in a new category for all liquidations
        if "all_liquidations" not in liquidations_data:
            liquidations_data["all_liquidations"] = []
        liquidations_data["all_liquidations"].append([symbol, used_trade_time, liquidation_type, usd_size, timestamp])

def get_stars(usd_size, threshold_console_manager):
    try:
        usd_size = float(usd_size)  # Ensure usd_size is a float
    except ValueError:
        threshold_console_manager.print_error(f"Error: usd_size '{usd_size}' is not a number.")
        return '          '  # Default value if usd_size is not a number
    
    for threshold, stars in stars_thresholds:
        if usd_size >= threshold:
            return stars
    return '          '

def get_time_window():
    """
    Asks the user to input the time window (in minutes) for which liquidations should be stored and calculated.
    """
    while True:
        try:
            time_window = float(input("Enter the time window for liquidation data (in minutes): ").strip())
            if time_window <= 0:
                print("Please enter a positive number.")
                continue
            return time_window * 60  # Convert minutes to seconds
        except ValueError:
            print("Invalid input. Please enter a number.")

async def cleanup_old_liquidations(time_window, cleanup_interval=10):
    """
    Periodically removes liquidations that are older than the specified time window from liquidations_data.
    """
    while True:
        current_time_ms = datetime.now().timestamp() * 1000  # Current time in milliseconds
        cutoff_time = current_time_ms - (time_window * 1000)  # Convert time_window to milliseconds

        # Acquire lock to safely modify liquidations_data
        async with liquidations_data_lock:
            for stars in list(liquidations_data.keys()):
                liquidations_list = liquidations_data[stars]
                # Filter liquidations to keep only those within the time window
                liquidations_data[stars] = [liq for liq in liquidations_list if liq[4] >= cutoff_time]

        await asyncio.sleep(cleanup_interval)

def calculate_metrics_with_stars(liquidations_data, start_timestamp):
    # Function similar to the one in the original code, adjusted for liquidations
    # Replace 'trades' with 'liquidations' and adjust calculations accordingly
    current_time = datetime.now().timestamp() * 1000  # Current time in milliseconds
    total_elapsed_time = (current_time - start_timestamp) / 1000  # in seconds

    metrics = {}
    liquidations_list_all = liquidations_data.get('all_liquidations', [])
    total_liquidations_all = len(liquidations_list_all)
    total_liquidations_all_per_minute = (total_liquidations_all * 60) / total_elapsed_time if total_elapsed_time > 0 else 0
    total_usd_size_all_long = sum(liq[3] for liq in liquidations_list_all if liq[2] == '📈 ')
    total_usd_size_all_short = sum(liq[3] for liq in liquidations_list_all if liq[2] == '📉 ')
    total_usd_size_all = total_usd_size_all_long + total_usd_size_all_short
    total_usd_size_all_per_minute = (total_usd_size_all * 60) / total_elapsed_time if total_elapsed_time > 0 else 0
    total_usd_size_all_long_percentage = (total_usd_size_all_long / total_usd_size_all) * 100 if total_usd_size_all > 0 else 0
    total_usd_size_all_short_percentage = (total_usd_size_all_short / total_usd_size_all) * 100 if total_usd_size_all > 0 else 0
    total_usd_size_all_difference = total_usd_size_all_long - total_usd_size_all_short
    total_usd_size_all_difference_percentage = total_usd_size_all_long_percentage - total_usd_size_all_short_percentage

    for threshold, stars in stars_thresholds:
        liquidations_list = liquidations_data.get(stars, [])
        # Initialize metrics for this category
        category_metrics = {}
        total_liquidations = len(liquidations_list)

        # Long and short liquidations counts
        liquidations_long_count = sum(1 for liq in liquidations_list if liq[2] == '📈 ')
        liquidations_short_count = sum(1 for liq in liquidations_list if liq[2] == '📉 ')
        liquidations_difference_count = liquidations_long_count - liquidations_short_count

        # Percentage of Long and short liquidations
        liquidations_long_count_percentage = (liquidations_long_count / total_liquidations) * 100 if total_liquidations > 0 else 0
        liquidations_short_count_percentage = (liquidations_short_count / total_liquidations) * 100 if total_liquidations > 0 else 0
        liquidation_count_difference_percentage = liquidations_long_count_percentage - liquidations_short_count_percentage

        # Total USD size of Long and short liquidations
        total_usd_size_long = sum(liq[3] for liq in liquidations_list if liq[2] == '📈 ')
        total_usd_size_short = sum(liq[3] for liq in liquidations_list if liq[2] == '📉 ')

        total_usd_size = total_usd_size_long + total_usd_size_short
        usd_size_difference = total_usd_size_long - total_usd_size_short

        # Percentage of Long and short liquidations
        total_usd_size_long_percentage = (total_usd_size_long / total_usd_size) * 100 if total_usd_size > 0 else 0
        total_usd_size_short_percentage = (total_usd_size_short / total_usd_size) * 100 if total_usd_size > 0 else 0
        usd_size_difference_percentage = total_usd_size_long_percentage - total_usd_size_short_percentage

        # Average liquidations and USD size per minute since program start
        avg_liquidations_per_minute = (total_liquidations * 60) / total_elapsed_time if total_elapsed_time > 0 else 0
        avg_usd_size_per_minute = (total_usd_size * 60) / total_elapsed_time if total_elapsed_time > 0 else 0

        # Determine the color of the average usd_size
        usd_size_color = 'green' if avg_usd_size_per_minute > 0 else 'red'
        # Determine the color based on the difference
        difference_color = 'green' if usd_size_difference > 0 else 'red'

        # Store metrics
        category_metrics['total_trades'] = total_liquidations
        category_metrics['trades_long_count'] = liquidations_long_count
        category_metrics['trades_short_count'] = liquidations_short_count
        category_metrics['trades_difference_count'] = liquidations_difference_count
        category_metrics['trades_long_count_percentage'] = liquidations_long_count_percentage
        category_metrics['trades_short_count_percentage'] = liquidations_short_count_percentage
        category_metrics['trade__count_difference_percentage'] = liquidation_count_difference_percentage
        category_metrics['total_usd_size_long'] = total_usd_size_long
        category_metrics['total_usd_size_short'] = total_usd_size_short
        category_metrics['total_usd_size'] = total_usd_size
        category_metrics['usd_size_difference'] = usd_size_difference
        category_metrics['total_usd_size_long_percentage'] = total_usd_size_long_percentage
        category_metrics['total_usd_size_short_percentage'] = total_usd_size_short_percentage
        category_metrics['usd_size_difference_percentage'] = usd_size_difference_percentage
        category_metrics['avg_trades_per_minute'] = avg_liquidations_per_minute
        category_metrics['avg_usd_size_per_minute'] = avg_usd_size_per_minute
        category_metrics['usd_size_color'] = usd_size_color
        category_metrics['difference_color'] = difference_color

        metrics[stars] = category_metrics
        total_usd_size_all += total_usd_size

    # Compute percentage of each category in total_usd_size_all
    for stars in metrics:
        total_usd_size = metrics[stars]['total_usd_size']
        total_usd_size_percentage = (total_usd_size / total_usd_size_all) * 100 if total_usd_size_all > 0 else 0
        metrics[stars]['total_usd_size_percentage'] = total_usd_size_percentage

    #Calculate percentage of each catergory in total_liquidations
    for stars in metrics:
        total_liquidations = metrics[stars]['total_trades']
        total_liquidations_percentage = (total_liquidations / sum(metrics[s]['total_trades'] for s in metrics)) * 100 if total_liquidations > 0 else 0
        metrics[stars]['total_trades_percentage'] = total_liquidations_percentage

    metrics['total_usd_size_all'] = total_usd_size_all
    metrics['total_trades_all'] = total_liquidations_all
    metrics['total_trades_all_per_minute'] = total_liquidations_all_per_minute
    metrics['total_usd_size_all_per_minute'] = total_usd_size_all_per_minute
    metrics['total_usd_size_all_long'] = total_usd_size_all_long
    metrics['total_usd_size_all_short'] = total_usd_size_all_short
    metrics['total_usd_size_all_difference'] = total_usd_size_all_difference
    metrics['total_usd_size_all_difference_percentage'] = total_usd_size_all_difference_percentage
    metrics['total_usd_size_all_long_percentage'] = total_usd_size_all_long_percentage
    metrics['total_usd_size_all_short_percentage'] = total_usd_size_all_short_percentage

    return metrics

async def process_liquidation(symbol, side, timestamp, usd_size, threshold_console_manager):
    # Adjusted to process a liquidation event
    liquidation_type = '📉 ' if side == 'SELL' else '📈 '
    used_trade_time = format_trade_time(timestamp)
    await collect_liquidation_data(symbol, used_trade_time, liquidation_type, usd_size, timestamp, threshold_console_manager)

# Binance Liquidation Stream
async def binance_liquidation_stream(uri, threshold_console_manager):
    while True:
        try:
            async with connect(uri, max_size=None) as websocket:
                while True:
                    msg = await websocket.recv()
                    data = json.loads(msg)
                    order_data = data['o']
                    symbol = order_data['s'].replace('USDT', '')
                    side = order_data['S']
                    timestamp = int(order_data['T'])
                    filled_quantity = float(order_data['z'])
                    price = float(order_data['p'])
                    usd_size = filled_quantity * price

                    # Process the liquidation
                    await process_liquidation(symbol, side, timestamp, usd_size, threshold_console_manager)
        except ConnectionClosed:
            threshold_console_manager.print_error("No Connection📡❌🛰️ (Binance Liquidation)")
            await asyncio.sleep(5)
        except Exception as e:
            threshold_console_manager.print_error(f"An error occurred in binance_liquidation_stream: {e}")
            await asyncio.sleep(5)

async def okx_liquidation_stream(uri, threshold_console_manager):
    if not okx_symbols_selected:
        return
    while True:
        try:
            async with connect(uri, max_size=None) as websocket:
                subscribe_message = {
                    "op": "subscribe",
                    "args": [{"channel": "liquidation-orders", "instType": "SWAP", "uly": symbol} for symbol in okx_symbols_selected]
                }
                await websocket.send(json.dumps(subscribe_message))
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    if 'data' in data:
                        for liq_data in data['data']:
                            symbol = liq_data['instId']
                            if symbol in okx_symbol_map:
                                mapped_symbol = okx_symbol_map[symbol]
                                side = liq_data['side']
                                timestamp = int(liq_data['ts'])
                                usd_size = float(liq_data['sz']) * float(liq_data['price'])
                                await process_liquidation(mapped_symbol, side, timestamp, usd_size, threshold_console_manager)
        except ConnectionClosed:
            threshold_console_manager.print_error("No Connection📡❌🛰️ (OKX Liquidation)")
            await asyncio.sleep(5)
        except Exception as e:
            threshold_console_manager.print_error(f"An error occurred in okx_liquidation_stream: {e}")
            await asyncio.sleep(5)
# WebSocket function for BitMEX
async def bitmex_liquidation_stream(uri, threshold_console_manager):
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
                                await process_liquidation(symbol, side, timestamp, usd_size, threshold_console_manager)
        except ConnectionClosed:
            threshold_console_manager.print_error("No Connection📡❌🛰️ (BitMEX Liquidation)")
            await asyncio.sleep(5)
        except Exception as e:
            threshold_console_manager.print_error(f"An error occurred in bitmex_liquidation_stream: {e}")
            await asyncio.sleep(5)

# WebSocket function for Bybit
async def bybit_liquidation_stream(uri, threshold_console_manager):
    while True:
        try:
            async with connect(uri) as websocket:
                # Subscription for liquidations on Bybit
                subscribe_msg = {
                    "op": "subscribe",
                    "args": ["liquidation.ALL"]  # Adjust as needed
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
                                await process_liquidation(symbol, side, timestamp, usd_size, threshold_console_manager)
        except ConnectionClosed:
            threshold_console_manager.print_error("No Connection📡❌🛰️ (Bybit Liquidation)")
            await asyncio.sleep(5)
        except Exception as e:
            threshold_console_manager.print_error(f"An error occurred in bybit_liquidation_stream: {e}")
            await asyncio.sleep(5)


# WebSocket function for Deribit
async def deribit_liquidation_stream(uri, threshold_console_manager):
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
                                    await process_liquidation(symbol, side, timestamp, usd_size, threshold_console_manager)
        except ConnectionClosed:
            threshold_console_manager.print_error("No Connection📡❌🛰️ (Deribit Liquidation)")
            await asyncio.sleep(5)
        except Exception as e:
            threshold_console_manager.print_error(f"An error occurred in deribit_liquidation_stream: {e}")
            await asyncio.sleep(5)



def export_to_excel(liquidations_data, directory):
    """
    Exports trades data to Excel files per threshold.
    For each threshold, creates or updates an Excel file containing the trades.
    """
    # Erstelle das Verzeichnis, falls es noch nicht existiert
    os.makedirs(directory, exist_ok=True)
    
    # Bestimme den Dateinamen basierend auf den ausgewählten Symbolen
    if selected_symbols == symbols:
        symbols_name = "All"
    else:
        # Verkette die ausgewählten Symbole zu einem String, getrennt durch Bindestriche
        symbols_name = "_".join([symbol.replace("usdt", "").upper() for symbol in selected_symbols])
    
    for threshold, stars in stars_thresholds:
        liquidations = liquidations_data.get(stars, [])
        if liquidations:
            # Erstelle einen DataFrame aus den Trades
            df = pd.DataFrame(liquidations, columns=['Symbol', 'Time', 'Type', 'USD Size', 'Timestamp'])
            # Sortiere nach Timestamp
            df = df.sort_values(by='Timestamp')
            
            # Erstelle den Dateinamen unter Berücksichtigung der Symbole
            filename = f"Liquidation_Threshold_{threshold}_{symbols_name}.xlsx"
            full_path = os.path.join(directory, filename)
            
            # Speichere die Daten als Excel-Datei
            with pd.ExcelWriter(full_path, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
                worksheet = writer.sheets['Sheet1']
                worksheet.set_column('A:E', 18)  # Setze die Spaltenbreite für bessere Lesbarkeit
                
                # Anwenden von bedingten Formatierungen
                green_format = writer.book.add_format({'font_color': 'green'})
                red_format = writer.book.add_format({'font_color': 'red'})
                positive_bg_format = writer.book.add_format({'bg_color': '#C6EFCE'})  # Hellgrüner Hintergrund
                negative_bg_format = writer.book.add_format({'bg_color': '#FFC7CE'})  # Hellroter Hintergrund

                worksheet.conditional_format('C2:C{}'.format(len(df) + 1), {
                    'type': 'text',
                    'criteria': 'containing',
                    'value': '📈 ',
                    'format': green_format
                })
                worksheet.conditional_format('C2:C{}'.format(len(df) + 1), {
                    'type': 'text',
                    'criteria': 'containing',
                    'value': '📉 ',
                    'format': red_format
                })

                worksheet.conditional_format('D2:D{}'.format(len(df) + 1), {
                    'type': 'cell',
                    'criteria': '>',
                    'value': 0,
                    'format': positive_bg_format
                })
                worksheet.conditional_format('D2:D{}'.format(len(df) + 1), {
                    'type': 'cell',
                    'criteria': '<',
                    'value': 0,
                    'format': negative_bg_format
                })

    # Erstelle das Verzeichnis, falls es noch nicht existiert
    os.makedirs(directory, exist_ok=True)
    
    # Bestimme den Dateinamen basierend auf den ausgewählten Symbolen
    if selected_symbols == symbols:
        symbols_name = "All"
    else:
        # Verkette die ausgewählten Symbole zu einem String, getrennt durch Bindestriche
        symbols_name = "_".join([symbol.replace("usdt", "").upper() for symbol in selected_symbols])
    
    for threshold, stars in stars_thresholds:
        liquidations = liquidations_data.get(stars, [])
        if liquidations:
            # Erstelle einen DataFrame aus den Liquidationen
            df = pd.DataFrame(liquidations, columns=['Symbol', 'Time', 'Type', 'USD Size', 'Timestamp'])
            # Sortiere nach Timestamp
            df = df.sort_values(by='Timestamp')
            
            # Erstelle den Dateinamen unter Berücksichtigung der Symbole
            filename = f"Liquidations_Threshold_{threshold}_{symbols_name}.xlsx"
            full_path = os.path.join(directory, filename)
            
            # Speichere die Daten als Excel-Datei
            with pd.ExcelWriter(full_path, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
                worksheet = writer.sheets['Sheet1']
                worksheet.set_column('A:E', 18)  # Setze die Spaltenbreite für bessere Lesbarkeit
                
                # Anwenden von bedingten Formatierungen
                green_format = writer.book.add_format({'font_color': 'green'})
                red_format = writer.book.add_format({'font_color': 'red'})
                positive_bg_format = writer.book.add_format({'bg_color': '#C6EFCE'})  # Hellgrüner Hintergrund
                negative_bg_format = writer.book.add_format({'bg_color': '#FFC7CE'})  # Hellroter Hintergrund

                worksheet.conditional_format('C2:C{}'.format(len(df) + 1), {
                    'type': 'text',
                    'criteria': 'containing',
                    'value': '📈 ',
                    'format': green_format
                })
                worksheet.conditional_format('C2:C{}'.format(len(df) + 1), {
                    'type': 'text',
                    'criteria': 'containing',
                    'value': '📉 ',
                    'format': red_format
                })

                worksheet.conditional_format('D2:D{}'.format(len(df) + 1), {
                    'type': 'cell',
                    'criteria': '>',
                    'value': 0,
                    'format': positive_bg_format
                })
                worksheet.conditional_format('D2:D{}'.format(len(df) + 1), {
                    'type': 'cell',
                    'criteria': '<',
                    'value': 0,
                    'format': negative_bg_format
                })

async def save_data_periodically(directory, interval=60):
    """
    Periodically saves the liquidations data to Excel files every 'interval' seconds.
    """
    while True:
        export_to_excel(liquidations_data, directory)
        await asyncio.sleep(interval)


def select_symbols():
    """
    Allows the user to select which symbols to include in the query.
    """
    title = ' Liquidation Trawler'

    # Färbe den ASCII-Text blau-weiß (blau als Textfarbe, weiß als Hintergrund)
    ascii_title = '🃏' * 35 + '\n' + pyfiglet.figlet_format(title) + '🃏' * 35
    print(colored(ascii_title, 'blue', 'on_white', attrs=['bold']))
    print(colored("     🚢Liquidation Trawler sets sail and gets ready to fish🐟🐠🦑🐳     ", 'black', 'on_blue'))
    # Verwende pyfiglet, um den Titel in ASCII-Kunstform darzustellen
    print("""📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📈📉📈📉📈📉📈📉
☁️  ☁️  ☁️  ☁️  ☁️  ☁️  ☁️  ☁️  ☁️  ☁️  ☁️  ☁️  ☁️  ☁️  ☁️  ☁️  ☀️


             💭        💭        💭
              💭  💭    💭  💭    💭  💭
              ||   💭   ||   💭   ||   💭
             _||___||___||___||___||___||_
       _____|   o    o    o   o      🎛️🪟|________
      || ⚓\\_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-/
     ###    \\o»»»o»»»»o»»»»o»»»»o»»»»o»»»»o»»»o/   🌊    🌊
~~~~#####~~~~\\________________________________/~~~~~~~~~~~~~~~~
~~~####🐟#~~🐟~~~~🐟~~~~~~🐟~~🐟~~~~🐠~~~~🐟~~~~~~~~~~~~~~~~~🐠~
~~~##🐠##🐟~~~~~~~~~🐟🐟~~~~🐠~~~~🐟~~~~🐟~~~~🦑~~~~🐟~~~~🐟~~~~~
~~~~###🦑~~~~~🐳~~~~🐟~~~~🦑~~~~~~~~~~~~~~🐟~~~~~🐳~~~~🐠~~~~🐟~~~
📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📈📉📈📉📈📉📈📉
         """)

    print(colored("\n♠️♦️Choose your symbols♣️♥️", 'black', 'on_white'))

    # Erstelle eine Liste der Namen
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
            selected_symbols = symbols  # Verwende alle Symbole
            selected_symbols_display = "🃏ALL🃏"
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

    if not selected_symbols:
        selected_symbols = symbols  # Verwende alle Symbole, wenn keine ausgewählt wurden

    # Create the formatted symbol list
    selected_symbols_formatted = [name_map.get(symbol.upper().replace('USDT', ''), symbol.upper().replace('USDT', '')) for symbol in selected_symbols]

    # Bestimmen der Symbole, die auf den jeweiligen Börsen verfügbar sind
    global okx_symbols_selected, bybit_symbols_selected, bitmex_symbols_selected, deribit_symbols_selected

    # OKX Symbole vorbereiten
    okx_symbols_selected = [symbol.upper().replace('USDT', '-USDT') for symbol in selected_symbols]
    okx_symbol_map = {symbol.upper().replace('USDT', '-USDT'): symbol for symbol in selected_symbols}

    # Bybit Symbole vorbereiten
    bybit_symbols_selected = [symbol.upper() for symbol in selected_symbols]
    bybit_symbol_map = {symbol.upper(): symbol for symbol in selected_symbols}

    # BitMEX Symbole vorbereiten
    bitmex_symbols_selected = [symbol.upper().replace('USDT', 'USD') for symbol in selected_symbols]
    bitmex_symbol_map = {symbol.upper().replace('USDT', 'USD'): symbol for symbol in selected_symbols}

    # Deribit Symbole vorbereiten
    deribit_symbols_selected = [symbol.upper().replace('USDT', '-PERPETUAL') for symbol in selected_symbols]
    deribit_symbol_map = {symbol.upper().replace('USDT', '-PERPETUAL'): symbol for symbol in selected_symbols}


async def main():
    # Symbol selection and initialization
    select_symbols()
    select_thresholds()

    # Get the time window from the user
    time_window_seconds = get_time_window()

    # Capture the start time
    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    start_timestamp = datetime.now().timestamp() * 1000

    if selected_symbols == symbols:
        selected_symbols_display = "🃏ALL🃏"
    else:
        selected_symbols_display = ", ".join(selected_symbols_formatted)

    # Create an instance of ThresholdConsoleManager
    threshold_console_manager = ThresholdConsoleManager(
        num_columns=num_columns,
        num_rows=num_rows,
        start_time=start_time,
        start_timestamp=start_timestamp,
        time_window_seconds=time_window_seconds,
        selected_symbols_display=selected_symbols_display
    )


    # Start WebSocket tasks for liquidations
    asyncio.create_task(binance_liquidation_stream(websocket_url_liq_binance, threshold_console_manager))
    asyncio.create_task(okx_liquidation_stream(websocket_url_liq_okx, threshold_console_manager))
    asyncio.create_task(bitmex_liquidation_stream(websocket_url_liq_bitmex, threshold_console_manager))
    asyncio.create_task(bybit_liquidation_stream(websocket_url_liq_bybit, threshold_console_manager))
    asyncio.create_task(deribit_liquidation_stream(websocket_url_liq_deribit, threshold_console_manager))

    # Start periodic data saving
    directory = "/path/to/liquidation_data/"
    asyncio.create_task(save_data_periodically(directory))

    # Start cleaning up old liquidations
    asyncio.create_task(cleanup_old_liquidations(time_window_seconds))

    # Start live display
    await threshold_console_manager.live_display()


if __name__ == "__main__":
    try:
        print("⚙️ Program is starting ⚙️")
        asyncio.run(main())  # Main entry point for running the program
        print("✅⚙️ Program is done ⚙✅️")
    except Exception as e:
        console.print(f"[red]An error occurred in the main program: {e}[/red]")
        import traceback
        traceback.print_exc()
