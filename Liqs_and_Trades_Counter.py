import asyncio
import json
import os
from datetime import datetime
import pytz
from websockets import connect, ConnectionClosed
from termcolor import colored
from colorama import init

# Initialize Colorama
init()

# Configuration
symbols = [
    'btcusdt', 'ethusdt', 'solusdt', 'bnbusdt', 'dogeusdt', 'usdcusdt',
    'xrpusdt', 'adausdt', 'maticusdt', 'tonusdt', 'linkusdt', 'trxusdt',
    'nearusdt', 'xlmusdt', 'rndrusdt', 'dotusdt', 'uniusdt', 'atomusdt',
    'xmrusdt', 'ldousdt', 'gmxusdt', 'ltcusdt', 'avaxusdt', 'bchusdt',
    'vetusdt', 'filusdt', 'etcusdt', 'algousdt', 'xtzusdt', 'eosusdt',
    'aaveusdt', 'mkrusdt', 'thetausdt', 'axsusdt', 'sandusdt', 'icpusdt'
]

# Placeholder for user-selected symbols
selected_symbols = []

websocket_url_base_binance = 'wss://fstream.binance.com/ws/'
websocket_url_base_coinbase = 'wss://ws-feed.exchange.coinbase.com'
websocket_url_liq = 'wss://fstream.binance.com/ws/!forceOrder@arr'

# Initialize Variables
name_map = {
    'BTC': '🟡BTC     ', 'ETH': '💠ETH     ', 'SOL': '👾SOL     ', 'BNB': '🔶BNB     ', 'DOGE': '🐶DOGE    ',
    'USDC': '💵USDC    ', 'XRP': '⚫XRP     ', 'ADA': '🔵ADA     ', 'MATIC': '🟣MATIC   ',
    'TON': '🎮TON     ', 'LINK': '🔗LINK    ', 'TRX': '⚙️TRX     ', 'NEAR': '🔍NEAR    ', 'XLM': '🌟XLM     ',
    'RNDR': '🎨RNDR    ', 'DOT': '⚪DOT     ', 'UNI': '🦄UNI     ', 'ATOM': '⚛️ATOM    ', 'XMR': '👽XMR     ',
    'LDO': '🧪LDO     ', 'GMX': '🌀GMX     ', 'LTC': '🌕LTC     ', 'AVAX': '🏔️AVAX    ', 'BCH': '💰BCH     ',
    'VET': '♻️VET     ', 'FIL': '📁FIL     ', 'ETC': '⛏️ETC     ', 'ALGO': '🔺ALGO    ', 'XTZ': '🏺XTZ     ',
    'EOS': '🌐EOS     ', 'AAVE': '🏦AAVE    ', 'MKR': '🏭MKR     ', 'THETA': '📺THETA   ', 'AXS': '🕹️AXS     ',
    'SAND': '🏖️SAND    ', 'ICP': '🌐ICP     '
}

# Data Collection Lists
trades_data = []
liquidations_data = []

# Thresholds for printing output
trade_threshold = 0
liquidation_threshold = 0

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
    return time_difference

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

def calculate_metrics(trades_data, liquidations_data, trade_threshold, liquidation_threshold, average_interval, start_timestamp):
    current_time = datetime.now().timestamp() * 1000  # Aktuelle Zeit in Millisekunden

    # Gesamtzeit seit Programmstart in Sekunden
    total_elapsed_time = (current_time - start_timestamp) / 1000

    # Filter data to last average_interval seconds
    filtered_trades_data = [trade for trade in trades_data if current_time - trade[4] <= average_interval * 1000]
    filtered_liquidations_data = [liq for liq in liquidations_data if current_time - liq[4] <= average_interval * 1000]

    # --- Berechnungen innerhalb des average_interval ---

    # Trades innerhalb des Intervalls
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

    # Liquidationen innerhalb des Intervalls
    total_liquidations_in_interval = len(filtered_liquidations_data)
    total_usd_size_liq_in_interval = sum(liq[3] if liq[2] == '📈 ' else -liq[3] for liq in filtered_liquidations_data)

    liquidations_long_count = sum(1 for liq in filtered_liquidations_data if liq[2] == '📈 ')
    liquidations_short_count = sum(1 for liq in filtered_liquidations_data if liq[2] == '📉 ')

    total_usd_size_long_liq = sum(liq[3] for liq in filtered_liquidations_data if liq[2] == '📈 ')
    total_usd_size_short_liq = sum(liq[3] for liq in filtered_liquidations_data if liq[2] == '📉 ')

    usd_size_difference_liq = total_usd_size_long_liq - total_usd_size_short_liq

    avg_liquidations_per_minute = (total_liquidations_in_interval * 60) / average_interval if average_interval > 0 else 0
    avg_usd_size_per_minute_liq = (total_usd_size_liq_in_interval * 60) / average_interval if average_interval > 0 else 0

    # Sterne zählen für Trades innerhalb des Intervalls
    stars_count_trades = {}
    for trade in filtered_trades_data:
        usd_size = trade[3]
        stars = get_stars(usd_size)
        trade_type = trade[2]
        if stars not in stars_count_trades:
            stars_count_trades[stars] = {'📈 ': {'count': 0, 'total_usd_size': 0}, '📉 ': {'count': 0, 'total_usd_size': 0}}
        stars_count_trades[stars][trade_type]['count'] += 1
        stars_count_trades[stars][trade_type]['total_usd_size'] += usd_size

    # Sterne zählen für Liquidationen innerhalb des Intervalls
    stars_count_liquidations = {}
    for liquidation in filtered_liquidations_data:
        usd_size = liquidation[3]
        stars = get_liq_stars(usd_size)
        liquidation_type = liquidation[2]
        if stars not in stars_count_liquidations:
            stars_count_liquidations[stars] = {'📈 ': {'count': 0, 'total_usd_size': 0}, '📉 ': {'count': 0, 'total_usd_size': 0}}
        stars_count_liquidations[stars][liquidation_type]['count'] += 1
        stars_count_liquidations[stars][liquidation_type]['total_usd_size'] += usd_size

    # --- Kumulative Berechnungen seit Programmstart ---

    # Trades seit Programmstart
    total_trades_all = len(trades_data)
    total_usd_size_all = sum(trade[3] if trade[2] == '📈 ' else -trade[3] for trade in trades_data)

    trades_long_count_all = sum(1 for trade in trades_data if trade[2] == '📈 ')
    trades_short_count_all = sum(1 for trade in trades_data if trade[2] == '📉 ')

    total_usd_size_long_all = sum(trade[3] for trade in trades_data if trade[2] == '📈 ')
    total_usd_size_short_all = sum(trade[3] for trade in trades_data if trade[2] == '📉 ')

    usd_size_difference_all = total_usd_size_long_all - total_usd_size_short_all

    # Durchschnittliche Trades und USD-Größe pro Minute seit Programmstart
    avg_trades_per_minute_all = (total_trades_all * 60) / total_elapsed_time if total_elapsed_time > 0 else 0
    avg_usd_size_per_minute_all = (total_usd_size_all * 60) / total_elapsed_time if total_elapsed_time > 0 else 0

    # Liquidationen seit Programmstart
    total_liquidations_all = len(liquidations_data)
    total_usd_size_liq_all = sum(liq[3] if liq[2] == '📈 ' else -liq[3] for liq in liquidations_data)

    liquidations_long_count_all = sum(1 for liq in liquidations_data if liq[2] == '📈 ')
    liquidations_short_count_all = sum(1 for liq in liquidations_data if liq[2] == '📉 ')

    total_usd_size_long_liq_all = sum(liq[3] for liq in liquidations_data if liq[2] == '📈 ')
    total_usd_size_short_liq_all = sum(liq[3] for liq in liquidations_data if liq[2] == '📉 ')

    usd_size_difference_liq_all = total_usd_size_long_liq_all - total_usd_size_short_liq_all

    avg_liquidations_per_minute_all = (total_liquidations_all * 60) / total_elapsed_time if total_elapsed_time > 0 else 0
    avg_usd_size_per_minute_liq_all = (total_usd_size_liq_all * 60) / total_elapsed_time if total_elapsed_time > 0 else 0

    # Sterne zählen für alle Trades
    stars_count_trades_all = {}
    for trade in trades_data:
        usd_size = trade[3]
        stars = get_stars(usd_size)
        trade_type = trade[2]
        if stars not in stars_count_trades_all:
            stars_count_trades_all[stars] = {'📈 ': {'count': 0, 'total_usd_size': 0}, '📉 ': {'count': 0, 'total_usd_size': 0}}
        stars_count_trades_all[stars][trade_type]['count'] += 1
        stars_count_trades_all[stars][trade_type]['total_usd_size'] += usd_size

    # Sterne zählen für alle Liquidationen
    stars_count_liquidations_all = {}
    for liquidation in liquidations_data:
        usd_size = liquidation[3]
        stars = get_liq_stars(usd_size)
        liquidation_type = liquidation[2]
        if stars not in stars_count_liquidations_all:
            stars_count_liquidations_all[stars] = {'📈 ': {'count': 0, 'total_usd_size': 0}, '📉 ': {'count': 0, 'total_usd_size': 0}}
        stars_count_liquidations_all[stars][liquidation_type]['count'] += 1
        stars_count_liquidations_all[stars][liquidation_type]['total_usd_size'] += usd_size

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

def export_data():
    """
    Handles data export if necessary.
    Currently a placeholder as export functionality is not required.
    """
    pass  # No action needed as per current requirements

def display_output(metrics, start_time, trade_threshold, liquidation_threshold):
    """
    Displays the calculated metrics to the console.
    """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    time_difference = calculate_time_difference(start_time, current_time)

    # Unpack metrics for easier access
    average_interval = metrics['average_interval']

    # Trades within interval
    total_trades_in_interval = metrics['total_trades_in_interval']
    total_usd_size_in_interval = metrics['total_usd_size_in_interval']
    trades_long_count = metrics['trades_long_count']
    trades_short_count = metrics['trades_short_count']
    total_usd_size_long = metrics['total_usd_size_long']
    total_usd_size_short = metrics['total_usd_size_short']
    usd_size_difference = metrics['usd_size_difference']
    avg_trades_per_minute = metrics['avg_trades_per_minute']
    avg_usd_size_per_minute = metrics['avg_usd_size_per_minute']
    usd_size_color = metrics['usd_size_color']
    difference_color = metrics['difference_color']
    stars_count_trades = metrics['stars_count_trades']

    # Liquidations within interval
    total_liquidations_in_interval = metrics['total_liquidations_in_interval']
    total_usd_size_liq_in_interval = metrics['total_usd_size_liq_in_interval']
    liquidations_long_count = metrics['liquidations_long_count']
    liquidations_short_count = metrics['liquidations_short_count']
    total_usd_size_long_liq = metrics['total_usd_size_long_liq']
    total_usd_size_short_liq = metrics['total_usd_size_short_liq']
    usd_size_difference_liq = metrics['usd_size_difference_liq']
    avg_liquidations_per_minute = metrics['avg_liquidations_per_minute']
    avg_usd_size_per_minute_liq = metrics['avg_usd_size_per_minute_liq']
    usd_size_color_liq = metrics['usd_size_color_liq']
    difference_color_liq = metrics['difference_color_liq']
    stars_count_liquidations = metrics['stars_count_liquidations']

    # Cumulative Trades
    total_trades_all = metrics['total_trades_all']
    total_usd_size_all = metrics['total_usd_size_all']
    trades_long_count_all = metrics['trades_long_count_all']
    trades_short_count_all = metrics['trades_short_count_all']
    total_usd_size_long_all = metrics['total_usd_size_long_all']
    total_usd_size_short_all = metrics['total_usd_size_short_all']
    usd_size_difference_all = metrics['usd_size_difference_all']
    avg_trades_per_minute_all = metrics['avg_trades_per_minute_all']
    avg_usd_size_per_minute_all = metrics['avg_usd_size_per_minute_all']
    usd_size_color_all = metrics['usd_size_color_all']
    difference_color_all = metrics['difference_color_all']
    stars_count_trades_all = metrics['stars_count_trades_all']

    # Cumulative Liquidations
    total_liquidations_all = metrics['total_liquidations_all']
    total_usd_size_liq_all = metrics['total_usd_size_liq_all']
    liquidations_long_count_all = metrics['liquidations_long_count_all']
    liquidations_short_count_all = metrics['liquidations_short_count_all']
    total_usd_size_long_liq_all = metrics['total_usd_size_long_liq_all']
    total_usd_size_short_liq_all = metrics['total_usd_size_short_liq_all']
    usd_size_difference_liq_all = metrics['usd_size_difference_liq_all']
    avg_liquidations_per_minute_all = metrics['avg_liquidations_per_minute_all']
    avg_usd_size_per_minute_liq_all = metrics['avg_usd_size_per_minute_liq_all']
    usd_size_color_liq_all = metrics['usd_size_color_liq_all']
    difference_color_liq_all = metrics['difference_color_liq_all']
    stars_count_liquidations_all = metrics['stars_count_liquidations_all']

    # Prepare selected symbols for display
    selected_symbols_display = [symbol.upper().replace('USDT', '') for symbol in selected_symbols]
    symbols_display = ', '.join(selected_symbols_display)

    print(f"\n--------------------------------------------------------------------")
    print(f"📅 Start Time: {start_time}")
    print(f"🕰️ Current Time: {current_time}")
    print(f"⏳{time_difference}⏳")
    print(f"📊 Selected Symbols: {symbols_display}")
    print(f"--------------------------------------------------------------------")
    # --- Metrics within the average_interval ---
    print(f"\n🔹 🔷Metrics for the last {average_interval} seconds:🔷 🔹")
    print(f"🎣A Total of {total_trades_in_interval} Trades above {trade_threshold}$:")
    print(colored(f"📈Total Count: {trades_long_count}  | 📈Total Size: {total_usd_size_long:,.2f}$", 'black', 'on_green'))
    print(colored(f"📉Total Count: {trades_short_count} | 📉Total Size: {total_usd_size_short:,.2f}$", 'black', 'on_red'))
    print("🔍 Trade Sizes:")
    # Sort and display trades with 📈 first and 📉 second
    for trade_type in ['📈 ', '📉 ']:
        for stars, data in stars_count_trades.items():
            if data[trade_type]['count'] > 0:
                usd_size_color_type = 'green' if trade_type == '📈 ' else 'red'
                print(f"  {stars}: {trade_type}{data[trade_type]['count']} Trades | Total USD Size: {colored(f'{data[trade_type]['total_usd_size']:,.2f}$', usd_size_color_type)}")
    print(colored(f"\n          Difference: {usd_size_difference:,.2f}$", difference_color, attrs=['bold']))
    print(colored(f"\n📊 Avg. Trades per minute: {avg_trades_per_minute:.2f}", 'white'))
    print(colored(f"📊 Avg. USD Size per minute: {avg_usd_size_per_minute:,.2f}$", usd_size_color, attrs=['bold']))
    print(f"\n--------------------------------------------------------------------")

    print(f"\n\n🔸 🔶Total since start:🔶 🔸")
    print(f"🎣A Total of {total_trades_all} Trades above {trade_threshold}$:")
    print(colored(f"📈Total Count: {trades_long_count_all}  | 📈Total Size: {total_usd_size_long_all:,.2f}$", 'black', 'on_green'))
    print(colored(f"📉Total Count: {trades_short_count_all} | 📉Total Size: {total_usd_size_short_all:,.2f}$", 'black', 'on_red'))
    print("🔍 Trade Sizes:")
    # Sort and display cumulative trades with 📈 first and 📉 second
    for trade_type in ['📈 ', '📉 ']:
        for stars, data in stars_count_trades_all.items():
            if data[trade_type]['count'] > 0:
                usd_size_color_type = 'green' if trade_type == '📈 ' else 'red'
                print(f"  {stars}: {trade_type}{data[trade_type]['count']} Trades | Total USD Size: {colored(f'{data[trade_type]['total_usd_size']:,.2f}$', usd_size_color_type)}")
    print(colored(f"\n            Difference: {usd_size_difference_all:,.2f}$", difference_color_all, attrs=['bold']))
    print(colored(f"\n📊 Avg. Trades per minute: {avg_trades_per_minute_all:.2f}", 'white'))
    print(colored(f"📊 Avg. USD Size per minute: {avg_usd_size_per_minute_all:,.2f}$", usd_size_color_all, attrs=['bold']))
    print(f"\n--------------------------------------------------------------------")    
    print(f"\n🔹 🔷Metrics for the last {average_interval} seconds:🔷 🔹")
    print(f"\n🌊A Total of {total_liquidations_in_interval} Liquidations above {liquidation_threshold}$:")
    print(colored(f"📈Total Count: {liquidations_long_count}  | 📈Total Size: {total_usd_size_long_liq:,.2f}$", 'black', 'on_green'))
    print(colored(f"📉Total Count: {liquidations_short_count} | 📉Total Size: {total_usd_size_short_liq:,.2f}$", 'black', 'on_red'))
    print("🔍 Liquidation Sizes:")
    # Sort and display liquidations with 📈 first and 📉 second
    for liquidation_type in ['📈 ', '📉 ']:
        for stars, data in stars_count_liquidations.items():
            if data[liquidation_type]['count'] > 0:
                usd_size_color_type_liq = 'green' if liquidation_type == '📈 ' else 'red'
                print(f"  {stars}: {liquidation_type}{data[liquidation_type]['count']} Liquidations | Total USD Size: {colored(f'{data[liquidation_type]['total_usd_size']:,.2f}$', usd_size_color_type_liq)}")
    print(colored(f"Difference: {usd_size_difference_liq:,.2f}$", difference_color_liq, attrs=['bold']))
    print(colored(f"📊 Avg. Liquidations per minute: {avg_liquidations_per_minute:.2f}", 'white'))
    print(colored(f"📊 Avg. USD Size per minute: {avg_usd_size_per_minute_liq:,.2f}$", usd_size_color_liq, attrs=['bold']))
    print(f"\n--------------------------------------------------------------------")
    # --- Cumulative Metrics since start ---
    print(f"\n🔸 🔶Total since start:🔶 🔸")
    print(f"\n🌊A Total of {total_liquidations_all} Liquidations above {liquidation_threshold}$:")
    print(colored(f"\n📈Total Count: {liquidations_long_count_all}  | 📈Total Size: {total_usd_size_long_liq_all:,.2f}$", 'black', 'on_green'))
    print(colored(f"📉Total Count: {liquidations_short_count_all} | 📉Total Size: {total_usd_size_short_liq_all:,.2f}$", 'black', 'on_red'))
    print("🔍 Liquidation Sizes:")
    # Sort and display cumulative liquidations with 📈 first and 📉 second
    for liquidation_type in ['📈 ', '📉 ']:
        for stars, data in stars_count_liquidations_all.items():
            if data[liquidation_type]['count'] > 0:
                usd_size_color_type_liq = 'green' if liquidation_type == '📈 ' else 'red'
                print(f"  {stars}: {liquidation_type}{data[liquidation_type]['count']} Liquidations | Total USD Size: {colored(f'{data[liquidation_type]['total_usd_size']:,.2f}$', usd_size_color_type_liq)}")
    print(colored(f"\n            Difference: {usd_size_difference_liq_all:,.2f}$", difference_color_liq_all, attrs=['bold']))
    print(colored(f"📊 Avg. Liquidations per minute: {avg_liquidations_per_minute_all:.2f}", 'white'))
    print(colored(f"📊 Avg. USD Size per minute: {avg_usd_size_per_minute_liq_all:,.2f}$", usd_size_color_liq_all, attrs=['bold']))

    print(f"\n--------------------------------------------------------------------")

# Process Trade Function for Normal Trades
async def process_trade(symbol, price, quantity, trade_time, is_buyer_maker):
    global trade_threshold
    usd_size = price * quantity
    SYMBL = symbol.upper().replace('USDT', '')
    if usd_size >= trade_threshold:
        trade_type = '📉 ' if is_buyer_maker else '📈 '
        used_trade_time = format_trade_time(trade_time)
        # Collect data
        collect_trade_data(SYMBL, used_trade_time, trade_type, usd_size, trade_time)

# Process Liquidation Function
async def process_liquidation(symbol, side, timestamp, usd_size):
    global liquidation_threshold
    used_trade_time = format_trade_time(timestamp)
    liquidation_type = '📉 ' if side == 'SELL' else '📈 '
    if usd_size >= liquidation_threshold:
        formatted_symbol = symbol.ljust(6)[:6]
        # Collect data
        collect_liquidation_data(formatted_symbol, used_trade_time, liquidation_type, usd_size, timestamp)

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
        except:
            await asyncio.sleep(5)

# Coinbase Trade Stream
async def coinbase_trade_stream(uri):
    # Extract symbols from the global selected_symbols list and format them to match Coinbase's product IDs (e.g., BTC-USD)
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
                        symbol = product_id.split('-')[0]
                        price = float(data['price'])
                        quantity = float(data['last_size'])
                        trade_time = int(datetime.fromisoformat(data['time'].replace('Z', '+00:00')).timestamp() * 1000)
                        is_buyer_maker = data['side'] == 'sell'
                        await process_trade(symbol, price, quantity, trade_time, is_buyer_maker)
        except:
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
        except:
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

    global selected_symbols
    selected_symbols = []

    while True:
        user_input = input("Select symbol: ").strip().upper()
        if user_input == 'ALL':
            selected_symbols = symbols
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

async def main():
    """
    Main function that initializes thresholds, selects symbols, and starts WebSocket streams.
    """
    global trade_threshold, liquidation_threshold

    # Symbol selection
    select_symbols()

    # Prompt user for threshold values
    trade_threshold = float(input("🔧Please enter the threshold value for 'usd_size' on trades: "))
    liquidation_threshold = float(input("🔧Please enter the threshold value for 'usd_size' on liquidations: "))
    average_interval = int(input("🔧Please enter the interval over which to calculate averages in seconds: "))
    interval = 1  # Set interval to 1 second

    # Capture the start time in a readable format
    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    start_timestamp = datetime.now().timestamp() * 1000  # in milliseconds

    # Start WebSocket tasks
    for symbol in selected_symbols:
        stream_url = f"{websocket_url_base_binance}{symbol}@aggTrade"
        asyncio.create_task(binance_trade_stream(stream_url, symbol))

    asyncio.create_task(coinbase_trade_stream(websocket_url_base_coinbase))
    asyncio.create_task(binance_liquidation(websocket_url_liq))

    # Main loop for periodic calculations and display
    while True:
        await asyncio.sleep(interval)
        # Clear the console
        os.system('cls' if os.name == 'nt' else 'clear')
        metrics = calculate_metrics(
            trades_data,
            liquidations_data,
            trade_threshold,
            liquidation_threshold,
            average_interval,
            start_timestamp
        )
        display_output(metrics, start_time, trade_threshold, liquidation_threshold)

# Start the main function
asyncio.run(main())
