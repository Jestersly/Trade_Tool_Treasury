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
All_symbols = False

websocket_url_base_binance = 'wss://fstream.binance.com/ws/'
websocket_url_base_coinbase = 'wss://ws-feed.exchange.coinbase.com'
websocket_url_liq = 'wss://fstream.binance.com/ws/!forceOrder@arr'
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
liquidations_data = []

# Thresholds for printing output
trade_threshold = 0
liquidation_threshold = 0

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

def collect_liquidation_data(symbol, used_trade_time, liquidation_type, usd_size, timestamp):
    """
    Collects liquidation data and appends it to the liquidations_data list.
    """
    liquidations_data.append([symbol, used_trade_time, liquidation_type, usd_size, timestamp])

def get_stars(usd_size):
    if usd_size >= 500000000:
        return '❓💰🃏💰❓'
    elif usd_size >= 250000000:
        return '💸🌈🦄🌈💸'
    elif usd_size >= 120000000:
        return '  🐳🐳🐳  '
    elif usd_size >= 80000000:
        return '   🐳🐳   '
    elif usd_size >= 50000000:
        return '    🐳    '
    elif usd_size >= 25000000:
        return '  🦈🦈🦈  '
    elif usd_size >= 12400000:
        return '   🦈🦈   '
    elif usd_size >= 5120000:
        return '    🦈    '
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

def get_liq_stars(usd_size):
    if usd_size > 40000000:
        return '🌊💰🤿💰🌊'
    elif usd_size > 20000000:
        return '💸🌊🤿🌊💸'
    elif usd_size > 10000000:
        return '  🌊🤿🌊  '
    elif usd_size > 5000000:
        return '    🤿    '
    elif usd_size > 2480000:
        return '  🌊🌊🌊  '
    elif usd_size > 1240000:
        return '   🌊🌊   '
    elif usd_size > 512000:
        return '    🌊    '
    elif usd_size > 256000:
        return '💦💦💦💦💦'
    elif usd_size > 128000:
        return ' 💦💦💦💦 '
    elif usd_size > 64000:
        return '  💦💦💦  '
    elif usd_size > 32000:
        return '   💦💦   '
    elif usd_size > 16000:
        return '    💦    '
    elif usd_size > 8000:
        return '  💧💧💧  '
    elif usd_size > 4000:
        return '   💧💧   '
    elif usd_size > 2000:
        return '    💧    '
    else:
        return '          '

def calculate_metrics(trades_data, liquidations_data, trade_threshold, liquidation_threshold, average_interval, start_timestamp):
    current_time = datetime.now().timestamp() * 1000  # Current time in milliseconds

    # Total elapsed time since program start in seconds
    total_elapsed_time = (current_time - start_timestamp) / 1000

    # Filter data to last average_interval seconds
    filtered_trades_data = [trade for trade in trades_data if current_time - trade[4] <= average_interval * 1000]
    filtered_liquidations_data = [liq for liq in liquidations_data if current_time - liq[4] <= average_interval * 1000]

    # --- Calculations within the average_interval ---

    # Trades within the interval
    total_trades_in_interval = len(filtered_trades_data)
    total_usd_size_in_interval = sum(trade[3] if trade[2] == '📈 ' else -trade[3] for trade in filtered_trades_data)

    trades_long_count = sum(1 for trade in filtered_trades_data if trade[2] == '📈 ')
    trades_short_count = sum(1 for trade in filtered_trades_data if trade[2] == '📉 ')

    total_usd_size_long = sum(trade[3] for trade in filtered_trades_data if trade[2] == '📈 ')
    total_usd_size_short = sum(trade[3] for trade in filtered_trades_data if trade[2] == '📉 ')

    usd_size_difference = total_usd_size_long - total_usd_size_short

    # Averages per minute
    avg_trades_per_minute = (total_trades_in_interval * 60) / average_interval if average_interval > 0 else 0
    avg_usd_size_per_minute = (total_usd_size_in_interval * 60) / average_interval if average_interval > 0 else 0

    # Liquidations within the interval
    total_liquidations_in_interval = len(filtered_liquidations_data)
    total_usd_size_liq_in_interval = sum(liq[3] if liq[2] == '📈 ' else -liq[3] for liq in filtered_liquidations_data)

    liquidations_long_count = sum(1 for liq in filtered_liquidations_data if liq[2] == '📈 ')
    liquidations_short_count = sum(1 for liq in filtered_liquidations_data if liq[2] == '📉 ')

    total_usd_size_long_liq = sum(liq[3] for liq in filtered_liquidations_data if liq[2] == '📈 ')
    total_usd_size_short_liq = sum(liq[3] for liq in filtered_liquidations_data if liq[2] == '📉 ')

    usd_size_difference_liq = total_usd_size_long_liq - total_usd_size_short_liq

    avg_liquidations_per_minute = (total_liquidations_in_interval * 60) / average_interval if average_interval > 0 else 0
    avg_usd_size_per_minute_liq = (total_usd_size_liq_in_interval * 60) / average_interval if average_interval > 0 else 0

    # Count stars for trades within the interval
    stars_count_trades = {}
    for trade in filtered_trades_data:
        usd_size = trade[3]
        stars = get_stars(usd_size)
        trade_type = trade[2]
        symbol = trade[0]
        if stars not in stars_count_trades:
            stars_count_trades[stars] = {}
        if trade_type not in stars_count_trades[stars]:
            stars_count_trades[stars][trade_type] = {}
        if symbol not in stars_count_trades[stars][trade_type]:
            stars_count_trades[stars][trade_type][symbol] = {'count': 0, 'total_usd_size': 0}
        stars_count_trades[stars][trade_type][symbol]['count'] += 1
        stars_count_trades[stars][trade_type][symbol]['total_usd_size'] += usd_size

    # Count stars for liquidations within the interval
    stars_count_liquidations = {}
    for liquidation in filtered_liquidations_data:
        usd_size = liquidation[3]
        stars = get_liq_stars(usd_size)
        liquidation_type = liquidation[2]
        symbol = liquidation[0]
        if stars not in stars_count_liquidations:
            stars_count_liquidations[stars] = {}
        if liquidation_type not in stars_count_liquidations[stars]:
            stars_count_liquidations[stars][liquidation_type] = {}
        if symbol not in stars_count_liquidations[stars][liquidation_type]:
            stars_count_liquidations[stars][liquidation_type][symbol] = {'count': 0, 'total_usd_size': 0}
        stars_count_liquidations[stars][liquidation_type][symbol]['count'] += 1
        stars_count_liquidations[stars][liquidation_type][symbol]['total_usd_size'] += usd_size

    # --- Cumulative calculations since program start ---
        # Count stars for trades since the program started
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


    # Count stars for liquidations since the program started
    stars_count_liquidations_all = {}
    for liquidation in liquidations_data:
        usd_size = liquidation[3]
        stars = get_liq_stars(usd_size)
        liquidation_type = liquidation[2]
        symbol = liquidation[0]
        if stars not in stars_count_liquidations_all:
            stars_count_liquidations_all[stars] = {}
        if liquidation_type not in stars_count_liquidations_all[stars]:
            stars_count_liquidations_all[stars][liquidation_type] = {}
        if symbol not in stars_count_liquidations_all[stars][liquidation_type]:
            stars_count_liquidations_all[stars][liquidation_type][symbol] = {'count': 0, 'total_usd_size': 0}
        stars_count_liquidations_all[stars][liquidation_type][symbol]['count'] += 1
        stars_count_liquidations_all[stars][liquidation_type][symbol]['total_usd_size'] += usd_size


    # Trades since program start
    total_trades_all = len(trades_data)
    total_usd_size_all = sum(trade[3] if trade[2] == '📈 ' else -trade[3] for trade in trades_data)

    trades_long_count_all = sum(1 for trade in trades_data if trade[2] == '📈 ')
    trades_short_count_all = sum(1 for trade in trades_data if trade[2] == '📉 ')

    total_usd_size_long_all = sum(trade[3] for trade in trades_data if trade[2] == '📈 ')
    total_usd_size_short_all = sum(trade[3] for trade in trades_data if trade[2] == '📉 ')

    usd_size_difference_all = total_usd_size_long_all - total_usd_size_short_all

    # Average trades and USD size per minute since program start
    avg_trades_per_minute_all = (total_trades_all * 60) / total_elapsed_time if total_elapsed_time > 0 else 0
    avg_usd_size_per_minute_all = (total_usd_size_all * 60) / total_elapsed_time if total_elapsed_time > 0 else 0

    # Liquidations since program start
    total_liquidations_all = len(liquidations_data)
    total_usd_size_liq_all = sum(liq[3] if liq[2] == '📈 ' else -liq[3] for liq in liquidations_data)

    liquidations_long_count_all = sum(1 for liq in liquidations_data if liq[2] == '📈 ')
    liquidations_short_count_all = sum(1 for liq in liquidations_data if liq[2] == '📉 ')

    total_usd_size_long_liq_all = sum(liq[3] for liq in liquidations_data if liq[2] == '📈 ')
    total_usd_size_short_liq_all = sum(liq[3] for liq in liquidations_data if liq[2] == '📉 ')

    usd_size_difference_liq_all = total_usd_size_long_liq_all - total_usd_size_short_liq_all

    avg_liquidations_per_minute_all = (total_liquidations_all * 60) / total_elapsed_time if total_elapsed_time > 0 else 0
    avg_usd_size_per_minute_liq_all = (total_usd_size_liq_all * 60) / total_elapsed_time if total_elapsed_time > 0 else 0

    # Determine the color of the average usd_size
    usd_size_color = 'green' if avg_usd_size_per_minute > 0 else 'red'
    usd_size_color_liq = 'green' if avg_usd_size_per_minute_liq > 0 else 'red'
    usd_size_color_all = 'green' if avg_usd_size_per_minute_all > 0 else 'red'
    usd_size_color_liq_all = 'green' if avg_usd_size_per_minute_liq_all > 0 else 'red'

    # Determine the color based on the difference
    difference_color = 'green' if usd_size_difference > 0 else 'red'
    difference_color_liq = 'green' if usd_size_difference_liq > 0 else 'red'
    difference_color_all = 'green' if usd_size_difference_all > 0 else 'red'
    difference_color_liq_all = 'green' if usd_size_difference_liq_all > 0 else 'red'

    # Prepare metrics dictionary
    metrics = {
        # Times
        'average_interval': average_interval,
        'total_elapsed_time': total_elapsed_time,
        # Trades within interval
        'total_trades_in_interval': total_trades_in_interval,
        'total_usd_size_in_interval': total_usd_size_in_interval,
        'trades_long_count': trades_long_count,
        'trades_short_count': trades_short_count,
        'total_usd_size_long': total_usd_size_long,
        'total_usd_size_short': total_usd_size_short,
        'usd_size_difference': usd_size_difference,
        'avg_trades_per_minute': avg_trades_per_minute,
        'avg_usd_size_per_minute': avg_usd_size_per_minute,
        'usd_size_color': usd_size_color,
        'difference_color': difference_color,
        'stars_count_trades': stars_count_trades,
        # Liquidations within interval
        'total_liquidations_in_interval': total_liquidations_in_interval,
        'total_usd_size_liq_in_interval': total_usd_size_liq_in_interval,
        'liquidations_long_count': liquidations_long_count,
        'liquidations_short_count': liquidations_short_count,
        'total_usd_size_long_liq': total_usd_size_long_liq,
        'total_usd_size_short_liq': total_usd_size_short_liq,
        'usd_size_difference_liq': usd_size_difference_liq,
        'avg_liquidations_per_minute': avg_liquidations_per_minute,
        'avg_usd_size_per_minute_liq': avg_usd_size_per_minute_liq,
        'usd_size_color_liq': usd_size_color_liq,
        'difference_color_liq': difference_color_liq,
        'stars_count_liquidations': stars_count_liquidations,
        # Cumulative Trades
        'total_trades_all': total_trades_all,
        'total_usd_size_all': total_usd_size_all,
        'trades_long_count_all': trades_long_count_all,
        'trades_short_count_all': trades_short_count_all,
        'total_usd_size_long_all': total_usd_size_long_all,
        'total_usd_size_short_all': total_usd_size_short_all,
        'usd_size_difference_all': usd_size_difference_all,
        'avg_trades_per_minute_all': avg_trades_per_minute_all,
        'avg_usd_size_per_minute_all': avg_usd_size_per_minute_all,
        'usd_size_color_all': usd_size_color_all,
        'difference_color_all': difference_color_all,
        'stars_count_trades_all': stars_count_trades_all,
        # Cumulative Liquidations
        'total_liquidations_all': total_liquidations_all,
        'total_usd_size_liq_all': total_usd_size_liq_all,
        'liquidations_long_count_all': liquidations_long_count_all,
        'liquidations_short_count_all': liquidations_short_count_all,
        'total_usd_size_long_liq_all': total_usd_size_long_liq_all,
        'total_usd_size_short_liq_all': total_usd_size_short_liq_all,
        'usd_size_difference_liq_all': usd_size_difference_liq_all,
        'avg_liquidations_per_minute_all': avg_liquidations_per_minute_all,
        'avg_usd_size_per_minute_liq_all': avg_usd_size_per_minute_liq_all,
        'usd_size_color_liq_all': usd_size_color_liq_all,
        'difference_color_liq_all': difference_color_liq_all,
        'stars_count_liquidations_all': stars_count_liquidations_all
    }

    return metrics


def create_output(layout, metrics, start_time, trade_threshold, liquidation_threshold):
    """
    Creates the output layout using Rich components.
    """
    try:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        time_difference = calculate_time_difference(start_time, current_time)

        # Unpack metrics for easier access
        average_interval = metrics['average_interval']

        # Trades within interval
        total_trades_in_interval = metrics['total_trades_in_interval']
        trades_long_count = metrics['trades_long_count']
        trades_short_count = metrics['trades_short_count']
        total_usd_size_long = metrics['total_usd_size_long']
        total_usd_size_short = metrics['total_usd_size_short']
        usd_size_difference = metrics['usd_size_difference']
        avg_trades_per_minute = metrics['avg_trades_per_minute']
        avg_usd_size_per_minute = metrics['avg_usd_size_per_minute']
        stars_count_trades = metrics['stars_count_trades']

        # Liquidations within interval
        total_liquidations_in_interval = metrics['total_liquidations_in_interval']
        liquidations_long_count = metrics['liquidations_long_count']
        liquidations_short_count = metrics['liquidations_short_count']
        total_usd_size_long_liq = metrics['total_usd_size_long_liq']
        total_usd_size_short_liq = metrics['total_usd_size_short_liq']
        usd_size_difference_liq = metrics['usd_size_difference_liq']
        avg_liquidations_per_minute = metrics['avg_liquidations_per_minute']
        avg_usd_size_per_minute_liq = metrics['avg_usd_size_per_minute_liq']
        stars_count_liquidations = metrics['stars_count_liquidations']

        # Cumulative Trades
        total_trades_all = metrics['total_trades_all']
        trades_long_count_all = metrics['trades_long_count_all']
        trades_short_count_all = metrics['trades_short_count_all']
        total_usd_size_long_all = metrics['total_usd_size_long_all']
        total_usd_size_short_all = metrics['total_usd_size_short_all']
        usd_size_difference_all = metrics['usd_size_difference_all']
        avg_trades_per_minute_all = metrics['avg_trades_per_minute_all']
        avg_usd_size_per_minute_all = metrics['avg_usd_size_per_minute_all']
        stars_count_trades_all = metrics['stars_count_trades_all']

        # Cumulative Liquidations
        total_liquidations_all = metrics['total_liquidations_all']
        liquidations_long_count_all = metrics['liquidations_long_count_all']
        liquidations_short_count_all = metrics['liquidations_short_count_all']
        total_usd_size_long_liq_all = metrics['total_usd_size_long_liq_all']
        total_usd_size_short_liq_all = metrics['total_usd_size_short_liq_all']
        usd_size_difference_liq_all = metrics['usd_size_difference_liq_all']
        avg_liquidations_per_minute_all = metrics['avg_liquidations_per_minute_all']
        avg_usd_size_per_minute_liq_all = metrics['avg_usd_size_per_minute_liq_all']
        stars_count_liquidations_all = metrics['stars_count_liquidations_all']

        # Using formatted symbols
        # 
        if All_symbols:
            symbols_display = '🃏ALL🃏'
        else:
            symbols_display = ', '.join(selected_symbols_formatted)


        # Create the header content as a Text object with wrapping

        header_content = Text(justify="center", no_wrap=False)
        header_content.append(f"📊 Selected Symbols:\n", style="bold yellow")
        header_content.append(f"{symbols_display}\n", style="bold yellow")
        header_content.append(f"🌊 Liquidation Threshold at  {liquidation_threshold}$\n")
        header_content.append(f"🎣 Trade Threshold at        {trade_threshold}$\n")
        header_content.append(f"📅 {start_time} »» 🕰️{current_time}\n")
        header_content.append(f"")
        # Create the header Panel with wrapping enabled
        header_panel = Panel(
            header_content,
            border_style="bold blue",
            title="Market Monitor",
            width=console.width
        )

        # Update the header layout
        layout["header"].update(header_panel)

        # Determine panel border colors
        trades_panel_border_color = "green" if usd_size_difference > 0 else "red"
        trades_panel_all_border_color = "green" if usd_size_difference_all > 0 else "red"
        liq_panel_border_color = "green" if usd_size_difference_liq > 0 else "red"
        liq_panel_all_border_color = "green" if usd_size_difference_liq_all > 0 else "red"

        # Left side: Trades
        trades_panel = Panel(
            f"🔹 🔷Trades Metrics for the last {average_interval} seconds:🔷 🔹\n"
            f"🎣Total Trades:                {total_trades_in_interval}\n"
            f"📈Total Count:                 {trades_long_count}\n"
            f"📉Total Count:                 {trades_short_count}\n"
            f"📊Avg. Trades per minute:      {avg_trades_per_minute:.2f}\n\n"
            f"📈Total USD Size:              {total_usd_size_long:,.2f}$\n"
            f"📉Total USD Size:              {total_usd_size_short:,.2f}$\n"
            f"🔰USD Spread:                  {usd_size_difference:,.2f}$\n"
            f"📊Avg. USD Size per minute:    {avg_usd_size_per_minute:,.2f}$",
            border_style=trades_panel_border_color,
            title="Trades (Interval)"
        )

        # Trades Sizes Table (Interval)
        trade_table_interval = Table(title="🔍 Trade Sizes (Interval)")
        trade_table_interval.add_column("Stars")
        trade_table_interval.add_column("Symbol")
        trade_table_interval.add_column("Type")
        trade_table_interval.add_column("Count")
        trade_table_interval.add_column("Total USD Size")

        # Collect and sort rows
        trade_rows_interval = []
        for stars in stars_count_trades:
            for trade_type in stars_count_trades[stars]:
                data = stars_count_trades[stars][trade_type]
                for symbol in data:
                    count = data[symbol]['count']
                    total_usd_size = data[symbol]['total_usd_size']
                    usd_size_color_type = 'green' if trade_type == '📈 ' else 'red'
                    formatted_symbol = name_map.get(symbol, symbol)
                    trade_rows_interval.append({
                        'stars': stars,
                        'symbol': formatted_symbol.strip(),
                        'trade_type': trade_type.strip(),
                        'count': str(count),
                        'total_usd_size': total_usd_size,
                        'style': usd_size_color_type
                    })

        # Sort the rows by 'Total USD Size' in descending order
        trade_rows_interval_sorted = sorted(trade_rows_interval, key=lambda x: x['total_usd_size'], reverse=True)

        # Add rows to the table
        for row in trade_rows_interval_sorted:
            trade_table_interval.add_row(
                row['stars'],
                row['symbol'],
                row['trade_type'],
                row['count'],
                f"{row['total_usd_size']:,.2f}$",
                style=row['style']
            )

        # Trades Sizes Table (Since Start)
        trades_panel_all = Panel(
            f"🔸 🔶Total Trades since start:🔶 🔸\n"
            f"🎣Total Trades:                 {total_trades_all}\n"
            f"📈Total Count:                  {trades_long_count_all}\n"
            f"📉Total Count:                  {trades_short_count_all}\n"
            f"📊Avg. Trades per minute:       {avg_trades_per_minute_all:.2f}\n\n"
            f"📈Total USD Size:               {total_usd_size_long_all:,.2f}$\n"
            f"📉Total USD Size:               {total_usd_size_short_all:,.2f}$\n"
            f"🔰Spread:                       {usd_size_difference_all:,.2f}$\n"
            f"📊Avg. USD Size per minute:     {avg_usd_size_per_minute_all:,.2f}$",
            border_style=trades_panel_all_border_color,
            title="Trades (Since Start)"
        )

        trade_table_all = Table(title="🔍 Trade Sizes (Since Start)")
        trade_table_all.add_column("Stars")
        trade_table_all.add_column("Symbol")
        trade_table_all.add_column("Type")
        trade_table_all.add_column("Count")
        trade_table_all.add_column("Total USD Size")

        # Collect and sort rows
        trade_rows_all = []
        for stars in stars_count_trades_all:
            for trade_type in stars_count_trades_all[stars]:
                data = stars_count_trades_all[stars][trade_type]
                for symbol in data:
                    count = data[symbol]['count']
                    total_usd_size = data[symbol]['total_usd_size']
                    usd_size_color_type = 'green' if trade_type == '📈 ' else 'red'
                    formatted_symbol = name_map.get(symbol, symbol)
                    trade_rows_all.append({
                        'stars': stars,
                        'symbol': formatted_symbol.strip(),
                        'trade_type': trade_type.strip(),
                        'count': str(count),
                        'total_usd_size': total_usd_size,
                        'style': usd_size_color_type
                    })

        # Sort the rows by 'Total USD Size' in descending order
        trade_rows_all_sorted = sorted(trade_rows_all, key=lambda x: x['total_usd_size'], reverse=True)

        # Add rows to the table
        for row in trade_rows_all_sorted:
            trade_table_all.add_row(
                row['stars'],
                row['symbol'],
                row['trade_type'],
                row['count'],
                f"{row['total_usd_size']:,.2f}$",
                style=row['style']
            )

        # Update left layout
        layout["left"].update(
            Group(
                trades_panel,
                trade_table_interval,
                trades_panel_all,
                trade_table_all
            )
        )

        # Right side: Liquidations
        liq_panel = Panel(
            f"🔹 🔷Liquidations Metrics for the last {average_interval} seconds:🔷 🔹\n"
            f"🌊Total Liquidations:           {total_liquidations_in_interval}\n"
            f"📈Total Count:                  {liquidations_long_count}\n"
            f"📉Total Count:                  {liquidations_short_count}\n"
            f"📊Avg. Liquidations per minute: {avg_liquidations_per_minute:.2f}\n\n"
            f"📈Total Size:                   {total_usd_size_long_liq:,.2f}$\n"
            f"📉Total Size:                   {total_usd_size_short_liq:,.2f}$\n"
            f"🔰Spread:                       {usd_size_difference_liq:,.2f}$\n"
            f"📊Avg. USD Size per minute:     {avg_usd_size_per_minute_liq:,.2f}$",
            border_style=liq_panel_border_color,
            title="Liquidations (Interval)"
        )

        # Liquidations Sizes Table (Interval)
        liq_table_interval = Table(title="🔍 Liquidation Sizes (Interval)")
        liq_table_interval.add_column("Stars")
        liq_table_interval.add_column("Symbol")
        liq_table_interval.add_column("Type")
        liq_table_interval.add_column("Count")
        liq_table_interval.add_column("Total USD Size")

        # Collect and sort rows
        liq_rows_interval = []
        for stars in stars_count_liquidations:
            for liquidation_type in stars_count_liquidations[stars]:
                data = stars_count_liquidations[stars][liquidation_type]
                for symbol in data:
                    count = data[symbol]['count']
                    total_usd_size = data[symbol]['total_usd_size']
                    usd_size_color_type_liq = 'green' if liquidation_type == '📈 ' else 'red'
                    formatted_symbol = name_map.get(symbol, symbol)
                    liq_rows_interval.append({
                        'stars': stars,
                        'symbol': formatted_symbol.strip(),
                        'liquidation_type': liquidation_type.strip(),
                        'count': str(count),
                        'total_usd_size': total_usd_size,
                        'style': usd_size_color_type_liq
                    })

        # Sort the rows by 'Total USD Size' in descending order
        liq_rows_interval_sorted = sorted(liq_rows_interval, key=lambda x: x['total_usd_size'], reverse=True)

        # Add rows to the table
        for row in liq_rows_interval_sorted:
            liq_table_interval.add_row(
                row['stars'],
                row['symbol'],
                row['liquidation_type'],
                row['count'],
                f"{row['total_usd_size']:,.2f}$",
                style=row['style']
            )

        # Liquidations Sizes Table (Since Start)
        liq_panel_all = Panel(
            f"🔸 🔶Total Liquidations since start:🔶 🔸\n"
            f"🌊Total Liquidations:           {total_liquidations_all}\n"
            f"📈Total Count:                  {liquidations_long_count_all}\n"
            f"📉Total Count:                  {liquidations_short_count_all}\n"
            f"📊Avg. Liquidations per minute: {avg_liquidations_per_minute_all:.2f}\n\n"
            f"📈Total Size:                   {total_usd_size_long_liq_all:,.2f}$\n"
            f"📉Total Size:                   {total_usd_size_short_liq_all:,.2f}$\n"
            f"🔰Spread:                       {usd_size_difference_liq_all:,.2f}$\n"
            f"📊Avg. USD Size per minute:     {avg_usd_size_per_minute_liq_all:,.2f}$",
            border_style=liq_panel_all_border_color,
            title="Liquidations (Since Start)"
        )

        liq_table_all = Table(title="🔍 Liquidation Sizes (Since Start)")
        liq_table_all.add_column("Stars")
        liq_table_all.add_column("Symbol")
        liq_table_all.add_column("Type")
        liq_table_all.add_column("Count")
        liq_table_all.add_column("Total USD Size")

        # Collect and sort rows
        liq_rows_all = []
        for stars in stars_count_liquidations_all:
            for liquidation_type in stars_count_liquidations_all[stars]:
                data = stars_count_liquidations_all[stars][liquidation_type]
                for symbol in data:
                    count = data[symbol]['count']
                    total_usd_size = data[symbol]['total_usd_size']
                    usd_size_color_type_liq = 'green' if liquidation_type == '📈 ' else 'red'
                    formatted_symbol = name_map.get(symbol, symbol)
                    liq_rows_all.append({
                        'stars': stars,
                        'symbol': formatted_symbol.strip(),
                        'liquidation_type': liquidation_type.strip(),
                        'count': str(count),
                        'total_usd_size': total_usd_size,
                        'style': usd_size_color_type_liq
                    })

        # Sort the rows by 'Total USD Size' in descending order
        liq_rows_all_sorted = sorted(liq_rows_all, key=lambda x: x['total_usd_size'], reverse=True)

        # Add rows to the table
        for row in liq_rows_all_sorted:
            liq_table_all.add_row(
                row['stars'],
                row['symbol'],
                row['liquidation_type'],
                row['count'],
                f"{row['total_usd_size']:,.2f}$",
                style=row['style']
            )

        # Update right layout
        layout["right"].update(
            Group(
                liq_panel,
                liq_table_interval,
                liq_panel_all,
                liq_table_all
            )
        )

    except Exception as e:
        # Debugging information
        console.print(f"[red]An error occurred in create_output: {e}[/red]")
        import traceback
        traceback.print_exc()



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

# Process Liquidation Function
async def process_liquidation(symbol, side, timestamp, usd_size):
    global liquidation_threshold
    symbol = symbol.upper()
    used_trade_time = format_trade_time(timestamp)
    liquidation_type = '📉 ' if side == 'SELL' else '📈 '
    if usd_size >= liquidation_threshold:
        collect_liquidation_data(symbol, used_trade_time, liquidation_type, usd_size, timestamp)

from websockets.exceptions import ConnectionClosed

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

# Binance Liquidation Stream
async def binance_liquidation(uri):
    while True:
        try:
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
                    if usd_size >= liquidation_threshold:
                        await process_liquidation(symbol, side, timestamp, usd_size)
        except ConnectionClosed:
            binance_liquidation_stream_conection = '📡❌🛰️'
            await asyncio.sleep(5)
        except Exception as e:
            console.print(f"[red]An error occurred in binance_liquidation: {e}[/red]")
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
    print(colored("\n♠️♦️Choose your symbols♣️♥️", 'black', 'on_white'))
    for key, value in name_map.items():
        print(f"{key}: {value.strip()}")

    print("ALL: all of them.")
    print("Type 'DONE' when you are finished.")

    global selected_symbols, selected_symbols_formatted, All_symbols
    selected_symbols = []

    while True:
        user_input = input("Select symbol: ").strip().upper()
        if user_input == 'ALL':
            selected_symbols = symbols
            All_symbols = True
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
        selected_symbols = symbols

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
    global trade_threshold, liquidation_threshold

    # Symbol selection
    select_symbols()

    # Prompt user for threshold values
    trade_threshold = float(input("🔧Please enter the threshold value for 'usd_size' on trades in $: "))
    liquidation_threshold = float(input("🔧Please enter the threshold value for 'usd_size' on liquidations in $: "))
    average_interval = int(input("🔧Please enter the interval over which to calculate averages in seconds: "))
    interval = 0.2  # Set interval to 1 second

    # Capture the start time in a readable format
    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    start_timestamp = datetime.now().timestamp() * 1000  # in milliseconds

    # Start WebSocket tasks
    for symbol in selected_symbols:
        stream_url = f"{websocket_url_base_binance}{symbol}@aggTrade"
        asyncio.create_task(binance_trade_stream(stream_url, symbol))

    asyncio.create_task(coinbase_trade_stream(websocket_url_base_coinbase))
    asyncio.create_task(binance_liquidation(websocket_url_liq))
    if kraken_symbols_selected:
        asyncio.create_task(kraken_trade_stream(websocket_url_kraken))

    if bitfinex_symbols_selected:
        asyncio.create_task(bitfinex_trade_stream(websocket_url_bitfinex))

    layout = Layout()
    layout.split_column(
        Layout(name="header", size=7),
        Layout(name="body")
    )
    layout["body"].split_row(
        Layout(name="left"),
        Layout(name="right")
    )

    # Start the Live display
    with Live(layout, console=console, refresh_per_second=2, screen=True) as live:
        while True:
            await asyncio.sleep(interval)
            metrics = calculate_metrics(
                trades_data,
                liquidations_data,
                trade_threshold,
                liquidation_threshold,
                average_interval,
                start_timestamp
            )
            create_output(layout, metrics, start_time, trade_threshold, liquidation_threshold)
            live.refresh()

if __name__ == "__main__":
    try:
        print("⚙️ asyncio.run(main()) is running ⚙️")
        asyncio.run(main())
        print("✅⚙️ Program is done ⚙✅️")
    except Exception as e:
        console.print(f"[red]An error occurred in the main program: {e}[/red]")
        import traceback
        traceback.print_exc()
