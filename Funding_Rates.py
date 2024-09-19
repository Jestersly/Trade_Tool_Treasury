import asyncio
import json
from datetime import datetime
from websockets import connect, ConnectionClosed
from rich.console import Console
from rich.table import Table
from rich.live import Live
from termcolor import colored

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

websocket_url_base_binance = 'wss://fstream.binance.com/ws/'

shared_symbol_data = {symbol: {} for symbol in symbols}
print_lock = asyncio.Lock()

console = Console()

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


# Placeholder for user-selected symbols
selected_symbols = []
selected_symbols_formatted = []
All_symbols = False

async def binance_funding_stream(symbol):
    websocket_url = f'{websocket_url_base_binance}{symbol}@markPrice'
    while True:
        try:
            async with connect(websocket_url) as websocket:
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    event_time = datetime.fromtimestamp(data['E'] / 1000).strftime("%H:%M:%S")
                    symbol_display = data['s'].replace('USDT', '')
                    funding_rate = float(data['r'])
                    eight_hour_funding_rate = (funding_rate) * 100
                    daily_funding_rate = (funding_rate * 3) * 100
                    weekly_funding_rate = (funding_rate * 3 * 7) * 100
                    monthly_funding_rate = (funding_rate * 3 * 30) * 100
                    yearly_funding_rate = (funding_rate * 3 * 365) * 100
                    stars = '🟨    ' if -10 < yearly_funding_rate < 10 else (
                            '🟩    ' if -20 < yearly_funding_rate <= -10 else (
                            '🟩🟩  ' if -30 < yearly_funding_rate <= -20 else (
                            '🟩🟩🟩' if -40 < yearly_funding_rate <= -30 else (
                            '🟩🟩🟩🟩' if -50 < yearly_funding_rate <= -40 else (
                            '🟩🟩🟩🟩🟩' if yearly_funding_rate <= -50 else (
                            '🟥    ' if 20 > yearly_funding_rate >= 10 else (
                            '🟥🟥  ' if 30 > yearly_funding_rate >= 20 else (
                            '🟥🟥🟥' if 40 > yearly_funding_rate >= 30 else(
                            '🟥🟥🟥🟥' if 50 > yearly_funding_rate >= 40 else (
                            '🟥🟥🟥🟥🟥'))))))))))

                    async with print_lock:
                        previous_data = shared_symbol_data[symbol]
                        color = 'on_grey'
                        if previous_data:
                            previous_rate = previous_data.get('yearly_funding_rate', None)
                            if previous_rate is not None:
                                if yearly_funding_rate < previous_rate:
                                    color = 'on_green'
                                elif yearly_funding_rate > previous_rate:
                                    color = 'on_red'

                        shared_symbol_data[symbol] = {
                            'symbol_display': name_map.get(symbol_display, symbol_display),
                            'stars': stars,
                            'yearly_funding_rate': yearly_funding_rate,
                            'eight_hour_funding_rate': eight_hour_funding_rate,
                            'daily_funding_rate': daily_funding_rate,
                            'weekly_funding_rate': weekly_funding_rate,
                            'monthly_funding_rate': monthly_funding_rate,
                            'event_time': event_time,
                            'color': color
                        }
                        
        except ConnectionClosed:
            console.print(f"[red]WebSocket connection closed for {symbol}. Reconnecting...[/]")
            await asyncio.sleep(5)  # wait before reconnecting
        except Exception as e:
            console.print(f"[red]Error: {e}[/]")
            await asyncio.sleep(1)

def get_sorted_symbols():
    # Sort the symbols based on their yearly funding rate
    return sorted(shared_symbol_data.items(), key=lambda x: x[1].get('yearly_funding_rate', float('-inf')), reverse=True)

def create_table():
    """Creates and returns the funding rates table."""
    current_time = datetime.now().strftime("%H:%M:%S")
    table = Table(show_header=True, header_style="bold white", title=f"🚀 Funding Rates {current_time} ️🚀", title_style="bold white", show_lines=True)
    table.add_column("Symbol", style="white", justify="center")
    table.add_column("⭐Magnitude", style="green")
    table.add_column("⏱ 8-Hour", justify="center")
    table.add_column("⏱ Daily", justify="center")
    table.add_column("⏱ Weekly", justify="center")
    table.add_column("⏱ Monthly", justify="center")
    table.add_column("⏱ Yearly", justify="center")
    
    sorted_symbols = get_sorted_symbols()

    for sym, data in sorted_symbols:
        if data:
            table.add_row(
                data['symbol_display'],
                data['stars'],
                f"{data['eight_hour_funding_rate']:.2f}%",
                f"{data['daily_funding_rate']:.2f}%",
                f"{data['weekly_funding_rate']:.2f}%",
                f"{data['monthly_funding_rate']:.2f}%",
                f"{data['yearly_funding_rate']:.2f}%"
            )
    
    return table

async def update_display():
    """Continuously updates the displayed table."""
    with Live(create_table(), refresh_per_second=1, console=console) as live:
        while True:
            await asyncio.sleep(1)
            live.update(create_table())

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


async def main():
    select_symbols()
    tasks = [binance_funding_stream(symbol) for symbol in selected_symbols]
    tasks.append(update_display())
    await asyncio.gather(*tasks)

asyncio.run(main())
