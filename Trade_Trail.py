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

websocket_url_base_binance = 'wss://fstream.binance.com/ws/'
websocket_url_base_coinbase = 'wss://ws-feed.exchange.coinbase.com'
websocket_url_kraken = 'wss://ws.kraken.com/'
websocket_url_bitfinex = 'wss://api-pub.bitfinex.com/ws/2'
websocket_url_okx = 'wss://ws.okx.com:8443/ws/v5/public'
websocket_url_coincap = 'wss://ws.coincap.io/trades'
output_directory = "/home/jestersly/Schreibtisch/Codes/_Algo_Trade_Edge/Data_Streams/Liqs_and_Trades_Archive/" #Change this
print("📡 Configuration loaded")

# Ensure the output directory exists
os.makedirs(output_directory, exist_ok=True)

# Placeholder for user-selected symbols
selected_symbols = []
selected_symbols_formatted = []
kraken_symbols_selected = []
bitfinex_symbols_selected = []
okx_symbols_selected = []
coincap_symbols_selected = []

cumulative_sum_map = {}
trade_count_map = {}
connection_closed_logged = set()

# Data Collection Lists
trades_data = []

# Column names for the Excel export
trades_columns = ['symbol', 'used_trade_time', 'trade_type', 'usd_size']

# Thresholds for printing output
trade_threshold = 0

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
    # New symbols added
    'suiusdt', 'seiusdt', 'leousdt', 'taobusdt', 'fetusdt', 'pepeusdt',
    'hbarusdt', 'arusdt', 'kasusdt', 'imxusdt', 'injusdt', 'hexusdt',
    'ftmusdt', 'mntusdt', 'bgbusdt', 'hntusdt', 'qntusdt', 'mogusdt',
    'xecusdt', 'opusdt', 'crousdt', 'runeusdt', 'turbousdt', 'bttusdt',
    'fttusdt', 'pendleusdt', '1inchusdt', 'astrusdt', 'twtusdt', 'oceanusdt',
    'blurusdt', 'nexousdt', 'glmusdt', 'galausdt', 'axlusdt', 'superusdt',
    'mplxusdt', 'rayusdt', 'omusdt', 'flokiusdt', 'mantausdt', 'eigenusdt', 'wldusdt', 'achusdt'
]

# Initialize Variables
name_map = {
    'BTC': '🟡BTC    ', 'ETH': '💠ETH    ', 'SOL': '👾SOL    ', 'BNB': '🔶BNB    ', 'DOGE': '🐶DOGE   ',
    'USDC': '💵USDC   ', 'XRP': '⚫XRP    ', 'ADA': '🔵ADA    ', 'MATIC': '🟣MATIC  ',
    'TON': '🎮TON    ', 'LINK': '🔗LINK   ', 'TRX': '⚙️TRX    ', 'NEAR': '🔍NEAR   ', 'XLM': '🌟XLM    ',
    'RNDR': '🎨RNDR   ', 'DOT': '⚪DOT    ', 'UNI': '🦄UNI    ', 'ATOM': '⚛️ATOM   ', 'XMR': '👽XMR    ',
    'LDO': '🧪LDO    ', 'GMX': '🌀GMX    ', 'LTC': '🌕LTC    ', 'AVAX': '🏔️AVAX   ', 'BCH': '💰BCH    ',
    'VET': '♻️VET    ', 'FIL': '📁FIL    ', 'ETC': '⛏️ETC    ', 'ALGO': '🔺ALGO   ', 'XTZ': '🏺XTZ    ',
    'EOS': '🌐EOS    ', 'AAVE': '🏦AAVE   ', 'MKR': '🏭MKR    ', 'THETA': '📺THET   ', 'AXS': '🕹️AXS    ',
    'SAND': '🏖️SAND   ', 'ICP': '🌐ICP    ', 'SHIB': '🐾SHIBA  ', 'APT': '🚀APT    ', 'GRT': '📊GRT    ',
    'ENJ': '🎮ENJ    ', 'CHZ': '⚽CHZ    ', 'MANA': '🌐MANA   ', 'SUSHI': '🍣SUSHI  ', 'BAT': '🦇BAT    ',
    'ZEC': '💰ZEC    ', 'DASH': '⚡DASH   ', 'NEO': '💹NEO    ', 'IOTA': '🔗IOTA   ', 'OMG': '😮OMG    ',
    'CAKE': '🍰CAKE   ', 'STX': '📚STX    ', 'SNX': '💎SNX    ', 'COMP': '🏦COMP   ', 'ZIL': '💠ZIL    ',
    'KSM': '🪶KSM    ', 'REN': '🔄REN    ',
    'SUI': '🌊SUI    ', 'SEI': '🏝️SEI    ', 'LEO': '🦁LEO    ', 'TAO': '☯️TAO    ', 'FET': '🤖FET    ',
    'PEPE': '🐸PEPE   ', 'HBAR': '🌐HBAR   ', 'AR': '🕸️AR     ', 'KAS': '🔷KAS    ', 'IMX': '🖼️IMX    ',
    'INJ': '💉INJ    ', 'HEX': '🔷HEX    ', 'FTM': '👻FTM    ', 'MNT': '🛡️MNT    ', 'BGB': '💎BGB    ',
    'HNT': '📡HNT    ', 'QNT': '🔢QNT    ', 'MOG': '🐶MOG    ', 'XEC': '💱XEC    ', 'OP': '⚙️OP     ',
    'CRO': '🐾CRO    ', 'RUNE': '🪄RUNE   ', 'TURBO': '🚀TURB   ', 'BTT': '🔺BTT    ', 'FTT': '🪙FTT    ',
    'PENDLE': '🎛️PENDLE ', '1INCH': '🐎1INCH  ', 'ASTR': '🌌ASTRA  ', 'TWT': '🔑TWT    ', 'OCEAN': '🌊OCEAN  ',
    'BLUR': '💨BLUR   ', 'NEXO': '🏦NEXO   ', 'GLM': '⚡GLM    ', 'GALA': '🎉GALA   ', 'AXL': '🔗AXL    ',
    'SUPER': '🦸SUPER  ', 'MPLX': '🛰️MPLX   ', 'RAY': '☀️RAY    ', 'OM': '🕉️OM     ', 'FLOKI': '🐶FLOKI  ',
    'MANTA': '🦈MANTA  ', 'EIGEN': '🪞EIGEN  ', 'WLD': '🌎WLD    ', 'ACH': '🧪ACH    '
}

kraken_symbol_map = {
    'btcusdt': 'XBT/USDT',
    'ethusdt': 'ETH/USDT',
    'solusdt': 'SOL/USDT',
    'bnbusdt': None,  # BNB not available on Kraken
    'dogeusdt': 'DOGE/USDT',
    'usdcusdt': 'USDC/USDT',
    'xrpusdt': 'XRP/USDT',
    'adausdt': 'ADA/USDT',
    'maticusdt': 'MATIC/USDT',
    'tonusdt': None,  # TON not available on Kraken
    'linkusdt': 'LINK/USDT',
    'trxusdt': 'TRX/USDT',
    'nearusdt': 'NEAR/USDT',
    'xlmusdt': 'XLM/USDT',
    'renderusdt': 'RENDER/USDT',  # RNDR not available on Kraken
    'dotusdt': 'DOT/USDT',
    'uniusdt': 'UNI/USDT',
    'atomusdt': 'ATOM/USDT',
    'xmrusdt': 'XMR/USDT',
    'ldousdt': 'LDO/USDT',  # LDO not available on Kraken
    'gmxusdt': 'GMX/USDT',  # GMX not available on Kraken
    'ltcusdt': 'LTC/USDT',
    'avaxusdt': 'AVAX/USDT',
    'bchusdt': 'BCH/USDT',
    'vetusdt': 'VET/USDT',
    'filusdt': 'FIL/USDT',
    'etcusdt': 'ETC/USDT',
    'algousdt': 'ALGO/USDT',
    'xtzusdt': 'XTZ/USDT',
    'eosusdt': 'EOS/USDT',
    'aaveusdt': 'AAVE/USDT',
    'mkrusdt': 'MKR/USDT',
    'thetausdt': 'THETA/USDT',
    'axsusdt': 'AXS/USDT',
    'sandusdt': 'SAND/USDT',
    'icpusdt': 'ICP/USDT',
    'shibusdt': 'SHIB/USDT',
    'aptusdt': 'APT/USDT',
    'grtusdt': 'GRT/USDT',
    'enjusdt': 'ENJ/USDT',
    'chzusdt': 'CHZ/USDT',
    'manausdt': 'MANA/USDT',
    'sushiusdt': 'SUSHI/USDT',
    'batusdt': 'BAT/USDT',
    'zecusdt': 'ZEC/USDT',
    'dashusdt': 'DASH/USDT',
    'neousdt': 'NEO/USDT',
    'iotausdt': 'IOTA/USDT',
    'omgusdt': 'OMG/USDT',
    'cakeusdt': None,  # CAKE not available on Kraken
    'stxusdt': 'STX/USDT',
    'snxusdt': 'SNX/USDT',
    'compusdt': 'COMP/USDT',
    'zilusdt': 'ZIL/USDT',
    'ksmusdt': 'KSM/USDT',
    'renusdt': 'REN/USDT',
    # New symbols added
    'suiusdt': 'SUI/USD',
    'seiusdt': 'SEI/USD',
    'leousdt': None,    # LEO not available on Kraken
    'taobusdt': 'TAO/USDT',   # TAO not available on Kraken
    'fetusdt': 'FET/USDT',
    'pepeusdt': 'PEPE/USDT',   # PEPE not available on Kraken
    'hbarusdt': 'HBAR/USDT',
    'arusdt': 'AR/USDT',
    'kasusdt': None,    # KAS not available on Kraken
    'imxusdt': 'IMX/USDT',
    'injusdt': 'INJ/USDT',
    'hexusdt': None,    # HEX not available on Kraken
    'ftmusdt': 'FTM/USDT',
    'mntusdt': 'MNT/USDT',    # MNT not available on Kraken
    'bgbusdt': None,    # BGB not available on Kraken
    'hntusdt': 'HNT/USDT',
    'qntusdt': 'QNT/USDT',
    'mogusdt': 'MOG/USDT',    # MOG not available on Kraken
    'xecusdt': None,    # XEC not available on Kraken
    'opusdt': 'OP/USDT',
    'crousdt': None,    # CRO not available on Kraken
    'runeusdt': 'RUNE/USDT',
    'turbousdt': 'TURBO/USDT',  # TURBO not available on Kraken
    'bttusdt': None,    # BTT not available on Kraken
    'fttusdt': 'FTT/USDT',
    'pendleusdt': None, # PENDLE not available on Kraken
    '1inchusdt': '1INCH/USDT',
    'astrusdt': None,   # ASTR not available on Kraken
    'twtusdt': None,    # TWT not available on Kraken
    'oceanusdt': 'OCEAN/USDT',
    'blurusdt': 'BLUR/USDT',   # BLUR not available on Kraken
    'nexousdt': 'NEXO/USDT',
    'glmusdt': 'GLM/USDT',
    'galausdt': 'GALA/USDT',
    'axlusdt': 'WAXL/USDT',    # AXL not available on Kraken
    'superusdt': 'SUPER/USDT',  # SUPER not available on Kraken
    'mplxusdt': None,   # MPLX not available on Kraken
    'rayusdt': 'RAY/USDT',    # RAY not available on Kraken
    'omusdt': 'OM/USDT',
    'flokiusdt': 'FLOKI/USDT',   # FLOKI not available on Kraken
    'mantausdt': 'MANTA/USDT',
    'eigenusdt': 'EIGEN/USDT',
    'wldusdt': 'WLD/USDT',
    'achusdt': 'ACH/USDT'
}

bitfinex_symbol_map = {
    'btcusdt': 'tBTCUSD',
    'ethusdt': 'tETHUSD',
    'solusdt': 'tSOLUSD',
    'bnbusdt': None,  # BNB not available on Bitfinex
    'dogeusdt': 'tDOGEUSD',
    'usdcusdt': 'tUDCUSD',  # Bitfinex uses 'UDC' for USDC
    'xrpusdt': 'tXRPUSD',
    'adausdt': 'tADAUSD',
    'maticusdt': 'tMATICUSD',
    'tonusdt': 'tTONUSD',  # TON is available
    'linkusdt': 'tLINKUSD',
    'trxusdt': 'tTRXUSD',
    'nearusdt': 'tNEARUSD',
    'xlmusdt': 'tXLMUSD',
    'renderusdt': 'RENDER',  # RNDR not available on Bitfinex
    'dotusdt': 'tDOTUSD',
    'uniusdt': 'tUNIUSD',
    'atomusdt': 'tATOMUSD',
    'xmrusdt': 'tXMRUSD',
    'ldousdt': 'tLDOUSD',  # LDO not available on Bitfinex
    'gmxusdt': None,  # GMX not available on Bitfinex
    'ltcusdt': 'tLTCUSD',
    'avaxusdt': 'tAVAXUSD',
    'bchusdt': 'tBCHUSD',
    'vetusdt': 'tVETUSD',
    'filusdt': 'tFILUSD',
    'etcusdt': 'tETCUSD',
    'algousdt': 'tALGOUSD',
    'xtzusdt': 'tXTZUSD',
    'eosusdt': 'tEOSUSD',
    'aaveusdt': 'tAAVEUSD',
    'mkrusdt': 'tMKRUSD',
    'thetausdt': 'tTHETAUSD',
    'axsusdt': 'tAXSUSD',
    'sandusdt': 'tSANDUSD',
    'icpusdt': 'tICPUSD',
    'shibusdt': 'tSHIBUSD',
    'aptusdt': 'tAPTUSD',
    'grtusdt': 'tGRTUSD',
    'enjusdt': 'tENJUSD',
    'chzusdt': 'tCHZUSD',
    'manausdt': 'tMANAUSD',
    'sushiusdt': 'tSUSHIUSD',
    'batusdt': 'tBATUSD',
    'zecusdt': 'tZECUSD',
    'dashusdt': 'tDSHUSD',  # Bitfinex uses 'DSH' for DASH
    'neousdt': 'tNEOUSD',
    'iotausdt': 'tIOTAUSD',
    'omgusdt': 'tOMGUSD',
    'cakeusdt': None,  # CAKE not available on Bitfinex
    'stxusdt': 'tSTXUSD',
    'snxusdt': 'tSNXUSD',
    'compusdt': 'tCOMPUSD',
    'zilusdt': 'tZILUSD',
    'ksmusdt': 'tKSMUSD',
    'renusdt': 'tRENUSD',
    # New symbols added
    'suiusdt': 'tSUIUSD',
    'seiusdt': 'tSEIUSD',    # SEI not available on Bitfinex
    'leousdt': 'tLEOUSD',
    'taobusdt': None,   # TAO not available on Bitfinex
    'fetusdt': 'tFETUSD',
    'pepeusdt': 'tPEPE:USD',
    'hbarusdt': 'tHBARUSD',
    'arusdt': 'tARUSD',
    'kasusdt': None,    # KAS not available on Bitfinex
    'imxusdt': 'tIMXUSD',
    'injusdt': 'tINJUSD',    # INJ not available on Bitfinex
    'hexusdt': None,    # HEX not available on Bitfinex
    'ftmusdt': 'tFTMUSD',
    'mntusdt': None,    # MNT not available on Bitfinex
    'bgbusdt': 'tBGBUSD',    # BGB not available on Bitfinex
    'hntusdt': 'tHNTUSD',
    'qntusdt': 'tQNTUSD',
    'mogusdt': None,    # MOG not available on Bitfinex
    'xecusdt': None,    # XEC not available on Bitfinex
    'opusdt': 'tOPUSD',
    'crousdt': None,    # CRO not available on Bitfinex
    'runeusdt': 'tRUNEUSD',
    'turbousdt': 'tTURBOUSD',  # TURBO not available on Bitfinex
    'bttusdt': 'tBTTUSD',    # BTT not available on Bitfinex
    'fttusdt': 'tFTTUSD',
    'pendleusdt': None, # PENDLE not available on Bitfinex
    '1inchusdt': 't1INCH:USD',
    'astrusdt': None,   # ASTR not available on Bitfinex
    'twtusdt': None,    # TWT not available on Bitfinex
    'oceanusdt': 'tOCEANUSD',
    'blurusdt': 'tBLURUSD',
    'nexousdt': 'tNEXOUSD',
    'glmusdt': 'tGLMUSD',
    'galausdt': 'tGALAUSD',
    'axlusdt': None,    # AXL not available on Bitfinex
    'superusdt': None,  # SUPER not available on Bitfinex
    'mplxusdt': None,   # MPLX not available on Bitfinex
    'rayusdt': None,    # RAY not available on Bitfinex
    'omusdt': None,     # OM not available on Bitfinex
    'flokiusdt': 'tFLOKIUSD',   # FLOKI not available on Bitfinex
    'mantausdt': 'tMANTAUSD',
    'eigenusdt': 'tEIGENUSD',
    'wldusdt': 'tWLDUSD',
    'achusdt': 'tACHUSD'
}

# Symbol mappings for OKX and CoinCap
# Updated Symbol mappings for OKX
okx_symbol_map = {
    'BTC-USDT': 'btcusdt',
    'ETH-USDT': 'ethusdt',
    'SOL-USDT': 'solusdt',
    'BNB-USDT': 'bnbusdt',    # BNB not available on Bitfinex
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
    'RENDER-USDT': 'renderusdt',    
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
    'CAKE-USDT': 'cakeusdt',    # CAKE not available on Bitfinex
    'STX-USDT': 'stxusdt',
    'SNX-USDT': 'snxusdt',
    'COMP-USDT': 'compusdt',
    'ZIL-USDT': 'zilusdt',
    'KSM-USDT': 'ksmusdt',
    'REN-USDT': 'renusdt',
    # Newly added symbols
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

# Updated Symbol mappings for CoinCap
coincap_symbol_map = {
    'BTC': 'btcusdt',
    'ETH': 'ethusdt',
    'SOL': 'solusdt',
    'BNB': 'bnbusdt',    # BNB not available on Bitfinex
    'DOGE': 'dogeusdt',
    'USDC': 'usdcusdt',
    'XRP': 'xrpusdt',
    'ADA': 'adausdt',
    'MATIC': 'maticusdt',
    'TON': 'tonusdt',
    'LINK': 'linkusdt',
    'TRX': 'trxusdt',
    'NEAR': 'nearusdt',
    'XLM': 'xlmusdt',
    'RENDER': 'renderusdt',    # RNDR not available on Bitfinex
    'DOT': 'dotusdt',
    'UNI': 'uniusdt',
    'ATOM': 'atomusdt',
    'XMR': 'xmrusdt',
    'LDO': 'ldousdt',    # LDO not available on Bitfinex
    'GMX': 'gmxusdt',    # GMX not available on Bitfinex
    'LTC': 'ltcusdt',
    'AVAX': 'avaxusdt',
    'BCH': 'bchusdt',
    'VET': 'vetusdt',
    'FIL': 'filusdt',
    'ETC': 'etcusdt',
    'ALGO': 'algousdt',
    'XTZ': 'xtzusdt',
    'EOS': 'eosusdt',
    'AAVE': 'aaveusdt',
    'MKR': 'mkrusdt',
    'THETA': 'thetausdt',
    'AXS': 'axsusdt',
    'SAND': 'sandusdt',
    'ICP': 'icpusdt',
    'SHIB': 'shibusdt',
    'APT': 'aptusdt',
    'GRT': 'grtusdt',
    'ENJ': 'enjusdt',
    'CHZ': 'chzusdt',
    'MANA': 'manausdt',
    'SUSHI': 'sushiusdt',
    'BAT': 'batusdt',
    'ZEC': 'zecusdt',
    'DASH': 'dashusdt',
    'NEO': 'neousdt',
    'IOTA': 'iotausdt',
    'OMG': 'omgusdt',
    'CAKE': 'cakeusdt',    # CAKE not available on Bitfinex
    'STX': 'stxusdt',
    'SNX': 'snxusdt',
    'COMP': 'compusdt',
    'ZIL': 'zilusdt',
    'KSM': 'ksmusdt',
    'REN': 'renusdt',
    'SUI': 'suiusdt',
    'SEI': 'seiusdt',
    'LEO': 'leousdt',
    'TAO': 'taobusdt',
    'FET': 'fetusdt',
    'PEPE': 'pepeusdt',
    'HBAR': 'hbarusdt',
    'AR': 'arusdt',
    'KAS': 'kasusdt',
    'IMX': 'imxusdt',
    'INJ': 'injusdt',
    'HEX': 'hexusdt',
    'FTM': 'ftmusdt',
    'MNT': 'mntusdt',
    'BGB': 'bgbusdt',
    'HNT': 'hntusdt',
    'QNT': 'qntusdt',
    'MOG': 'mogusdt',
    'XEC': 'xecusdt',
    'OP': 'opusdt',
    'CRO': 'crousdt',
    'RUNE': 'runeusdt',
    'TURBO': 'turbousdt',
    'BTT': 'bttusdt',
    'FTT': 'fttusdt',
    'PENDLE': 'pendleusdt',
    '1INCH': '1inchusdt',
    'ASTR': 'astrusdt',
    'TWT': 'twtusdt',
    'OCEAN': 'oceanusdt',
    'BLUR': 'blurusdt',
    'NEXO': 'nexousdt',
    'GLM': 'glmusdt',
    'GALA': 'galausdt',
    'AXL': 'axlusdt',
    'SUPER': 'superusdt',
    'MPLX': 'mplxusdt',
    'RAY': 'rayusdt',
    'OM': 'omusdt',
    'FLOKI': 'flokiusdt',
    'MANTA': 'mantausdt',
    'EIGEN': 'eigenusdt',
    'WLD': 'wldusdt',
    'ACH': 'achusdt'
}


def initialize_maps():
    """
    Initializes cumulative sum maps for selected symbols.
    """
    global cumulative_sum_map
    cumulative_sum_map = {symbol.upper().replace('USDT', ''): 0 for symbol in selected_symbols}

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
    The cumulative sum is added or subtracted based on 'trade_type'.
    If 'trade_type' is '📈 ', the value is added; if '📉 ', it is subtracted.
    """
    cumulative_sum = 0
    cumulative_sums = []

    for index, row in df.iterrows():
        if 'trade_type' in df.columns and row['trade_type'] == '📈 ':
            cumulative_sum += row['usd_size']
        elif 'trade_type' in df.columns and row['trade_type'] == '📉 ':
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


async def periodic_export(interval, trade_threshold, start_time):
    """
    Periodically exports the collected trade data to Excel files.
    """
    # Initialize cumulative values and counts
    total_intervals = 0
    total_trades_above_threshold = 0
    total_usd_size = 0

    while True:
        try:
            await asyncio.sleep(interval)
            total_intervals += 1
            # Stars counting dictionaries for trades
            stars_count_trades = {}

            # Count trades above threshold
            trades_above_threshold = sum(1 for trade in trades_data if trade[3] >= trade_threshold)

            # Calculate total usd_size considering trade types
            usd_size_sum = sum(trade[3] if trade[2] == '📈 ' else -trade[3] for trade in trades_data)

            # Update cumulative values
            total_trades_above_threshold += trades_above_threshold
            total_usd_size += usd_size_sum

            # Iterate over trades to count stars occurrences and accumulate usd_size
            for trade in trades_data:
                usd_size = trade[3]
                stars = get_stars(usd_size)
                trade_type = trade[2]
                if stars not in stars_count_trades:
                    stars_count_trades[stars] = {'📈 ': {'count': 0, 'total_usd_size': 0}, '📉 ': {'count': 0, 'total_usd_size': 0}}
                stars_count_trades[stars][trade_type]['count'] += 1
                stars_count_trades[stars][trade_type]['total_usd_size'] += usd_size


            # Calculate averages
            avg_trades_per_minute = total_trades_above_threshold / total_intervals if total_intervals > 0 else 0
            avg_usd_size_per_minute = total_usd_size / total_intervals if total_intervals > 0 else 0

            # Determine the color of the average usd_size
            usd_size_color = 'green' if avg_usd_size_per_minute > 0 else 'red'

            # Calculate counts for trades
            trades_count = len(trades_data)
            trades_long_count = sum(1 for trade in trades_data if trade[2] == '📈 ')
            trades_short_count = sum(1 for trade in trades_data if trade[2] == '📉 ')

            # Calculate total usd_size for trades
            total_usd_size_long = sum(trade[3] for trade in trades_data if trade[2] == '📈 ')
            total_usd_size_short = sum(trade[3] for trade in trades_data if trade[2] == '📉 ')

            # Calculate the difference between long and short
            usd_size_difference = total_usd_size_long - total_usd_size_short

            # Determine the color based on the difference
            difference_color = 'green' if usd_size_difference > 0 else 'red'

            # Print the summary including the total usd_size and the difference
            print(f"\n--------------------------------------------------------------------")
            print(f"📅 Start Time: {start_time}")
            print(f"🕰️ Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"⏳{calculate_time_difference(start_time, datetime.now().strftime('%H:%M:%S'))} since start⏳")
            print(f"🔍 Selected Symbols: {', '.join(selected_symbols)}")
            print("--------------------------------------------------------------------")
            print(f"🎣 A total of {trades_count} Trades above {trade_threshold}$")
            print(colored(f"📈Total Count: {trades_long_count}  | 📈Total Size: {total_usd_size_long:,.2f}$", 'white', 'on_green'))
            print(colored(f"📉Total Count: {trades_short_count} | 📉Total Size: {total_usd_size_short:,.2f}$", 'white', 'on_red'))
            print("🔍 Trade Sizes:")
            # Sort and display trades with 📈 first and 📉 second
            for trade_type in ['📈 ', '📉 ']:
                for stars, data in stars_count_trades.items():
                    if data[trade_type]['count'] > 0:
                        usd_size_color = 'green' if trade_type == '📈 ' else 'red'
                        print(f"  {stars}: {trade_type}{data[trade_type]['count']} Trades | Total USD Size: {colored(f'{data[trade_type]['total_usd_size']:,.2f}$', usd_size_color)}")
            print(colored(f"Difference: {usd_size_difference:,.2f}$", difference_color, attrs=['bold']))
            print(colored(f"📊 Avg. Trades per interval: {avg_trades_per_minute:.2f}", 'black', 'on_white'))
            print(colored(f"📊 Avg. USD Size per interval: {avg_usd_size_per_minute:.2f}$", usd_size_color, 'on_white', attrs=['bold']))

            # Generate filenames that include the threshold values
            trades_filename = f"Trades_threshold_{trade_threshold}.xlsx"

            # Export to Excel with the generated filenames
            export_to_excel(trades_data, trades_columns, trades_filename, output_directory)
        except Exception as e:
            print(f"Error during export: {e}")






def collect_trade_data(symbol, used_trade_time, trade_type, usd_size):
    """
    Collects trade data and appends it to the trades_data list.
    """
    trades_data.append([symbol, used_trade_time, trade_type, usd_size])


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


def get_stars(usd_size):
    if usd_size >= 210935000:
        return '⁉️💰🃏💰⁉️'
    elif usd_size >= 130365000:
        return '  🐳🐳🐳  '
    elif usd_size >= 80570000:
        return '   🐳🐳   '
    elif usd_size >= 49795000:
        return '    🐳    '
    elif usd_size >= 30775000:
        return '  🦈🦈🦈  '
    elif usd_size >= 19020000:
        return '   🦈🦈   '
    elif usd_size >= 11755000:
        return '    🦈    '
    elif usd_size >= 7265000:
        return '  🦑🦑🦑  '
    elif usd_size >= 4490000:
        return '   🦑🦑   '
    elif usd_size >= 2775000:
        return '    🦑    '
    elif usd_size >= 1715000:
        return '  🐡🐡🐡  '
    elif usd_size >= 1060000:
        return '   🐡🐡   '
    elif usd_size >= 655000:
        return '    🐡    '
    elif usd_size >= 405000:
        return '🐠🐠🐠🐠🐠'
    elif usd_size >= 250000:
        return ' 🐠🐠🐠🐠 '
    elif usd_size >= 155000:
        return '  🐠🐠🐠  '
    elif usd_size >= 95000:
        return '   🐠🐠   '
    elif usd_size >= 60000:
        return '    🐠    '
    elif usd_size >= 35000:
        return '🐟🐟🐟🐟🐟'
    elif usd_size >= 25000:
        return ' 🐟🐟🐟🐟 '
    elif usd_size >= 15000:
        return '  🐟🐟🐟  '
    elif usd_size >= 10000:
        return '   🐟🐟   '
    elif usd_size >= 5000:
        return '    🐟    '
    else:
        return '          '

def get_attrs_trades(usd_size):
    if usd_size >= 5000000:
        return ['bold', 'blink']
    elif usd_size >= 1000000:
        return ['bold']
    else:
        return []

    
def update_cumulative_sum(symbol, usd_size, trade_type):
    if symbol not in cumulative_sum_map:
        cumulative_sum_map[symbol] = 0
    if trade_type == '📉 ':
        cumulative_sum_map[symbol] -= usd_size
    else:
        cumulative_sum_map[symbol] += usd_size
    return cumulative_sum_map[symbol]


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


async def process_trade(symbol, price, quantity, trade_time, is_buyer_maker):
    global trade_threshold
    usd_size = price * quantity

    # Extract the base symbol
    SYMBL = symbol.upper().lstrip('T').replace('USDT', '').replace('USD', '').replace('PERP', '')

    max_price = 1000000000

    # Skip symbol filtering if 'ALL' is selected (indicated by selected_symbols being None)
    if selected_symbols is None or usd_size >= trade_threshold:
        trade_type = '📉 ' if is_buyer_maker else '📈 '
        stars = get_stars(usd_size)
        attrs = get_attrs_trades(usd_size)
        used_trade_time = format_trade_time(trade_time)

        # Collect data
        collect_trade_data(SYMBL, used_trade_time, trade_type, usd_size)

        cumulative_sum = update_cumulative_sum(SYMBL, usd_size, trade_type)
        cumulative_sum_str = format_cumulative_sum(cumulative_sum)
        usd_size_str = format_usd_size(usd_size, trade_type)
        stars_padding = get_stars_padding(usd_size, max_price)

        # Use get() with a fallback if SYMBL is not in name_map
        output = f"{name_map.get(SYMBL, SYMBL.ljust(9))}{'|'}{stars}{'|'}{used_trade_time}{'|'}{trade_type}{usd_size_str}{stars_padding}{'|'} 💵🟰 {cumulative_sum_str}"

        if usd_size > 20000000:
            output = add_color_border(output, 'green')
        elif usd_size < -20000000:
            output = add_color_border(output, 'red')

        cprint(output, 'white', attrs=attrs)
        update_trade_count(SYMBL, stars, trade_type)




# Binance Trade Stream
async def binance_trade_stream(uri, symbol):
    while True:
        try:
            async with connect(uri, max_size=None) as websocket:  # Increase the buffer size
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    event_time = int(data['E'])
                    price = float(data['p'])
                    quantity = float(data['q'])
                    trade_time = int(data['T'])
                    is_buyer_maker = data['m']
                    await process_trade(symbol, price, quantity, trade_time, is_buyer_maker)
        except ConnectionClosed as e:
            if symbol not in connection_closed_logged:
                print(f"📡 ❗🛰️ Connection closed for {symbol}: {e}.  5 Seconds 🔃")
                connection_closed_logged.add(symbol)
            await asyncio.sleep(5)
        except Exception as e:
            print(f"❗Error❗: {e}.  5 Seconds 🔃")
            await asyncio.sleep(5)

# Coinbase Trade Stream
async def coinbase_trade_stream(uri):
    # Extract symbols from the global selected_symbols list and format them to match Coinbase's product IDs (e.g., BTC-USD)
    coinbase_symbols = [symbol.split('usdt')[0].upper() + '-USD' for symbol in selected_symbols if symbol.endswith('usdt')]
    
    # Check if there are any valid symbols for Coinbase subscription
    if not coinbase_symbols:
        print("No valid symbols selected for Coinbase stream.")
        return

    while True:
        try:
            print(f"📶  Coinbase Trades » {uri}")
            async with connect(uri, max_size=None) as websocket:
                # Dynamically set the channels based on the selected symbols
                subscribe_message = {
                    "type": "subscribe",
                    "channels": [{"name": "ticker", "product_ids": coinbase_symbols}]
                }
                await websocket.send(json.dumps(subscribe_message))

                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    if data['type'] == 'ticker':
                        product_id = data['product_id']
                        symbol = product_id.split('-')[0]
                        # Fallback to use the symbol directly if unknown
                        symbol = symbol if symbol else 'UNKNOWN'
                        price = float(data['price'])
                        quantity = float(data['last_size'])
                        trade_time = int(datetime.fromisoformat(data['time'].replace('Z', '+00:00')).timestamp() * 1000)
                        is_buyer_maker = data['side'] == 'sell'
                        await process_trade(symbol, price, quantity, trade_time, is_buyer_maker)
        except ConnectionClosed as e:
            print(f"📡 ❗ 🛰️: {e}.  5 Seconds 🔃")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"❗Error❗: {e}.  5 Seconds 🔃")
            await asyncio.sleep(5)


# Kraken Trade Stream
async def kraken_trade_stream(uri):
    if not kraken_symbols_selected:
        return
    while True:
        try:
            async with connect(uri, max_size=None) as websocket:
                subscribe_message = {
                    "event": "subscribe",
                    "pair": kraken_symbols_selected,
                    "subscription": {"name": "trade"}
                }
                await websocket.send(json.dumps(subscribe_message))
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    if isinstance(data, list) and data[-1] == 'trade':
                        trades = data[1]
                        pair = data[3]
                        symbol = pair.split('/')[0]
                        if symbol == 'XBT':
                            symbol = 'BTC'
                        # Fallback to handle unknown symbols
                        symbol = symbol if symbol else 'UNKNOWN'
                        for trade in trades:
                            price = float(trade[0])
                            quantity = float(trade[1])
                            trade_time = int(float(trade[2]) * 1000)
                            side = trade[3]  # 'b' or 's'
                            is_buyer_maker = True if side == 's' else False
                            await process_trade(symbol, price, quantity, trade_time, is_buyer_maker)
        except ConnectionClosed:
            print("No Connection📡❌🛰️ (Kraken)")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"[red]An error occurred in kraken_trade_stream: {e}[/red]")
            await asyncio.sleep(5)


async def bitfinex_trade_stream(uri):
    chan_id_symbol_map = {}

    while True:
        try:
            async with connect(uri, max_size=None) as websocket:
                # Subscribe to trades for each symbol
                symbols_to_subscribe = bitfinex_symbols_selected if bitfinex_symbols_selected else ['tBTCUSD', 'tETHUSD']
                for symbol in symbols_to_subscribe:
                    subscribe_message = {
                        "event": "subscribe",
                        "channel": "trades",
                        "symbol": symbol
                    }
                    await websocket.send(json.dumps(subscribe_message))

                # Handle incoming messages
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)

                    if isinstance(data, dict):
                        if data.get('event') == 'subscribed' and data.get('channel') == 'trades':
                            chan_id_symbol_map[data['chanId']] = data['symbol']

                    elif isinstance(data, list) and len(data) > 1:
                        chan_id = data[0]

                        if data[1] == 'tu':
                            trade_info = data[2]
                            symbol = chan_id_symbol_map.get(chan_id, 'UNKNOWN')

                            if symbol == 'UNKNOWN':
                                try:
                                    symbol = trade_info[0]
                                except IndexError:
                                    print(f"Error: Could not extract symbol from trade_info: {trade_info}")
                                    continue

                            # Process the trade
                            price = float(trade_info[3])
                            quantity = abs(float(trade_info[2]))
                            is_buyer_maker = float(trade_info[2]) < 0
                            trade_time = int(trade_info[1])

                            await process_trade(symbol, price, quantity, trade_time, is_buyer_maker)

        except ConnectionClosed:
            print("No Connection📡❌🛰️ (Bitfinex)")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"[red]An error occurred in bitfinex_trade_stream: {e}[/red]")
            await asyncio.sleep(5)



# OKX Trade Stream
async def okx_trade_stream(uri, threshold_console_manager):
    if not okx_symbols_selected:
        return
    while True:
        try:
            async with connect(uri, max_size=None) as websocket:
                subscribe_message = {
                    "op": "subscribe",
                    "args": [{"channel": "trades", "instId": symbol} for symbol in okx_symbols_selected]
                }
                await websocket.send(json.dumps(subscribe_message))
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    if 'data' in data:
                        for trade_data in data['data']:
                            symbol = trade_data['instId']
                            # Fallback for unknown symbols
                            mapped_symbol = okx_symbol_map.get(symbol, 'UNKNOWN')
                            price = float(trade_data['px'])
                            quantity = float(trade_data['sz'])
                            trade_time = int(trade_data['ts'])
                            side = trade_data['side']  # 'buy' oder 'sell'
                            is_buyer_maker = True if side == 'sell' else False
                            await process_trade(mapped_symbol, price, quantity, trade_time, is_buyer_maker, threshold_console_manager)
        except ConnectionClosed:
            threshold_console_manager.print_error("No Connection📡❌🛰️ (OKX)")
            await asyncio.sleep(5)
        except Exception as e:
            threshold_console_manager.print_error(f"An error occurred in okx_trade_stream: {e}")
            await asyncio.sleep(5)


# CoinCap Trade Stream
async def coincap_trade_stream(uri, threshold_console_manager):
    if not coincap_symbols_selected:
        return

    max_retries = 5  # Maximum retries before resetting backoff
    base_wait_time = 2  # Base wait time in seconds for exponential backoff

    while True:
        try:
            async with connect(uri, max_size=None) as websocket:
                retry_count = 0  # Reset retry count on successful connection
                while True:
                    try:
                        message = await websocket.recv()

                        # Check for empty messages
                        if not message.strip():
                            threshold_console_manager.print_warning("Received empty message from CoinCap.")
                            continue

                        # Parse JSON
                        try:
                            data = json.loads(message)
                        except json.JSONDecodeError:
                            continue

                        # Process trade message
                        if 'message' in data and data['message'] == 'trade':
                            symbol = data['base'].upper()
                            # Fallback for unknown symbols
                            mapped_symbol = coincap_symbol_map.get(symbol, 'UNKNOWN')
                            try:
                                price = float(data['priceUsd'])
                                quantity = float(data['volume'])
                                trade_time = int(datetime.strptime(data['time'], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp() * 1000)
                            except (KeyError, ValueError) as e:
                                threshold_console_manager.print_error(f"Error parsing trade data: {e}")
                                continue

                            is_buyer_maker = False  # CoinCap doesn't provide side information
                            await process_trade(mapped_symbol, price, quantity, trade_time, is_buyer_maker, threshold_console_manager)
                        else:
                            threshold_console_manager.print_warning("Received unexpected message structure from CoinCap.")

                    except ConnectionClosed as e:
                        # Filter out 1005 error from logging
                        if e.code == 1005:
                            # Silently reconnect without logging this specific error
                            await asyncio.sleep(5)
                            continue
                        else:
                            threshold_console_manager.print_error(f"Connection closed with status {e.code}. Reconnecting...")
                            await asyncio.sleep(5)  # Exponential backoff before reconnecting

        except Exception as e:
            threshold_console_manager.print_error(f"An error occurred in coincap_trade_stream: {e}")
            retry_count = min(retry_count + 1, max_retries)
            backoff_time = base_wait_time * (2 ** retry_count) + random.uniform(0, 1)
            await asyncio.sleep(backoff_time)


def select_symbols():
    """
    Allows the user to select which symbols to include in the query.
    """
    title = ' Trade Trail '

    # Färbe den ASCII-Text blau-weiß (blau als Textfarbe, weiß als Hintergrund)
    ascii_title = '🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏\n' + pyfiglet.figlet_format(title) + '🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏'
    print(colored(ascii_title, 'red', 'on_white', attrs=['bold']))

    # Verwende pyfiglet, um den Titel in ASCII-Kunstform darzustellen
    print("""
+------------------------------------------------+
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
            selected_symbols = None  # No filtering, process all symbols
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

    # If no symbols are selected, fallback to all symbols
    if not selected_symbols:
        selected_symbols = symbols  # Use all symbols by default

    # Create the formatted symbol list
    selected_symbols_formatted = [name_map.get(symbol.upper().replace('USDT', ''), symbol.upper().replace('USDT', '')) for symbol in selected_symbols]






    # Determine symbols available on Kraken and Bitfinex
    global kraken_symbols_selected, bitfinex_symbols_selected
    kraken_symbols_selected = [kraken_symbol_map[symbol] for symbol in selected_symbols if symbol in kraken_symbol_map and kraken_symbol_map[symbol] is not None]
    bitfinex_symbols_selected = [bitfinex_symbol_map[symbol] for symbol in selected_symbols if symbol in bitfinex_symbol_map and bitfinex_symbol_map[symbol] is not None]

    if not kraken_symbols_selected:
        console.print("No selected symbols are available on Kraken.")
    if not bitfinex_symbols_selected:
        console.print("No selected symbols are available on Bitfinex.")


async def main():
    """
    Main function that initializes thresholds, selects symbols, and starts WebSocket streams.
    """
    global trade_threshold
    print("⚙️ Start main function ⚙️")

    # Symbol selection
    select_symbols()  # Populate selected_symbols globally
    initialize_maps()  # Initialize the maps for cumulative sums

    # Prompt user for threshold values
    trade_threshold = float(input("🔧Please enter the threshold value for 'usd_size' on trades: "))
    interval = int(input("🔧Please enter the interval for exportation and calculation in seconds: "))

    # Capture the start time in a readable format
    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    tasks = []
    for symbol in selected_symbols:
        stream_url = f"{websocket_url_base_binance}{symbol}@aggTrade"
        tasks.append(binance_trade_stream(stream_url, symbol))
    # Ensure streams and processing are only set up for selected symbols
    tasks.append(coinbase_trade_stream(websocket_url_base_coinbase))
    if kraken_symbols_selected:
        asyncio.create_task(kraken_trade_stream(websocket_url_kraken))
    if bitfinex_symbols_selected:
        asyncio.create_task(bitfinex_trade_stream(websocket_url_bitfinex))
    if okx_symbols_selected:
        tasks.append(okx_trade_stream(websocket_url_okx, threshold_console_manager))
    if coincap_symbols_selected:
        tasks.append(coincap_trade_stream(websocket_url_coincap, threshold_console_manager))
    tasks.append(periodic_export(interval, trade_threshold, start_time))

    print("⚙️ asyncio.gather is running ⚙️")
    await asyncio.gather(*tasks)

# Start the main function properly
print("⚙️ asyncio.run(main()) is running ⚙️")
asyncio.run(main())
print("✅⚙️ Program is done ⚙✅️")
