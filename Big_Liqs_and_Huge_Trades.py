import asyncio
import json
import os
from datetime import datetime
import pytz
from websockets import connect, ConnectionClosed
from termcolor import colored, cprint
from colorama import init

# Initialize Colorama
init()
print("🗄️ Bibliotheken erfolgreich importiert")

# Configuration
symbols = [
    'btcusdt', 'ethusdt', 'solusdt', 'bnbusdt', 'dogeusdt', 'usdcusdt',
    'xrpusdt', 'adausdt', 'maticusdt', 'tonusdt', 'linkusdt', 'trxusdt', 'nearusdt',
    'xlmusdt', 'rndrusdt', 'dotusdt', 'uniusdt', 'atomusdt', 'xmrusdt', 'ldousdt', 'gmxusdt'
]
websocket_url_base_binance = 'wss://fstream.binance.com/ws/'
websocket_url_base_coinbase = 'wss://ws-feed.exchange.coinbase.com'
websocket_url_liq = 'wss://fstream.binance.com/ws/!forceOrder@arr'

# Define file paths
data_stream_archive_dir = "/home/jestersly/Schreibtisch/Codes/_Algo_Trade_Edge/Data_Streams/Data_Stream_Archive"
current_date = datetime.now().strftime("%Y%m%d")
daily_dir = os.path.join(data_stream_archive_dir, current_date)
trades_filename = os.path.join(daily_dir, "Trades.csv")
liq_trades_filename = os.path.join(daily_dir, "Liqs.csv")

print("📡 Konfiguration geladen")

# Initialize Maps and Files
name_map = {
    'BTC': '🟡BTC     ', 'ETH': '💠ETH     ', 'SOL': '👾SOL     ', 'BNB': '🔶BNB     ', 'DOGE': '🐶DOGE    ',
    'USDC': '💵USDC    ', 'XRP': '⚫XRP     ', 'ADA': '🔵ADA     ', 'MATIC': '🟣MATIC   ',
    'TON': '🎮TON      ', 'LINK': '🔗LINK    ', 'TRX': '⚙️TRX     ', 'NEAR': '🔍NEAR    ', 'XLM': '🌟XLM     ',
    'RNDR': '🎨RNDR    ', 'DOT': '⚪DOT     ', 'UNI': '🦄UNI     ', 'ATOM': '⚛️ATOM    ', 'XMR': '👽XMR     ',
    'LDO': '🧪LDO     ', 'GMX': '🌀GMX     '
}

cumulative_sum_map = {symbol.upper().replace('USDT', ''): 0 for symbol in symbols}
cumulative_sum_map_liq = {}
print("💾 Maps und Dateien initialisiert")

# Tracking Map for counting trades and liquidations
trade_count_map = {}
connection_closed_logged = set()

def initialize_files():
    if not os.path.isdir(daily_dir):
        os.makedirs(daily_dir)
        print(f"Verzeichnis {daily_dir} erstellt")

    if not os.path.isfile(trades_filename):
        with open(trades_filename, 'w') as f:
            f.write('Event Time, Symbol, Aggregate Trade ID, Price, Quantity, Trade Time, Is Buyer Maker, Trade Type, USD Size\n')
        print(f"Datei {trades_filename} erstellt")

    if not os.path.isfile(liq_trades_filename):
        with open(liq_trades_filename, 'w') as f:
            f.write(",".join([
                'symbol', 'side', 'order_type', 'time_in_force',
                'original_quantity', 'order_status', 'order_last_filled_quantity',
                'order_filled_accumulated_quantity', 'order_trade_time', 'usd_size'
            ]) + '\n')
        print(f"Datei {liq_trades_filename} erstellt")

initialize_files()

# Process Trade Function for Normal Trades
async def process_trade(symbol, price, quantity, trade_time, is_buyer_maker):
    usd_size = price * quantity
    SYMBL = symbol.upper().replace('USDT', '')
    max_price = 1000000000

    if usd_size >= 500000:
        trade_type = '📉 ' if is_buyer_maker else '📈 '
        stars = get_stars(usd_size)
        attrs = get_attrs_trades(usd_size)
        cumulative_sum = update_cumulative_sum(SYMBL, usd_size, trade_type)
        cumulative_sum_str = format_cumulative_sum(cumulative_sum)
        usd_size_str = format_usd_size(usd_size, trade_type)
        stars_padding = get_stars_padding(usd_size, max_price)
        time_berlin = format_trade_time(trade_time)
        output = f"{name_map[SYMBL]}{'|'}{stars}{'|'}{time_berlin}{'|'}{trade_type}{usd_size_str}{stars_padding}{'|'} 💵🟰 {cumulative_sum_str}"

        if usd_size > 20000000:
            output = add_color_border(output, 'green')
        elif usd_size < -20000000:
            output = add_color_border(output, 'red')

        cprint(output, 'white', attrs=attrs)
        write_to_file(trades_filename, trade_time, symbol, price, quantity, trade_type, usd_size)
        update_trade_count(SYMBL, stars, trade_type)

def add_color_border(text, color):
    lines = text.split('\n')
    width = max(len(line) for line in lines)
    top_border = colored('+' + '-' * (width + 2) + '+', color)
    bottom_border = colored('+' + '-' * (width + 2) + '+', color)
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
    elif usd_size >= 30000000:
        return '  🦈🦈🦈  '
    elif usd_size >= 20000000:
        return '   🦈🦈   '
    elif usd_size >= 10000000:
        return '    🦈    '
    elif usd_size >= 5000000:
        return '🐠🐠🐠🐠🐠'
    elif usd_size >= 2500000:
        return ' 🐠🐠🐠🐠 '
    elif usd_size >= 1500000:
        return '  🐠🐠🐠  '
    elif usd_size >= 1000000:
        return '   🐠🐠   '
    else:
        return '    🐠    '

def get_attrs_trades(usd_size):
    if usd_size >= 5000000:
        return ['bold', 'blink']
    elif usd_size >= 1000000:
        return ['bold']
    else:
        return []

def update_cumulative_sum(symbol, usd_size, trade_type):
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

def format_trade_time(trade_time):
    berlin = pytz.timezone("Europe/Berlin")
    return datetime.fromtimestamp(trade_time / 1000, berlin).strftime('%H:%M:%S')

def write_to_file(filename, trade_time, symbol, price, quantity, trade_type, usd_size):
    with open(filename, 'a') as f:
        f.write(f"{trade_time},{symbol.upper()},{price},{quantity},{trade_type},{usd_size}\n")

def update_trade_count(formatted_symbol, stars, trade_type):
    key = (formatted_symbol, stars, trade_type)
    if key not in trade_count_map:
        trade_count_map[key] = 0
    trade_count_map[key] += 1

# Process Liquidation Function
async def process_liquidation(symbol, side, timestamp, usd_size):
    global cumulative_sum_map_liq
    berlin = pytz.timezone("Europe/Berlin")
    time_berlin = datetime.fromtimestamp(timestamp / 1000, berlin).strftime('%H:%M:%S')
    liquidation_type = '📈 ' if side == 'SELL' else '📉 '
    max_price = 1000000000

    formatted_symbol = symbol.ljust(6)[:6]

    if formatted_symbol not in cumulative_sum_map_liq:
        cumulative_sum_map_liq[formatted_symbol] = 0

    stars = get_liq_stars(usd_size)
    cumulative_sum = update_cumulative_sum_liq(formatted_symbol, usd_size, liquidation_type)
    cumulative_sum_str = format_cumulative_sum(cumulative_sum)
    usd_size_str = format_usd_size(usd_size, liquidation_type)
    attrs = get_attrs_liquidations(usd_size)
    stars_padding = get_stars_padding(usd_size, max_price)
    output = f"{formatted_symbol}{'    |'}{stars}{'|'}{time_berlin}{'|'}{liquidation_type}{usd_size_str}{stars_padding}{'|'} 💧🟰 {cumulative_sum_str}"

    if usd_size > 5000000:
        output = add_color_border(output, 'green')
    elif usd_size < -5000000:
        output = add_color_border(output, 'red')

    cprint(output, 'white', attrs=attrs)
    write_to_file(liq_trades_filename, timestamp, symbol, formatted_symbol, usd_size, liquidation_type, usd_size)
    update_trade_count(formatted_symbol, stars, liquidation_type)

def get_liq_stars(usd_size):
    if usd_size > 50000000:
        return '🌊💰🤿💰🌊'
    elif usd_size > 25000000:
        return '💸🌊🤿🌊💸'
    elif usd_size > 10000000:
        return '  🌊🤿🌊  '
    elif usd_size > 5000000:
        return '    🤿    '
    elif usd_size > 2500000:
        return '  🌊🌊🌊  '
    elif usd_size > 1000000:
        return '   🌊🌊   '
    elif usd_size > 500000:
        return '    🌊    '
    elif usd_size > 250000:
        return '💦💦💦💦💦'
    elif usd_size > 100000:
        return ' 💦💦💦💦 '
    elif usd_size > 50000:
        return '  💦💦💦  '
    elif usd_size > 25000:
        return '   💦💦   '
    else:
        return '    💦    '

def update_cumulative_sum_liq(symbol, usd_size, liquidation_type):
    if liquidation_type == '📉':
        cumulative_sum_map_liq[symbol] -= usd_size
    else:
        cumulative_sum_map_liq[symbol] += usd_size
    return cumulative_sum_map_liq[symbol]

def get_attrs_liquidations(usd_size):
    if usd_size >= 250000:
        return ['bold', 'blink']
    elif usd_size >= 100000:
        return ['bold']
    else:
        return []

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
    while True:
        try:
            print(f"📶  Coinbase Trades » {uri}")
            async with connect(uri, max_size=None) as websocket:  # Increase the buffer size
                subscribe_message = {
                    "type": "subscribe",
                    "channels": [{"name": "ticker", "product_ids": ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "DOGE-USD", "USDC-USD", "XRP-USD", "ADA-USD", "MATIC-USD"]}]
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
async def binance_liquidation(uri, filename):
    while True:
        try:
            print(f"📶  Binance Liquidation » {uri}")
            async with connect(uri, max_size=None) as websocket:  # Increase the buffer size
                
                while True:
                    msg = await websocket.recv()
                    order_data = json.loads(msg)['o']
                    symbol = order_data['s'].replace('USDT', '')
                    side = order_data['S']
                    timestamp = int(order_data['T'])
                    filled_quantity = float(order_data['z'])
                    price = float(order_data['p'])
                    usd_size = filled_quantity * price

                    if usd_size > 10000:
                        await process_liquidation(symbol, side, timestamp, usd_size)

                    msg_values = [str(order_data.get(key)) for key in ['s', 'S', 'o', 'f', 'q', 'p', 'ap', 'X', 'l', 'z', 'T']]
                    msg_values.append(str(usd_size))
                    with open(filename, 'a') as f:
                        trade_info = ','.join(msg_values) + '\n'
                        f.write(trade_info)
        except ConnectionClosed as e:
            print(f"📡 ❗ 🛰️: {e}.  5 Seconds 🔃")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"❗Error❗: {e}.  5 Seconds 🔃")
            await asyncio.sleep(5)

# Main Function
async def main():
    print("🔧Starte Hauptfunktion")
    tasks = []
    for symbol in symbols:
        stream_url = f"{websocket_url_base_binance}{symbol}@aggTrade"
        tasks.append(binance_trade_stream(stream_url, symbol))
    tasks.append(coinbase_trade_stream(websocket_url_base_coinbase))
    tasks.append(binance_liquidation(websocket_url_liq, liq_trades_filename))
    print("🔧Starte asyncio.gather")
    print(f"📶  Binance Trades » wss://fstream.binance.com/ws")
    await asyncio.gather(*tasks)

print("🔧Starte asyncio.run(main())")
asyncio.run(main())
print("Programm abgeschlossen")
