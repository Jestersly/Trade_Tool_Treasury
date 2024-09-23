import asyncio
import json
from datetime import datetime
import pytz
from websockets import connect, ConnectionClosed
from termcolor import colored
from colorama import init
from rich.live import Live
from rich.table import Table
from rich.console import Console, Group
from rich.text import Text
from rich.panel import Panel
from rich.layout import Layout
from textual.app import App, ComposeResult
from textual.reactive import Reactive
from textual.widgets import Header, Footer, Static
from textual.layouts.grid import GridLayout
from textual.containers import Grid
from tabulate import tabulate
import pyfiglet
import math

# Initialize Colorama
init()

console = Console()

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
    'ksmusdt', 'renusdt'
]


# Placeholder for user-selected symbols
selected_symbols = []
selected_symbols_formatted = []

websocket_url_base_binance = 'wss://fstream.binance.com/ws/'
websocket_url_base_coinbase = 'wss://ws-feed.exchange.coinbase.com'
websocket_url_kraken = 'wss://ws.kraken.com/'
websocket_url_bitfinex = 'wss://api-pub.bitfinex.com/ws/2'

# Initialize Variables
name_map = {
    'BTC': '🟡BTC     ', 'ETH': '💠ETH     ', 'SOL': '👾SOL     ', 'BNB': '🔶BNB     ', 'DOGE': '🐶DOGE    ',
    'USDC': '💵USDC    ', 'XRP': '⚫XRP     ', 'ADA': '🔵ADA     ', 'MATIC': '🟣MATIC   ',
    'TON': '🎮TON     ', 'LINK': '🔗LINK    ', 'TRX': '⚙️TRX     ', 'NEAR': '🔍NEAR    ', 'XLM': '🌟XLM     ',
    'RNDR': '🎨RNDR    ', 'DOT': '⚪DOT     ', 'UNI': '🦄UNI     ', 'ATOM': '⚛️ATOM    ', 'XMR': '👽XMR     ',
    'LDO': '🧪LDO     ', 'GMX': '🌀GMX     ', 'LTC': '🌕LTC     ', 'AVAX': '🏔️AVAX    ', 'BCH': '💰BCH     ',
    'VET': '♻️VET     ', 'FIL': '📁FIL     ', 'ETC': '⛏️ETC     ', 'ALGO': '🔺ALGO    ', 'XTZ': '🏺XTZ     ',
    'EOS': '🌐EOS     ', 'AAVE': '🏦AAVE    ', 'MKR': '🏭MKR     ', 'THETA': '📺THETA   ', 'AXS': '🕹️AXS     ',
    'SAND': '🏖️SAND    ', 'ICP': '🌐ICP     ', 'SHIB': '🐾SHIB    ', 'APT': '🚀APT     ', 'GRT': '📊GRT     ',
    'ENJ': '🎮ENJ     ', 'CHZ': '⚽CHZ     ', 'MANA': '🌐MANA    ', 'SUSHI': '🍣SUSHI   ', 'BAT': '🦇BAT     ',
    'ZEC': '💰ZEC     ', 'DASH': '⚡DASH    ', 'NEO': '💹NEO     ', 'IOTA': '🔗IOTA    ', 'OMG': '😮OMG     ',
    'CAKE': '🍰CAKE    ', 'STX': '📚STX     ', 'SNX': '💎SNX     ', 'COMP': '🏦COMP    ', 'ZIL': '💠ZIL     ',
    'KSM': '🪶KSM     ', 'REN': '🔄REN     '
}


# Data Collection Lists
trades_data = []

# Thresholds for printing output
trade_threshold = 0

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
    'rndrusdt': None,  # RNDR not available on Kraken
    'dotusdt': 'DOT/USDT',
    'uniusdt': 'UNI/USDT',
    'atomusdt': 'ATOM/USDT',
    'xmrusdt': 'XMR/USDT',
    'ldousdt': None,  # LDO not available on Kraken
    'gmxusdt': None,  # GMX not available on Kraken
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
    'renusdt': 'REN/USDT'
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
    'rndrusdt': None,  # RNDR not available on Bitfinex
    'dotusdt': 'tDOTUSD',
    'uniusdt': 'tUNIUSD',
    'atomusdt': 'tATOMUSD',
    'xmrusdt': 'tXMRUSD',
    'ldousdt': None,  # LDO not available on Bitfinex
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
    'manausdt': 'tMNAUSD',  # Bitfinex uses 'MNA' for MANA
    'sushiusdt': 'tSUSHIUSD',
    'batusdt': 'tBATUSD',
    'zecusdt': 'tZECUSD',
    'dashusdt': 'tDSHUSD',  # Bitfinex uses 'DSH' for DASH
    'neousdt': 'tNEOUSD',
    'iotausdt': 'tIOTUSD',  # Bitfinex uses 'IOT' for IOTA
    'omgusdt': 'tOMGUSD',
    'cakeusdt': None,  # CAKE not available on Bitfinex
    'stxusdt': 'tSTXUSD',
    'snxusdt': 'tSNXUSD',
    'compusdt': 'tCOMPUSD',
    'zilusdt': 'tZILUSD',
    'ksmusdt': 'tKSMUSD',
    'renusdt': 'tRENUSD'
}


# Initialize exchange-specific symbol lists
kraken_symbols_selected = []
bitfinex_symbols_selected = []

def format_trade_time(trade_time):
    """Formats the trade time to a readable format based on Berlin timezone."""
    berlin = pytz.timezone("Europe/Berlin")
    return datetime.fromtimestamp(trade_time / 1000, berlin).strftime('%H:%M:%S')



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

def collect_trade_data(symbol, used_trade_time, trade_type, usd_size, timestamp):
    """
    Collects trade data and appends it to the trades_data list.
    """
    trades_data.append([symbol, used_trade_time, trade_type, usd_size, timestamp])

def get_stars(usd_size):
    if usd_size >= 1310720000:
        return '⁉️💰🃏💰⁉️'
    elif usd_size >= 655360000:
        return '💸🌠🦄🌠💸'
    elif usd_size >= 327680000:
        return '  🌠🦄🌠  '
    elif usd_size >= 163840000:
        return '  🐳🐳🐳  '
    elif usd_size >= 81920000:
        return '   🐳🐳   '
    elif usd_size >= 40960000:
        return '    🐳    '
    elif usd_size >= 20480000:
        return '  🦑🦑🦑  '
    elif usd_size >= 10240000:
        return '   🦑🦑   '
    elif usd_size >= 5120000:
        return '    🦑    '
    elif usd_size >= 2560000:
        return '🐠🐠🐠🐠🐠'
    elif usd_size >= 1280000:
        return ' 🐠🐠🐠🐠 '
    elif usd_size >= 640000:
        return '  🐠🐠🐠  '
    elif usd_size >= 320000:
        return '   🐠🐠   '
    elif usd_size >= 160000:
        return '    🐠    '
    elif usd_size >= 80000:
        return '🐟🐟🐟🐟🐟'
    elif usd_size >= 40000:
        return ' 🐟🐟🐟🐟 '
    elif usd_size >= 20000:
        return '  🐟🐟🐟  '
    elif usd_size >= 10000:
        return '   🐟🐟   '
    elif usd_size >= 5000:
        return '    🐟    '
    else:
        return '          '


def calculate_metrics(trades_data, trade_threshold, average_interval_1, average_interval_2, average_interval_3, start_timestamp):
    current_time = datetime.now().timestamp() * 1000  # Current time in milliseconds

    # Total elapsed time since program start in seconds
    total_elapsed_time = (current_time - start_timestamp) / 1000

    # Filter data to last average_interval_1 seconds
    filtered_trades_data = [trade for trade in trades_data if current_time - trade[4] <= average_interval_1 * 1000]
    # --- Calculations within the average_interval_1 ---

    # Trades within the interval 1
    total_trades_in_interval_1 = len(filtered_trades_data)
    total_usd_size_in_interval_1 = sum(trade[3] if trade[2] == '📈 ' else -trade[3] for trade in filtered_trades_data)

    trades_long_count_1 = sum(1 for trade in filtered_trades_data if trade[2] == '📈 ')
    trades_short_count_1 = sum(1 for trade in filtered_trades_data if trade[2] == '📉 ')
    trades_difference_count_1 = trades_long_count_1 - trades_short_count_1

    trades_long_count_percentage_1 = (trades_long_count_1 / total_trades_in_interval_1) * 100 if total_trades_in_interval_1 > 0 else 0
    trades_short_count_percentage_1 = (trades_short_count_1 / total_trades_in_interval_1) * 100 if total_trades_in_interval_1 > 0 else 0

    total_usd_size_long_1 = sum(trade[3] for trade in filtered_trades_data if trade[2] == '📈 ')
    total_usd_size_short_1 = sum(trade[3] for trade in filtered_trades_data if trade[2] == '📉 ')

    usd_size_difference_1 = total_usd_size_long_1 - total_usd_size_short_1
    total_usd_size_trades_1 = total_usd_size_long_1 + total_usd_size_short_1

    total_usd_size_long_percentage_1 = (total_usd_size_long_1 / total_usd_size_trades_1) * 100 if total_usd_size_trades_1 > 0 else 0
    total_usd_size_short_percentage_1 = (total_usd_size_short_1 / total_usd_size_trades_1) * 100 if total_usd_size_trades_1 > 0 else 0

    # Averages per minute
    avg_trades_per_minute_1 = (total_trades_in_interval_1 * 60) / average_interval_1 if average_interval_1 > 0 else 0
    avg_usd_size_per_minute_1 = (total_usd_size_in_interval_1 * 60) / average_interval_1 if average_interval_1 > 0 else 0


    # Count stars for trades within the interval
    stars_count_trades_1 = {}
    for trade in filtered_trades_data:
        usd_size = trade[3]
        stars = get_stars(usd_size)
        trade_type = trade[2]
        symbol = trade[0]
        if stars not in stars_count_trades_1:
            stars_count_trades_1[stars] = {}
        if trade_type not in stars_count_trades_1[stars]:
            stars_count_trades_1[stars][trade_type] = {}
        if symbol not in stars_count_trades_1[stars][trade_type]:
            stars_count_trades_1[stars][trade_type][symbol] = {'count': 0, 'total_usd_size': 0}
        stars_count_trades_1[stars][trade_type][symbol]['count'] += 1
        stars_count_trades_1[stars][trade_type][symbol]['total_usd_size'] += usd_size


    #trades within the interval 2
    total_trades_in_interval_2 = len(filtered_trades_data)
    total_usd_size_in_interval_2 = sum(trade[3] if trade[2] == '📈 ' else -trade[3] for trade in filtered_trades_data)

    trades_long_count_2 = sum(1 for trade in filtered_trades_data if trade[2] == '📈 ')
    trades_short_count_2 = sum(1 for trade in filtered_trades_data if trade[2] == '📉 ')
    trades_difference_count_2 = trades_long_count_2 - trades_short_count_2

    trades_long_count_percentage_2 = (trades_long_count_2 / total_trades_in_interval_2) * 100 if total_trades_in_interval_2 > 0 else 0
    trades_short_count_percentage_2 = (trades_short_count_2 / total_trades_in_interval_2) * 100 if total_trades_in_interval_2 > 0 else 0

    total_usd_size_long_2 = sum(trade[3] for trade in filtered_trades_data if trade[2] == '📈 ')
    total_usd_size_short_2 = sum(trade[3] for trade in filtered_trades_data if trade[2] == '📉 ')

    usd_size_difference_2 = total_usd_size_long_2 - total_usd_size_short_2
    total_usd_size_trades_2 = total_usd_size_long_2 + total_usd_size_short_2

    total_usd_size_long_percentage_2 = (total_usd_size_long_2 / total_usd_size_trades_2) * 100 if total_usd_size_trades_2 > 0 else 0
    total_usd_size_short_percentage_2 = (total_usd_size_short_2 / total_usd_size_trades_2) * 100 if total_usd_size_trades_2 > 0 else 0

    # Averages per minute
    avg_trades_per_minute_2 = (total_trades_in_interval_2 * 60) / average_interval_2 if average_interval_2 > 0 else 0
    avg_usd_size_per_minute_2 = (total_usd_size_in_interval_2 * 60) / average_interval_2 if average_interval_2 > 0 else 0


    # Count stars for trades within the interval
    stars_count_trades_2 = {}
    for trade in filtered_trades_data:
        usd_size = trade[3]
        stars = get_stars(usd_size)
        trade_type = trade[2]
        symbol = trade[0]
        if stars not in stars_count_trades_2:
            stars_count_trades_2[stars] = {}
        if trade_type not in stars_count_trades_2[stars]:
            stars_count_trades_2[stars][trade_type] = {}
        if symbol not in stars_count_trades_2[stars][trade_type]:
            stars_count_trades_2[stars][trade_type][symbol] = {'count': 0, 'total_usd_size': 0}
        stars_count_trades_2[stars][trade_type][symbol]['count'] += 1
        stars_count_trades_2[stars][trade_type][symbol]['total_usd_size'] += usd_size


    #trades within the interval 3
    total_trades_in_interval_3 = len(filtered_trades_data)
    total_usd_size_in_interval_3 = sum(trade[3] if trade[2] == '📈 ' else -trade[3] for trade in filtered_trades_data)

    trades_long_count_3 = sum(1 for trade in filtered_trades_data if trade[2] == '📈 ')
    trades_short_count_3 = sum(1 for trade in filtered_trades_data if trade[2] == '📉 ')
    trades_difference_count_3 = trades_long_count_3 - trades_short_count_3

    trades_long_count_percentage_3 = (trades_long_count_3 / total_trades_in_interval_3) * 100 if total_trades_in_interval_3 > 0 else 0
    trades_short_count_percentage_3 = (trades_short_count_3 / total_trades_in_interval_3) * 100 if total_trades_in_interval_3 > 0 else 0

    total_usd_size_long_3 = sum(trade[3] for trade in filtered_trades_data if trade[2] == '📈 ')
    total_usd_size_short_3 = sum(trade[3] for trade in filtered_trades_data if trade[2] == '📉 ')

    usd_size_difference_3 = total_usd_size_long_3 - total_usd_size_short_3
    total_usd_size_trades_3 = total_usd_size_long_3 + total_usd_size_short_3

    total_usd_size_long_percentage_3 = (total_usd_size_long_3 / total_usd_size_trades_3) * 100 if total_usd_size_trades_3 > 0 else 0
    total_usd_size_short_percentage_3 = (total_usd_size_short_3 / total_usd_size_trades_3) * 100 if total_usd_size_trades_3 > 0 else 0

    # Averages per minute
    avg_trades_per_minute_3 = (total_trades_in_interval_3 * 60) / average_interval_3 if average_interval_3 > 0 else 0
    avg_usd_size_per_minute_3 = (total_usd_size_in_interval_3 * 60) / average_interval_3 if average_interval_3 > 0 else 0


    # Count stars for trades within the interval
    stars_count_trades_3 = {}
    for trade in filtered_trades_data:
        usd_size = trade[3]
        stars = get_stars(usd_size)
        trade_type = trade[2]
        symbol = trade[0]
        if stars not in stars_count_trades_3:
            stars_count_trades_3[stars] = {}
        if trade_type not in stars_count_trades_3[stars]:
            stars_count_trades_3[stars][trade_type] = {}
        if symbol not in stars_count_trades_3[stars][trade_type]:
            stars_count_trades_3[stars][trade_type][symbol] = {'count': 0, 'total_usd_size': 0}
        stars_count_trades_3[stars][trade_type][symbol]['count'] += 1
        stars_count_trades_3[stars][trade_type][symbol]['total_usd_size'] += usd_size


# --- Cumulative calculations since program start ---
    stars_count_trades_all = {}
    for trade in trades_data:
        usd_size = trade[3]
        stars = get_stars(usd_size)
        trade_type = trade[2]
        symbol = trade[0]
        if stars not in stars_count_trades_all:
            stars_count_trades_all[stars] = {}
        if trade_type not in stars_count_trades_all[stars]:
            stars_count_trades_all[stars][trade_type] = {}
        if symbol not in stars_count_trades_all[stars][trade_type]:
            stars_count_trades_all[stars][trade_type][symbol] = {'count': 0, 'total_usd_size': 0}
        stars_count_trades_all[stars][trade_type][symbol]['count'] += 1
        stars_count_trades_all[stars][trade_type][symbol]['total_usd_size'] += usd_size

    # Trades since program start
    # Total trades and USD size since program start
    total_trades_all = len(trades_data)
    total_usd_size_all = sum(trade[3] if trade[2] == '📈 ' else -trade[3] for trade in trades_data)

    #Number of Long and short trades since program start and the difference between them
    trades_long_count_all = sum(1 for trade in trades_data if trade[2] == '📈 ')
    trades_short_count_all = sum(1 for trade in trades_data if trade[2] == '📉 ')
    trades_difference_count_all = trades_long_count_all - trades_short_count_all

    # Percentage of Long and short trades since program start
    trades_long_count_percentage_all = (trades_long_count_all / total_trades_all) * 100 if total_trades_all > 0 else 0
    trades_short_count_percentage_all = (trades_short_count_all / total_trades_all) * 100 if total_trades_all > 0 else 0

    # Total USD size of Long and short trades since program start
    total_usd_size_long_all = sum(trade[3] for trade in trades_data if trade[2] == '📈 ')
    total_usd_size_short_all = sum(trade[3] for trade in trades_data if trade[2] == '📉 ')

    # Difference between Long and short trades since program start
    usd_size_difference_all = total_usd_size_long_all - total_usd_size_short_all
    total_usd_size_trades_all = total_usd_size_long_all + total_usd_size_short_all 

    # Percentage of Long and short trades since program start
    total_usd_size_long_percentage_all = (total_usd_size_long_all / total_usd_size_trades_all) * 100 if total_usd_size_trades_all > 0 else 0
    total_usd_size_short_percentage_all = (total_usd_size_short_all / total_usd_size_trades_all) * 100 if total_usd_size_trades_all > 0 else 0

    # Average trades and USD size per minute since program start
    avg_trades_per_minute_all = (total_trades_all * 60) / total_elapsed_time if total_elapsed_time > 0 else 0
    avg_usd_size_per_minute_all = (total_usd_size_all * 60) / total_elapsed_time if total_elapsed_time > 0 else 0


    # Determine the color of the average usd_size
    usd_size_color = 'green' if avg_usd_size_per_minute_1 > 0 else 'red'
    usd_size_color_all = 'green' if avg_usd_size_per_minute_all > 0 else 'red'

    # Determine the color based on the difference
    difference_color = 'green' if usd_size_difference_1 > 0 else 'red'
    difference_color_all = 'green' if usd_size_difference_all > 0 else 'red'

    # Prepare metrics dictionary
    metrics = {
        # Times
        'average_interval_1': average_interval_1,
        'average_interval_2': average_interval_2,
        'average_interval_3': average_interval_3,
        'total_elapsed_time': total_elapsed_time,
        'usd_size_color': usd_size_color,
        'difference_color': difference_color,
        # Trades within interval 1
        'total_trades_in_interval_1': total_trades_in_interval_1,
        'total_usd_size_in_interval_1': total_usd_size_in_interval_1,
        'trades_long_count_1': trades_long_count_1,
        'trades_short_count_1': trades_short_count_1,
        'trades_difference_count_1': trades_difference_count_1,
        'trades_long_count_percentage_1': trades_long_count_percentage_1,
        'trades_short_count_percentage_1': trades_short_count_percentage_1,
        'total_usd_size_long_1': total_usd_size_long_1,
        'total_usd_size_short_1': total_usd_size_short_1,
        'total_usd_size_long_percentage_1': total_usd_size_long_percentage_1,
        'total_usd_size_short_percentage_1': total_usd_size_short_percentage_1,
        'usd_size_difference_1': usd_size_difference_1,
        'avg_trades_per_minute_1': avg_trades_per_minute_1,
        'avg_usd_size_per_minute_1': avg_usd_size_per_minute_1,
        'stars_count_trades_1': stars_count_trades_1,
        'total_usd_size_trades_1': total_usd_size_trades_1,
        # Trades within interval 2
        'total_trades_in_interval_2': total_trades_in_interval_2,
        'total_usd_size_in_interval_2': total_usd_size_in_interval_2,
        'trades_long_count_2': trades_long_count_2,
        'trades_short_count_2': trades_short_count_2,
        'trades_difference_count_2': trades_difference_count_2,
        'trades_long_count_percentage_2': trades_long_count_percentage_2,
        'trades_short_count_percentage_2': trades_short_count_percentage_2,
        'total_usd_size_long_2': total_usd_size_long_2,
        'total_usd_size_short_2': total_usd_size_short_2,
        'total_usd_size_long_percentage_2': total_usd_size_long_percentage_2,
        'total_usd_size_short_percentage_2': total_usd_size_short_percentage_2,
        'usd_size_difference_2': usd_size_difference_2,
        'avg_trades_per_minute_2': avg_trades_per_minute_2,
        'avg_usd_size_per_minute_2': avg_usd_size_per_minute_2,
        'stars_count_trades_2': stars_count_trades_2,
        'total_usd_size_trades_2': total_usd_size_trades_2,
        # Trades within interval 3
        'total_trades_in_interval_3': total_trades_in_interval_3,
        'total_usd_size_in_interval_3': total_usd_size_in_interval_3,
        'trades_long_count_3': trades_long_count_3,
        'trades_short_count_3': trades_short_count_3,
        'trades_difference_count_3': trades_difference_count_3,
        'trades_long_count_percentage_3': trades_long_count_percentage_3,
        'trades_short_count_percentage_3': trades_short_count_percentage_3,
        'total_usd_size_long_3': total_usd_size_long_3,
        'total_usd_size_short_3': total_usd_size_short_3,
        'total_usd_size_long_percentage_3': total_usd_size_long_percentage_3,
        'total_usd_size_short_percentage_3': total_usd_size_short_percentage_3,
        'usd_size_difference_3': usd_size_difference_3,
        'avg_trades_per_minute_3': avg_trades_per_minute_3,
        'avg_usd_size_per_minute_3': avg_usd_size_per_minute_3,
        'stars_count_trades_3': stars_count_trades_3,
        'total_usd_size_trades_3': total_usd_size_trades_3,



        # Cumulative Trades
        'total_trades_all': total_trades_all,
        'total_usd_size_all': total_usd_size_all,
        'trades_long_count_all': trades_long_count_all,
        'trades_short_count_all': trades_short_count_all,
        'trades_difference_count_all': trades_difference_count_all,
        'total_usd_size_long_all': total_usd_size_long_all,
        'total_usd_size_short_all': total_usd_size_short_all,
        'trades_long_count_percentage_all': trades_long_count_percentage_all,
        'trades_short_count_percentage_all': trades_short_count_percentage_all,
        'total_usd_size_long_percentage_all': total_usd_size_long_percentage_all,
        'total_usd_size_short_percentage_all': total_usd_size_short_percentage_all,
        'usd_size_difference_all': usd_size_difference_all,
        'avg_trades_per_minute_all': avg_trades_per_minute_all,
        'avg_usd_size_per_minute_all': avg_usd_size_per_minute_all,
        'usd_size_color_all': usd_size_color_all,
        'difference_color_all': difference_color_all,
        'stars_count_trades_all': stars_count_trades_all,
        'total_usd_size_trades_all': total_usd_size_trades_all,

    }

    return metrics



class TradeTrawlerApp(App):
    """Textual Application for displaying trade data with detailed metrics and scrollable layout."""

    def __init__(self, metrics, start_time, trade_threshold):
        super().__init__()
        self.metrics = metrics
        self.start_time = start_time
        self.trade_threshold = trade_threshold
        self.start_timestamp = datetime.now().timestamp() * 1000  # Start time in milliseconds

    def compose(self) -> ComposeResult:
        """Compose the UI layout by adding header and footer."""
        yield Header()
        yield Footer()

    async def on_mount(self) -> None:
        """Add the grid layout and other widgets after the app is mounted."""
        # Create a grid layout
        self.grid = Grid()

        # Set the grid dimensions
        self.grid.styles.grid_template_columns = "1fr 1fr"  # Two equal columns
        self.grid.styles.grid_template_rows = "1fr 1fr"  # Two equal rows
        self.grid.styles.gap = "2"  # Set the gap between the elements in the grid

        # Mount the grid to the application
        await self.mount(self.grid)

        # Scrollable content for the left and right areas
        self.scroll_left = Static(expand=True)
        self.scroll_right = Static(expand=True)

        # Mount scrollable panels to the grid layout
        await self.grid.mount(self.scroll_left)
        await self.grid.mount(self.scroll_right)

        # Start a background task to periodically update the metrics and UI
        self.set_interval(1, self.update_metrics_and_ui)

    async def update_metrics_and_ui(self) -> None:
        """Periodically update metrics and refresh the UI."""
        # Recalculate metrics (assuming trades_data is being updated by other WebSocket streams)
        self.metrics = calculate_metrics(
            trades_data,
            self.trade_threshold,
            self.metrics['average_interval_1'],
            self.metrics['average_interval_2'],
            self.metrics['average_interval_3'],
            self.start_timestamp
        )

        # Update the content of both panels
        self.update_left(self.scroll_left)
        self.update_right(self.scroll_right)

    def update_left(self, scroll_view: Static):
        """Updates the left panel with interval 1 and 2 metrics."""
        interval_1_panel = self.create_interval_panels(1)
        interval_2_panel = self.create_interval_panels(2)

        # Pass updated content to the scrollable view
        scroll_view.update(interval_1_panel)
        scroll_view.update(interval_2_panel)

    def update_right(self, scroll_view: Static):
        """Updates the right panel with interval 3 metrics and cumulative metrics."""
        interval_3_panel = self.create_interval_panels(3)
        total_panel = self.create_total_panel("Cumulative Trades", self.metrics)

        # Pass updated content to the scrollable view
        scroll_view.update(interval_3_panel)
        scroll_view.update(total_panel)

    def create_interval_panels(self, interval_num: int) -> Group:
        """Creates panels for all metrics within a given interval."""
        panels = []
        interval_key_prefix = f"interval_{interval_num}"

        panels.append(self.create_single_panel(
            f"Total Trades in Interval {interval_num}", 
            f"{self.metrics[f'total_trades_in_{interval_key_prefix}']} Trades"
        ))
        panels.append(self.create_single_panel(
            f"Long Trades in Interval {interval_num}", 
            f"{self.metrics[f'trades_long_count_{interval_num}']} ({self.metrics[f'trades_long_count_percentage_{interval_num}']:.2f}%)"
        ))
        panels.append(self.create_single_panel(
            f"Short Trades in Interval {interval_num}", 
            f"{self.metrics[f'trades_short_count_{interval_num}']} ({self.metrics[f'trades_short_count_percentage_{interval_num}']:.2f}%)"
        ))
        panels.append(self.create_single_panel(
            f"USD Size in Interval {interval_num}", 
            f"{self.metrics[f'total_usd_size_in_{interval_key_prefix}']:,.2f}$"
        ))
        panels.append(self.create_single_panel(
            f"Long USD Size in Interval {interval_num}", 
            f"{self.metrics[f'total_usd_size_long_{interval_num}']:,.2f}$ ({self.metrics[f'total_usd_size_long_percentage_{interval_num}']:.2f}%)"
        ))
        panels.append(self.create_single_panel(
            f"Short USD Size in Interval {interval_num}", 
            f"{self.metrics[f'total_usd_size_short_{interval_num}']:,.2f}$ ({self.metrics[f'total_usd_size_short_percentage_{interval_num}']:.2f}%)"
        ))
        panels.append(self.create_single_panel(
            f"USD Difference in Interval {interval_num}", 
            f"{self.format_value(self.metrics[f'usd_size_difference_{interval_num}'])}"
        ))
        panels.append(self.create_single_panel(
            f"Average Trades per Minute in Interval {interval_num}", 
            f"{self.metrics[f'avg_trades_per_minute_{interval_num}']:,.2f}"
        ))
        panels.append(self.create_single_panel(
            f"Average USD per Minute in Interval {interval_num}", 
            f"{self.format_value(self.metrics[f'avg_usd_size_per_minute_{interval_num}'])}$"
        ))

        return Group(*panels)

    def create_single_panel(self, title: str, content: str) -> Panel:
        """Creates a single panel with title and content."""
        return Panel(Text(content), title=title, border_style="green")

    def create_total_panel(self, title: str, metrics: dict) -> Panel:
        """Creates a panel for displaying cumulative trade metrics since the start."""
        total_trades = metrics['total_trades_all']
        long_trades = metrics['trades_long_count_all']
        short_trades = metrics['trades_short_count_all']
        usd_size_total = metrics['total_usd_size_all']
        usd_size_long = metrics['total_usd_size_long_all']
        usd_size_short = metrics['total_usd_size_short_all']
        usd_size_difference = metrics['usd_size_difference_all']
        avg_trades_per_minute = metrics['avg_trades_per_minute_all']
        avg_usd_size_per_minute = metrics['avg_usd_size_per_minute_all']

        panel_content = (
            f"🎣 Total Trades since start: {total_trades}\n"
            f"📈 Long Trades: {long_trades} "
            f"({metrics['trades_long_count_percentage_all']:.2f}%)\n"
            f"📉 Short Trades: {short_trades} "
            f"({metrics['trades_short_count_percentage_all']:.2f}%)\n"
            f"💵 Total USD Size: {usd_size_total:,.2f}$\n"
            f"📈 Long USD Size: {usd_size_long:,.2f}$ "
            f"({metrics['total_usd_size_long_percentage_all']:.2f}%)\n"
            f"📉 Short USD Size: {usd_size_short:,.2f}$ "
            f"({metrics['total_usd_size_short_percentage_all']:.2f}%)\n"
            f"🔰 USD Difference: {self.format_value(usd_size_difference)}\n"
            f"📊 Avg. Trades per Minute: {avg_trades_per_minute:,.2f}\n"
            f"📊 Avg. USD per Minute: {self.format_value(avg_usd_size_per_minute)}$\n"
        )

        return Panel(Text(panel_content), title=title, border_style="blue" if usd_size_difference > 0 else "red")


    def format_value(self, value):
        """Helper method to apply color formatting based on positive/negative values."""
        return f"[green]{value:,.2f}[/green]" if value > 0 else f"[red]{value:,.2f}[/red]"


# Process Trade Function for Normal Trades
async def process_trade(symbol, price, quantity, trade_time, is_buyer_maker):
    global trade_threshold
    usd_size = price * quantity
    symbol = symbol.upper().replace('USDT', '')
    if symbol == 'XBT':
        symbol = 'BTC'
    if usd_size >= trade_threshold:
        trade_type = '📉 ' if is_buyer_maker else '📈 '
        used_trade_time = format_trade_time(trade_time)
        collect_trade_data(symbol, used_trade_time, trade_type, usd_size, trade_time)

# Binance Trade Stream
async def binance_trade_stream(uri, symbol):
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
                    await process_trade(symbol, price, quantity, trade_time, is_buyer_maker)
        except ConnectionClosed:
            console.print("No Connection📡❌🛰️ (Binance Trade)")
            await asyncio.sleep(5)
        except Exception as e:
            console.print(f"[red]An error occurred in binance_trade_stream: {e}[/red]")
            await asyncio.sleep(5)

# Coinbase Trade Stream
async def coinbase_trade_stream(uri):
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
                    if data['type'] == 'ticker':
                        product_id = data['product_id']
                        symbol = product_id.split('-')[0].upper()
                        price = float(data['price'])
                        quantity = float(data['last_size'])
                        trade_time = int(datetime.fromisoformat(data['time'].replace('Z', '+00:00')).timestamp() * 1000)
                        is_buyer_maker = data['side'] == 'sell'
                        await process_trade(symbol, price, quantity, trade_time, is_buyer_maker)
        except ConnectionClosed:
            console.print("No Connection📡❌🛰️ (Coinbase)")
            await asyncio.sleep(5)
        except Exception as e:
            console.print(f"[red]An error occurred in coinbase_trade_stream: {e}[/red]")
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
                        for trade in trades:
                            price = float(trade[0])
                            quantity = float(trade[1])
                            trade_time = int(float(trade[2]) * 1000)
                            side = trade[3]  # 'b' or 's'
                            is_buyer_maker = True if side == 's' else False
                            await process_trade(symbol, price, quantity, trade_time, is_buyer_maker)
        except ConnectionClosed:
            console.print("No Connection📡❌🛰️ (Kraken)")
            await asyncio.sleep(5)
        except Exception as e:
            console.print(f"[red]An error occurred in kraken_trade_stream: {e}[/red]")
            await asyncio.sleep(5)

# Bitfinex Trade Stream
async def bitfinex_trade_stream(uri):
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
                        if data[1] == 'tu':
                            # Trade executed update
                            trade_info = data[2]
                            symbol = chan_id_symbol_map.get(chan_id, 'UNKNOWN').lstrip('t')
                            if symbol == 'BTC':
                                symbol = 'BTC'
                            price = float(trade_info[3])
                            quantity = abs(float(trade_info[2]))
                            is_buyer_maker = True if float(trade_info[2]) < 0 else False
                            trade_time = int(trade_info[1])
                            await process_trade(symbol, price, quantity, trade_time, is_buyer_maker)
        except ConnectionClosed:
            console.print("No Connection📡❌🛰️ (Bitfinex)")
            await asyncio.sleep(5)
        except Exception as e:
            console.print(f"[red]An error occurred in bitfinex_trade_stream: {e}[/red]")
            await asyncio.sleep(5)




def select_symbols():
    """
    Allows the user to select which symbols to include in the query.
    """
    title = ' Trade Trawler'

    # Färbe den ASCII-Text blau-weiß (blau als Textfarbe, weiß als Hintergrund)
    ascii_title = '🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏\n' + pyfiglet.figlet_format(title) + '🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏'
    print(colored(ascii_title, 'blue', 'on_white', attrs=['bold']))

    # Verwende pyfiglet, um den Titel in ASCII-Kunstform darzustellen
    print("""📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉
☁️  ☁️  ☁️  ☁️  ☁️  ☁️  ☁️  ☁️  ☁️  ☁️  ☁️  ☁️  ☁️  ☁️  ☁️  ☁️  ☁️  ☁️  ☀️
  
                     💭        💭        💭
                      💭  💭    💭  💭    💭  💭
                      ||   💭   ||   💭   ||   💭
                     _||___||___||___||___||___||_
            🐳______|   o    o    o   o      🎛️🪟|_______
            ||  ⚓\\_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-/
🌊    🌊    ##     \\o»»»o»»»»o»»»»o»»»»o»»»»o»»»»o»»»o/   🌊    🌊    🌊
~~~~~~~~~~~####~~~~~\\________________________________/~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~####🐟~~~🐟~~~~🐟~~~~~~🐟~~🐟~~~~🐠~~~~🐟~~~~~~~~~~~~~~~~~🐠~~~~
~~~~~~~~~~##🐠##🐟~~~~~~~~~🐟🐟~~~~🐠~~~~🐟~~~~🐟~~~~🦑~~~~🐟~~~~🐟~~~~~~~~
~~~~~~~~~~~###🦑~~~~~🐳~~~~🐟~~~~🦑~~~~~~~~~~~~~~🐟~~~~~🐳~~~~🐠~~~~🐟~~~~~~
📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📈📉📈📉📈📉📈📉📈📉📈📉📈📉📈📉
         """)
    print("🚢Trade Trawler sets sail and gets ready to fish🐟🐠🦑🐳")
    
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
            selected_symbols = symbols  # Verwende alle Symbole
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
        selected_symbols = list(name_map.keys())  # Verwende alle Symbole, wenn keine ausgewählt wurden

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

    # Symbol selection
    select_symbols()

    # Prompt user for threshold values
    trade_threshold = float(input("🔧Please enter the threshold value for 'usd_size' on trades in $: "))
    average_interval_1 = int(input("🔧Please enter the first interval over which to calculate averages in seconds: "))
    average_interval_2 = int(input("🔧Please enter the second interval over which to calculate averages in seconds: "))
    average_interval_3 = int(input("🔧Please enter the third interval over which to calculate averages in seconds: "))

    interval = 0.2  # Set interval to 1 second

    # Capture the start time in a readable format
    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    start_timestamp = datetime.now().timestamp() * 1000  # in milliseconds

    # Start WebSocket tasks
    for symbol in selected_symbols:
        stream_url = f"{websocket_url_base_binance}{symbol}@aggTrade"
        asyncio.create_task(binance_trade_stream(stream_url, symbol))

    asyncio.create_task(coinbase_trade_stream(websocket_url_base_coinbase))
    if kraken_symbols_selected:
        asyncio.create_task(kraken_trade_stream(websocket_url_kraken))

    if bitfinex_symbols_selected:
        asyncio.create_task(bitfinex_trade_stream(websocket_url_bitfinex))

    # Periodically update the metrics and refresh the app
    metrics = calculate_metrics(
        trades_data,
        trade_threshold,
        average_interval_1,
        average_interval_2,
        average_interval_3,
        start_timestamp
    )

    # Launch the textual app asynchronously
    app = TradeTrawlerApp(metrics, start_time, trade_threshold)
    
    # Use run_async() to run the app without blocking the event loop
    await app.run_async()

if __name__ == "__main__":
    try:
        print("⚙️ Program is starting ⚙️")
        asyncio.run(main())  # Main entry point for running the program
        print("✅⚙️ Program is done ⚙✅️")
    except Exception as e:
        console.print(f"[red]An error occurred in the main program: {e}[/red]")
        import traceback
        traceback.print_exc()
