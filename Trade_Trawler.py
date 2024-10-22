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



#TODO: Uhrzeit des letzten Trades angeben
#TODO: Prozentualer unterschied zur letzten Minute
#TODO: Gleiche Tabelle mit LIquidationsdaten
#TODO: Tabellen nummerieren, um schneller zu erkennen um welchen Threshold es sich handelt
#TODO: Füge einen Parameter ein, welcher die letzten 3 Trades mit Zeit angibt 
# Initialize Colorama
init()
console = Console()
# Data Collection Dictionary
trades_data = {}
trades_data_lock = asyncio.Lock()  # Lock for concurrent access

# Placeholder for user-selected symbols
selected_symbols = []
selected_symbols_formatted = []
kraken_symbols_selected = []
bitfinex_symbols_selected = []
okx_symbols_selected = []
coincap_symbols_selected = []


websocket_url_base_binance = 'wss://fstream.binance.com/ws/'
websocket_url_base_coinbase = 'wss://ws-feed.exchange.coinbase.com'
websocket_url_kraken = 'wss://ws.kraken.com/'
websocket_url_bitfinex = 'wss://api-pub.bitfinex.com/ws/2'
websocket_url_okx = 'wss://ws.okx.com:8443/ws/v5/public'
websocket_url_coincap = 'wss://ws.coincap.io/trades'

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



# Threshold lists
stars_thresholds_1 = [
    (231840000, '⁉️💰🃏💰⁉️'),
    (143285000, '  🐳🐳🐳  '),
    (88555000,  '   🐳🐳   '),
    (54730000,  '    🐳    '),
    (33825000,  '  🦈🦈🦈  '),
    (20905000,  '   🦈🦈   '),
    (12920000,  '    🦈    '),
    (7985000,   '  🦑🦑🦑  '),
    (4935000,   '   🦑🦑   '),
    (3050000,   '    🦑    '),
    (1885000,   '  🐡🐡🐡  '),
    (1165000,   '   🐡🐡   '),
    (720000,    '    🐡    '),
    (445000,    '🐠🐠🐠🐠🐠'),
    (275000,    ' 🐠🐠🐠🐠 '),
    (170000,    '  🐠🐠🐠  '),
    (105000,    '   🐠🐠   '),
    (65000,     '    🐠    '),
    (40000,     '🐟🐟🐟🐟🐟'),
    (25000,     ' 🐟🐟🐟🐟 '),
    (15000,     '  🐟🐟🐟  '),
    (10000,     '   🐟🐟   '),
    (5000,      '    🐟    '),
    (0,         '          ')
]

stars_thresholds_2 = [
    (317811000, '⁉️💰🃏💰⁉️'),
    (196418000, '  🐳🐳🐳  '),
    (121393000, '   🐳🐳   '),
    (75025000,  '    🐳    '),
    (46368000,  '  🦈🦈🦈  '),
    (28657000,  '   🦈🦈   '),
    (17711000,  '    🦈    '),
    (10946000,  '🦑🦑🦑🦑🦑'),
    (6765000,   ' 🦑🦑🦑🦑 '),
    (4181000,   '  🦑🦑🦑  '),
    (2584000,   '   🦑🦑   '),
    (1597000,   '    🦑    '),
    (987000,    '🐡🐡🐡🐡🐡'),
    (610000,    ' 🐡🐡🐡🐡 '),
    (377000,    '  🐡🐡🐡  '),
    (233000,    '   🐡🐡   '),
    (144000,    '    🐡    '),
    (89000,     '🐠🐠🐠🐠🐠'),
    (55000,     ' 🐠🐠🐠🐠 '),
    (34000,     '  🐠🐠🐠  '),
    (21000,     '   🐠🐠   '),
    (13000,     '    🐠    '),
    (8000,      '🐟🐟🐟🐟🐟'),
    (5000,      ' 🐟🐟🐟🐟 '),
    (3000,      '  🐟🐟🐟  '),
    (2000,      '   🐟🐟   '),
    (1000,      '    🐟    '),
    (0,         '          ')
]

stars_thresholds_3 = [
    (262144000, '⁉️💰🃏💰⁉️'),
    (131072000, '  🐳🐳🐳  '),
    (65536000,  '   🐳🐳   '),
    (32768000,  '    🐳    '),
    (16384000,  '  🦈🦈🦈  '),
    (8192000,   '   🦈🦈   '),
    (4096000,   '    🦈    '),
    (2048000,   '  🦑🦑🦑  '),
    (1024000,   '   🦑🦑   '),
    (512000,    '    🦑    '),
    (256000,    '  🐡🐡🐡  '),
    (128000,    '   🐡🐡   '),
    (64000,     '    🐡    '),
    (32000,     '  🐠🐠🐠  '),
    (16000,     '   🐠🐠   '),
    (8000,      '    🐠    '),
    (4000,      '  🐟🐟🐟  '),
    (2000,      '   🐟🐟   '),
    (1000,      '    🐟    '),
    (0,         '          ')
]

stars_thresholds_4 = [
    (100000000, '    🐳    '),
    (10000000,  '    🦈    '),
    (1000000,   '    🦑    '),
    (100000,    '    🐬    '),
    (10000,     '    🐡    '),
    (1000,      '    🐠    '),
    (100,       '    🐟    '),
    (0,         '          ')
]

stars_thresholds_5 = [
    (5000000,     '⁉️💰🃏💰⁉️'),
    (1925000,     '🦄🦄🦄🦄🦄'),
    (1775000,     ' 🦄🦄🦄🦄 '),
    (1633000,     '  🦄🦄🦄  '),
    (1499000,     '   🦄🦄   '),
    (1373000,     '    🦄    '),
    (1255000,     '🐳🐳🐳🐳🐳'),
    (1145000,     ' 🐳🐳🐳🐳 '),
    (1043000,     '  🐳🐳🐳  '),
    (949000,      '   🐳🐳   '),
    (863000,      '    🐳    '),
    (785000,      '🦈🦈🦈🦈🦈'),
    (715000,      ' 🦈🦈🦈🦈 '),
    (649000,      '  🦈🦈🦈  '),
    (587000,      '   🦈🦈   '),
    (529000,      '    🦈    '),
    (475000,      '🦑🦑🦑🦑🦑'),
    (425000,      ' 🦑🦑🦑🦑 '),
    (379000,      '  🦑🦑🦑  '),
    (337000,      '   🦑🦑   '),
    (299000,      '    🦑    '),
    (265000,      '🐬🐬🐬🐬🐬'),
    (235000,      ' 🐬🐬🐬🐬 '),
    (207000,      '  🐬🐬🐬  '),
    (181000,      '   🐬🐬   '),
    (157000,      '    🐬    '),
    (135000,      '🐡🐡🐡🐡🐡'),
    (115000,      ' 🐡🐡🐡🐡 '),
    (97000,       '  🐡🐡🐡  '),
    (81000,       '   🐡🐡   '),
    (67000,       '    🐡    '),
    (55000,       '🐠🐠🐠🐠🐠'),
    (45000,       ' 🐠🐠🐠🐠 '),
    (36000,       '  🐠🐠🐠  '),
    (28000,       '   🐠🐠   '),
    (21000,       '    🐠    '),
    (15000,       '🐟🐟🐟🐟🐟'),
    (10000,       ' 🐟🐟🐟🐟 '),
    (6000,        '  🐟🐟🐟  '),
    (3000,        '   🐟🐟   '),
    (1000,        '    🐟    '),
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
                metrics = calculate_metrics_with_stars(trades_data, self.start_timestamp)
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
    """
    Calculates the time difference between start_time and current_time.
    """
    # Convert start_time and current_time to datetime objects
    start_datetime = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    current_datetime = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')

    # Calculate the time difference
    time_difference = current_datetime - start_datetime

    # Return time difference in a readable format
    return str(time_difference)

def format_trade_time(trade_time):
    """Formats the trade time to a readable format based on Berlin timezone."""
    berlin = pytz.timezone("Europe/Berlin")
    return datetime.fromtimestamp(trade_time / 1000, berlin).strftime('%H:%M:%S')

async def collect_trade_data(symbol, used_trade_time, trade_type, usd_size, timestamp, threshold_console_manager):
    try:
        usd_size = float(usd_size)  # Ensure usd_size is stored as a float
    except ValueError:
        threshold_console_manager.print_error(f"Error: Invalid usd_size '{usd_size}' for trade.")
        return

    stars = get_stars(usd_size, threshold_console_manager)
    
    # Speichere die Transaktion basierend auf dem Threshold (wie bisher)
    async with trades_data_lock:
        if stars not in trades_data:
            trades_data[stars] = []
        trades_data[stars].append([symbol, used_trade_time, trade_type, usd_size, timestamp])
        
        # Speichere auch die Transaktion in einer neuen Kategorie für alle Transaktionen
        if "all_trades" not in trades_data:
            trades_data["all_trades"] = []
        trades_data["all_trades"].append([symbol, used_trade_time, trade_type, usd_size, timestamp])

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
    Asks the user to input the time window (in minutes) for which trades should be stored and calculated.
    """
    while True:
        try:
            time_window = float(input("Enter the time window for trade data (in minutes): ").strip())
            if time_window <= 0:
                print("Please enter a positive number.")
                continue
            return time_window * 60  # Convert minutes to seconds
        except ValueError:
            print("Invalid input. Please enter a number.")

async def cleanup_old_trades(time_window, cleanup_interval=10):
    """
    Periodically removes trades that are older than the specified time window from trades_data.
    """
    while True:
        current_time_ms = datetime.now().timestamp() * 1000  # Current time in milliseconds
        cutoff_time = current_time_ms - (time_window * 1000)  # Convert time_window to milliseconds

        # Acquire lock to safely modify trades_data
        async with trades_data_lock:
            for stars in list(trades_data.keys()):
                trades_list = trades_data[stars]
                # Filter trades to keep only those within the time window
                trades_data[stars] = [trade for trade in trades_list if trade[4] >= cutoff_time]

        await asyncio.sleep(cleanup_interval)

def calculate_metrics_with_stars(trades_data, start_timestamp):
    current_time = datetime.now().timestamp() * 1000  # Current time in milliseconds
    total_elapsed_time = (current_time - start_timestamp) / 1000  # in seconds

    metrics = {}
    trades_list_all = trades_data.get('all_trades', [])
    total_trades_all = len(trades_list_all)
    total_trades_all_per_minute = (total_trades_all * 60) / total_elapsed_time if total_elapsed_time > 0 else 0
    total_usd_size_all_long = sum(trade[3] for trade in trades_list_all if trade[2] == '📈 ')
    total_usd_size_all_short = sum(trade[3] for trade in trades_list_all if trade[2] == '📉 ')
    total_usd_size_all = total_usd_size_all_long + total_usd_size_all_short
    total_usd_size_all_per_minute = (total_usd_size_all * 60) / total_elapsed_time if total_elapsed_time > 0 else 0
    total_usd_size_all_long_percentage = (total_usd_size_all_long / total_usd_size_all) * 100 if total_usd_size_all > 0 else 0
    total_usd_size_all_short_percentage = (total_usd_size_all_short / total_usd_size_all) * 100 if total_usd_size_all > 0 else 0
    total_usd_size_all_difference = total_usd_size_all_long - total_usd_size_all_short
    total_usd_size_all_difference_percentage = total_usd_size_all_long_percentage - total_usd_size_all_short_percentage

    for threshold, stars in stars_thresholds:
        trades_list = trades_data.get(stars, [])
        # Initialize metrics for this category
        category_metrics = {}
        total_trades = len(trades_list)

        # Long and short trades counts
        trades_long_count = sum(1 for trade in trades_list if trade[2] == '📈 ')
        trades_short_count = sum(1 for trade in trades_list if trade[2] == '📉 ')
        trades_difference_count = trades_long_count - trades_short_count

        # Percentage of Long and short trades
        trades_long_count_percentage = (trades_long_count / total_trades) * 100 if total_trades > 0 else 0
        trades_short_count_percentage = (trades_short_count / total_trades) * 100 if total_trades > 0 else 0
        trade_count_difference_percentage = trades_long_count_percentage - trades_short_count_percentage

        # Total USD size of Long and short trades
        total_usd_size_long = sum(trade[3] for trade in trades_list if trade[2] == '📈 ')
        total_usd_size_short = sum(trade[3] for trade in trades_list if trade[2] == '📉 ')

        total_usd_size = total_usd_size_long + total_usd_size_short
        usd_size_difference = total_usd_size_long - total_usd_size_short

        # Percentage of Long and short trades
        total_usd_size_long_percentage = (total_usd_size_long / total_usd_size) * 100 if total_usd_size > 0 else 0
        total_usd_size_short_percentage = (total_usd_size_short / total_usd_size) * 100 if total_usd_size > 0 else 0
        usd_size_difference_percentage = total_usd_size_long_percentage - total_usd_size_short_percentage

        # Average trades and USD size per minute since program start
        avg_trades_per_minute = (total_trades * 60) / total_elapsed_time if total_elapsed_time > 0 else 0
        avg_usd_size_per_minute = (total_usd_size * 60) / total_elapsed_time if total_elapsed_time > 0 else 0

        # Determine the color of the average usd_size
        usd_size_color = 'green' if avg_usd_size_per_minute > 0 else 'red'
        # Determine the color based on the difference
        difference_color = 'green' if usd_size_difference > 0 else 'red'

        # Store metrics
        category_metrics['total_trades'] = total_trades
        category_metrics['trades_long_count'] = trades_long_count
        category_metrics['trades_short_count'] = trades_short_count
        category_metrics['trades_difference_count'] = trades_difference_count
        category_metrics['trades_long_count_percentage'] = trades_long_count_percentage
        category_metrics['trades_short_count_percentage'] = trades_short_count_percentage
        category_metrics['trade__count_difference_percentage'] = trade_count_difference_percentage
        category_metrics['total_usd_size_long'] = total_usd_size_long
        category_metrics['total_usd_size_short'] = total_usd_size_short
        category_metrics['total_usd_size'] = total_usd_size
        category_metrics['usd_size_difference'] = usd_size_difference
        category_metrics['total_usd_size_long_percentage'] = total_usd_size_long_percentage
        category_metrics['total_usd_size_short_percentage'] = total_usd_size_short_percentage
        category_metrics['usd_size_difference_percentage'] = usd_size_difference_percentage
        category_metrics['avg_trades_per_minute'] = avg_trades_per_minute
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

    #Calculate percentage of each catergory in total_trades
    for stars in metrics:
        total_trades = metrics[stars]['total_trades']
        total_trades_percentage = (total_trades / sum(metrics[s]['total_trades'] for s in metrics)) * 100 if total_trades > 0 else 0
        metrics[stars]['total_trades_percentage'] = total_trades_percentage

    metrics['total_usd_size_all'] = total_usd_size_all
    metrics['total_trades_all'] = total_trades_all
    metrics['total_trades_all_per_minute'] = total_trades_all_per_minute
    metrics['total_usd_size_all_per_minute'] = total_usd_size_all_per_minute
    metrics['total_usd_size_all_long'] = total_usd_size_all_long
    metrics['total_usd_size_all_short'] = total_usd_size_all_short
    metrics['total_usd_size_all_difference'] = total_usd_size_all_difference
    metrics['total_usd_size_all_difference_percentage'] = total_usd_size_all_difference_percentage
    metrics['total_usd_size_all_long_percentage'] = total_usd_size_all_long_percentage
    metrics['total_usd_size_all_short_percentage'] = total_usd_size_all_short_percentage

    return metrics

async def process_trade(symbol, price, quantity, trade_time, is_buyer_maker, threshold_console_manager):
    try:
        usd_size = float(price) * float(quantity)  # Ensure price and quantity are numbers
    except ValueError:
        threshold_console_manager.print_error(f"Error: Invalid price or quantity received - price: {price}, quantity: {quantity}")
        return  # Exit the function if the calculation fails
    
    symbol = symbol.upper().replace('USDT', '')
    trade_type = '📉 ' if is_buyer_maker else '📈 '
    if symbol == 'XBT':
        symbol = 'BTC'
    
    if usd_size >= 10:  # Filter for minimum trade size
        used_trade_time = format_trade_time(trade_time)
        await collect_trade_data(symbol, used_trade_time, trade_type, usd_size, trade_time, threshold_console_manager)

# Binance Trade Stream
async def binance_trade_stream(uri, symbol, threshold_console_manager):
    while True:
        try:
            async with connect(uri, max_size=None) as websocket:
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    price = float(data['p'])
                    quantity = float(data['q'])
                    trade_time = int(data['T'])
                    is_buyer_maker = data['m']
                    await process_trade(symbol, price, quantity, trade_time, is_buyer_maker, threshold_console_manager)
        except ConnectionClosed:
            threshold_console_manager.print_error("No Connection📡❌🛰️ (Binance Trade)")
            await asyncio.sleep(5)
        except Exception as e:
            threshold_console_manager.print_error(f"An error occurred in binance_trade_stream: {e}")
            await asyncio.sleep(5)

# Coinbase Trade Stream
async def coinbase_trade_stream(uri, threshold_console_manager):
    coinbase_symbols = [symbol.split('usdt')[0].upper() + '-USD' for symbol in selected_symbols if symbol.endswith('usdt')]
    if not coinbase_symbols:
        return
    while True:
        try:
            async with connect(uri, max_size=None) as websocket:
                subscribe_message = {
                    "type": "subscribe",
                    "channels": [{"name": "ticker", "product_ids": coinbase_symbols}]
                }
                await websocket.send(json.dumps(subscribe_message))
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    if data.get('type') == 'ticker':
                        product_id = data['product_id']
                        symbol = product_id.split('-')[0].upper()
                        price = float(data['price'])
                        quantity = float(data['last_size'])
                        trade_time = int(datetime.fromisoformat(data['time'].replace('Z', '+00:00')).timestamp() * 1000)
                        is_buyer_maker = data['side'] == 'sell'
                        await process_trade(symbol, price, quantity, trade_time, is_buyer_maker, threshold_console_manager)
        except ConnectionClosed:
            threshold_console_manager.print_error("No Connection📡❌🛰️ (Coinbase)")
            await asyncio.sleep(5)
        except Exception as e:
            threshold_console_manager.print_error(f"An error occurred in coinbase_trade_stream: {e}")
            await asyncio.sleep(5)

# Kraken Trade Stream
async def kraken_trade_stream(uri, threshold_console_manager):
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
                    if isinstance(data, list) and len(data) > 0 and data[-1] == 'trade':
                        trades = data[1]
                        pair = data[3]
                        symbol = pair.split('/')[0]
                        if symbol == 'XBT':
                            symbol = 'BTC'
                        for trade in trades:
                            price = float(trade[0])
                            quantity = float(trade[1])
                            trade_time = int(float(trade[2]) * 1000)
                            side = trade[3]  # 'b' or 's'
                            is_buyer_maker = True if side == 's' else False
                            await process_trade(symbol, price, quantity, trade_time, is_buyer_maker, threshold_console_manager)
        except ConnectionClosed:
            threshold_console_manager.print_error("No Connection📡❌🛰️ (Kraken)")
            await asyncio.sleep(5)
        except Exception as e:
            threshold_console_manager.print_error(f"An error occurred in kraken_trade_stream: {e}")
            await asyncio.sleep(5)


# Bitfinex Trade Stream
async def bitfinex_trade_stream(uri, threshold_console_manager):
    if not bitfinex_symbols_selected:
        return
    chan_id_symbol_map = {}
    while True:
        try:
            async with connect(uri, max_size=None) as websocket:
                # Subscribe to trades for each symbol
                for symbol in bitfinex_symbols_selected:
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
                    elif isinstance(data, list):
                        chan_id = data[0]
                        if len(data) > 1 and data[1] == 'tu':
                            # Trade executed update
                            trade_info = data[2]
                            symbol = chan_id_symbol_map.get(chan_id, 'UNKNOWN').lstrip('t')
                            if symbol == 'BTC':
                                symbol = 'BTC'
                            price = float(trade_info[3])
                            quantity = abs(float(trade_info[2]))
                            is_buyer_maker = True if float(trade_info[2]) < 0 else False
                            trade_time = int(trade_info[1])
                            await process_trade(symbol, price, quantity, trade_time, is_buyer_maker, threshold_console_manager)
        except ConnectionClosed:
            threshold_console_manager.print_error("No Connection📡❌🛰️ (Bitfinex)")
            await asyncio.sleep(5)
        except Exception as e:
            threshold_console_manager.print_error(f"An error occurred in bitfinex_trade_stream: {e}")
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
                            if symbol in okx_symbol_map:
                                mapped_symbol = okx_symbol_map[symbol]
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
                            if symbol in coincap_symbol_map:
                                mapped_symbol = coincap_symbol_map[symbol]
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




def export_to_excel(trades_data, directory):
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
        trades = trades_data.get(stars, [])
        if trades:
            # Erstelle einen DataFrame aus den Trades
            df = pd.DataFrame(trades, columns=['Symbol', 'Time', 'Type', 'USD Size', 'Timestamp'])
            # Sortiere nach Timestamp
            df = df.sort_values(by='Timestamp')
            
            # Erstelle den Dateinamen unter Berücksichtigung der Symbole
            filename = f"Trades_Threshold_{threshold}_{symbols_name}.xlsx"
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
    Periodically saves the trades data to Excel files every 'interval' seconds.
    """
    while True:
        export_to_excel(trades_data, directory)
        await asyncio.sleep(interval)

def fetch_binance_symbols():
    import requests
    url = 'https://fapi.binance.com/fapi/v1/exchangeInfo'
    response = requests.get(url)
    data = response.json()
    symbols = [item['symbol'].lower() for item in data['symbols'] if item['status'] == 'TRADING']
    return symbols

def select_symbols():
    """
    Allows the user to select which symbols to include in the query.
    """
    title = ' Trade Trawler'

    # Färbe den ASCII-Text blau-weiß (blau als Textfarbe, weiß als Hintergrund)
    ascii_title = '🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏\n' + pyfiglet.figlet_format(title) + '🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏'
    print(colored(ascii_title, 'blue', 'on_white', attrs=['bold']))
    print(colored("     🚢Trade Trawler sets sail and gets ready to fish🐟🐠🦑🐳     ", 'black', 'on_blue'))
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
            selected_symbols = fetch_binance_symbols()
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
        selected_symbols = fetch_binance_symbols()
        selected_symbols_display = "🃏ALL🃏"

    # Create the formatted symbol list
    selected_symbols_formatted = [name_map.get(symbol.upper().replace('USDT', ''), symbol.upper().replace('USDT', '')) for symbol in selected_symbols]


    # Bestimmen der Symbole, die auf den jeweiligen Börsen verfügbar sind
    global kraken_symbols_selected, bitfinex_symbols_selected, okx_symbols_selected, coincap_symbols_selected

    # Kraken und Bitfinex (bereits vorhanden)
    kraken_symbols_selected = [kraken_symbol_map[symbol] for symbol in selected_symbols if symbol in kraken_symbol_map and kraken_symbol_map[symbol] is not None]
    bitfinex_symbols_selected = [bitfinex_symbol_map[symbol] for symbol in selected_symbols if symbol in bitfinex_symbol_map and bitfinex_symbol_map[symbol] is not None]

    # OKX Symbole vorbereiten
    okx_symbols_selected = [symbol.upper().replace('USDT', '-USDT') for symbol in selected_symbols]
    okx_symbol_map = {symbol.upper().replace('USDT', '-USDT'): symbol for symbol in selected_symbols}

    # CoinCap Symbole vorbereiten
    coincap_symbols_selected = [symbol.upper().replace('USDT', '') for symbol in selected_symbols]
    coincap_symbol_map = {symbol.upper().replace('USDT', ''): symbol for symbol in selected_symbols}


async def main():
    # Symbol selection and initialization
    select_symbols()
    select_thresholds()

    # Get the time window from the user
    time_window_seconds = get_time_window()

    # Capture the start time
    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    start_timestamp = datetime.now().timestamp() * 1000

    # Initialisiere die Variable hier, bevor sie verwendet wird
    global selected_symbols_display
    if not selected_symbols:
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

    # Start WebSocket tasks
    for symbol in selected_symbols:
        stream_url = f"{websocket_url_base_binance}{symbol}@aggTrade"
        asyncio.create_task(binance_trade_stream(stream_url, symbol, threshold_console_manager))

    asyncio.create_task(coinbase_trade_stream(websocket_url_base_coinbase, threshold_console_manager))
    if kraken_symbols_selected:
        asyncio.create_task(kraken_trade_stream(websocket_url_kraken, threshold_console_manager))

    if bitfinex_symbols_selected:
        asyncio.create_task(bitfinex_trade_stream(websocket_url_bitfinex, threshold_console_manager))

    asyncio.create_task(okx_trade_stream(websocket_url_okx, threshold_console_manager))
    asyncio.create_task(coincap_trade_stream(websocket_url_coincap, threshold_console_manager))

    # Start periodic data saving
    directory = "/home/jestersly/Schreibtisch/Codes/_Algo_Trade_Edge/Data_Streams/Trade_Trawler_Catch/"
    asyncio.create_task(save_data_periodically(directory))

    # Start cleaning up old trades
    asyncio.create_task(cleanup_old_trades(time_window_seconds))

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
