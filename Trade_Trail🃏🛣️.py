import asyncio
import json
import os
from datetime import datetime
import pytz
from websockets import connect, ConnectionClosed
from termcolor import colored, cprint
from colorama import init
import pandas as pd
import xlsxwriter

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
    'ksmusdt', 'renusdt'
]

# Placeholder for user-selected symbols
selected_symbols = []

websocket_url_base_binance = 'wss://fstream.binance.com/ws/'
websocket_url_base_coinbase = 'wss://ws-feed.exchange.coinbase.com'
websocket_url_liq = 'wss://fstream.binance.com/ws/!forceOrder@arr'
websocket_url_kraken = 'wss://ws.kraken.com/'
websocket_url_bitfinex = 'wss://api-pub.bitfinex.com/ws/2'
output_directory = "/home/jestersly/Schreibtisch/Codes/_Algo_Trade_Edge/Data_Streams/Liqs_and_Trades_Archive/"
print("📡 Configuration loaded")

# Ensure the output directory exists
os.makedirs(output_directory, exist_ok=True)

# Initialize Maps and Variables
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


cumulative_sum_map = {}
cumulative_sum_map_liq = {}
trade_count_map = {}
connection_closed_logged = set()

# Data Collection Lists
trades_data = []
liquidations_data = []

# Column names for the Excel export
trades_columns = ['symbol', 'used_trade_time', 'trade_type', 'usd_size']
liquidations_columns = ['symbol', 'used_trade_time', 'liquidation_type', 'usd_size']

# Thresholds for printing output
trade_threshold = 0
liquidation_threshold = 0

def initialize_maps():
    """
    Initializes cumulative sum maps for selected symbols.
    """
    global cumulative_sum_map, cumulative_sum_map_liq
    cumulative_sum_map = {symbol.upper().replace('USDT', ''): 0 for symbol in selected_symbols}
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
        if 'trade_type' in df.columns and row['trade_type'] == '📈 ':
            cumulative_sum += row['usd_size']
        elif 'trade_type' in df.columns and row['trade_type'] == '📉 ':
            cumulative_sum -= row['usd_size']
        elif 'liquidation_type' in df.columns and row['liquidation_type'] == '📈 ':
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


async def periodic_export(interval, trade_threshold, liquidation_threshold, start_time):
    """
    Periodically exports the collected trade and liquidation data to Excel files.
    """
    # Initialize cumulative values and counts
    total_intervals = 0
    total_trades_above_threshold = 0
    total_liquidations_above_threshold = 0
    total_usd_size = 0
    total_usd_size_liq = 0

    while True:
        try:
            await asyncio.sleep(interval)
            total_intervals += 1
            # Stars counting dictionaries for trades and liquidations
            stars_count_trades = {}
            stars_count_liquidations = {}

            # Count trades and liquidations above threshold
            trades_above_threshold = sum(1 for trade in trades_data if trade[3] >= trade_threshold)
            liquidations_above_threshold = sum(1 for liquidation in liquidations_data if liquidation[3] >= liquidation_threshold)

            # Calculate total usd_size considering trade types
            usd_size_sum = sum(trade[3] if trade[2] == '📈 ' else -trade[3] for trade in trades_data)
            usd_size_sum_liq = sum(liquidation[3] if liquidation[2] == '📈 ' else -liquidation[3] for liquidation in liquidations_data)

            # Update cumulative values
            total_trades_above_threshold += trades_above_threshold
            total_liquidations_above_threshold += liquidations_above_threshold
            total_usd_size += usd_size_sum
            total_usd_size_liq += usd_size_sum_liq

            # Iterate over trades to count stars occurrences and accumulate usd_size
            for trade in trades_data:
                usd_size = trade[3]
                stars = get_stars(usd_size)
                trade_type = trade[2]
                if stars not in stars_count_trades:
                    stars_count_trades[stars] = {'📈 ': {'count': 0, 'total_usd_size': 0}, '📉 ': {'count': 0, 'total_usd_size': 0}}
                stars_count_trades[stars][trade_type]['count'] += 1
                stars_count_trades[stars][trade_type]['total_usd_size'] += usd_size

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
            avg_trades_per_minute = total_trades_above_threshold / total_intervals if total_intervals > 0 else 0
            avg_liquidations_per_minute = total_liquidations_above_threshold / total_intervals if total_intervals > 0 else 0
            avg_usd_size_per_minute = total_usd_size / total_intervals if total_intervals > 0 else 0
            avg_usd_size_per_minute_liq = total_usd_size_liq / total_intervals if total_intervals > 0 else 0

            # Determine the color of the average usd_size
            usd_size_color = 'green' if avg_usd_size_per_minute > 0 else 'red'
            usd_size_color_liq = 'green' if avg_usd_size_per_minute_liq > 0 else 'red'

            # Calculate counts for trades
            trades_count = len(trades_data)
            trades_long_count = sum(1 for trade in trades_data if trade[2] == '📈 ')
            trades_short_count = sum(1 for trade in trades_data if trade[2] == '📉 ')

            # Calculate counts for liquidations
            liquidations_count = len(liquidations_data)
            liquidations_long_count = sum(1 for liquidation in liquidations_data if liquidation[2] == '📈 ')
            liquidations_short_count = sum(1 for liquidation in liquidations_data if liquidation[2] == '📉 ')

            # Calculate total usd_size for trades
            total_usd_size_long = sum(trade[3] for trade in trades_data if trade[2] == '📈 ')
            total_usd_size_short = sum(trade[3] for trade in trades_data if trade[2] == '📉 ')

            # Calculate total usd_size for liquidations
            total_usd_size_long_liq = sum(liquidation[3] for liquidation in liquidations_data if liquidation[2] == '📈 ')
            total_usd_size_short_liq = sum(liquidation[3] for liquidation in liquidations_data if liquidation[2] == '📉 ')

            # Calculate the difference between long and short
            usd_size_difference = total_usd_size_long - total_usd_size_short
            usd_size_difference_liq = total_usd_size_long_liq - total_usd_size_short_liq

            # Determine the color based on the difference
            difference_color = 'green' if usd_size_difference > 0 else 'red'
            difference_color_liq = 'green' if usd_size_difference_liq > 0 else 'red'

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
            trades_filename = f"Trades_threshold_{trade_threshold}.xlsx"
            liquidations_filename = f"Liquidations_threshold_{liquidation_threshold}.xlsx"

            # Export to Excel with the generated filenames
            export_to_excel(trades_data, trades_columns, trades_filename, output_directory)
            export_to_excel(liquidations_data, liquidations_columns, liquidations_filename, output_directory)

        except Exception as e:
            print(f"Error during export: {e}")






def collect_trade_data(symbol, used_trade_time, trade_type, usd_size):
    """
    Collects trade data and appends it to the trades_data list.
    """
    trades_data.append([symbol, used_trade_time, trade_type, usd_size])

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

def get_attrs_trades(usd_size):
    if usd_size >= 5000000:
        return ['bold', 'blink']
    elif usd_size >= 1000000:
        return ['bold']
    else:
        return []

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


def get_attrs_liquidations(usd_size):
    if usd_size >= 1000000:
        return ['bold', 'blink']
    elif usd_size >= 500000:
        return ['bold']
    else:
        return []


    
def update_cumulative_sum(symbol, usd_size, trade_type):
    if trade_type == '📉 ':
        cumulative_sum_map[symbol] -= usd_size
    else:
        cumulative_sum_map[symbol] += usd_size
    return cumulative_sum_map[symbol]

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

# Process Trade Function for Normal Trades
async def process_trade(symbol, price, quantity, trade_time, is_buyer_maker):
    global trade_threshold
    usd_size = price * quantity
    SYMBL = symbol.upper().replace('USDT', '')
    max_price = 1000000000

    if usd_size >= trade_threshold:
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
        output = f"{name_map.get(SYMBL, SYMBL.ljust(9))}{'|'}{stars}{'|'}{used_trade_time}{'|'}{trade_type}{usd_size_str}{stars_padding}{'|'} 💵🟰 {cumulative_sum_str}"

        if usd_size > 20000000:
            output = add_color_border(output, 'green')
        elif usd_size < -20000000:
            output = add_color_border(output, 'red')

        cprint(output, 'white', attrs=attrs)
        update_trade_count(SYMBL, stars, trade_type)

# Process Liquidation Function
async def process_liquidation(symbol, side, timestamp, usd_size):
    global liquidation_threshold
    berlin = pytz.timezone("Europe/Berlin")
    used_trade_time = format_trade_time(timestamp)
    liquidation_type = '📉 ' if side == 'SELL' else '📈 '
    max_price = 1000000000

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

                    if usd_size >= liquidation_threshold:
                        await process_liquidation(symbol, side, timestamp, usd_size)
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
            print("No Connection📡❌🛰️ (Bitfinex)")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"[red]An error occurred in bitfinex_trade_stream: {e}[/red]")
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

    global selected_symbols  # Ensure we're using the global variable
    selected_symbols = []  # Reinitialize it to avoid any previous data

    while True:
        user_input = input("Select symbol: ").strip().upper()
        if user_input == 'ALL':
            selected_symbols = symbols  # Return all symbols in their original format
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

    # Return selected symbols; fallback to all symbols if none selected
    if not selected_symbols:
        selected_symbols = symbols

        # Create the formatted symbol list
    selected_symbols_formatted = [name_map.get(symbol.upper().replace('USDT', ''), symbol.upper().replace('USDT', '')) for symbol in selected_symbols]

    global kraken_symbols_selected, bitfinex_symbols_selected
    kraken_symbols_selected = [kraken_symbol_map[symbol] for symbol in selected_symbols if symbol in kraken_symbol_map and kraken_symbol_map[symbol] is not None]
    bitfinex_symbols_selected = [bitfinex_symbol_map[symbol] for symbol in selected_symbols if symbol in bitfinex_symbol_map and bitfinex_symbol_map[symbol] is not None]

    if not kraken_symbols_selected:
        print("No selected symbols are available on Kraken.")
    if not bitfinex_symbols_selected:
        print("No selected symbols are available on Bitfinex.")



async def main():
    """
    Main function that initializes thresholds, selects symbols, and starts WebSocket streams.
    """
    global trade_threshold, liquidation_threshold
    print("⚙️ Start main function ⚙️")

    # Symbol selection
    select_symbols()  # Populate selected_symbols globally
    initialize_maps()  # Initialize the maps for cumulative sums

    # Prompt user for threshold values
    trade_threshold = float(input("🔧Please enter the threshold value for 'usd_size' on trades: "))
    liquidation_threshold = float(input("🔧Please enter the threshold value for 'usd_size' on liquidations: "))
    interval = int(input("🔧Please enter the interval for exportation and calculation in seconds: "))

    # Capture the start time in a readable format
    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    tasks = []
    for symbol in selected_symbols:
        stream_url = f"{websocket_url_base_binance}{symbol}@aggTrade"
        tasks.append(binance_trade_stream(stream_url, symbol))

    # Ensure streams and processing are only set up for selected symbols
    tasks.append(coinbase_trade_stream(websocket_url_base_coinbase))
    tasks.append(binance_liquidation(websocket_url_liq))
    if kraken_symbols_selected:
        asyncio.create_task(kraken_trade_stream(websocket_url_kraken))
    if bitfinex_symbols_selected:
        asyncio.create_task(bitfinex_trade_stream(websocket_url_bitfinex))
    tasks.append(periodic_export(interval, trade_threshold, liquidation_threshold, start_time))

    print("⚙️ asyncio.gather is running ⚙️")
    await asyncio.gather(*tasks)

# Start the main function properly
print("⚙️ asyncio.run(main()) is running ⚙️")
asyncio.run(main())
print("✅⚙️ Program is done ⚙✅️")
