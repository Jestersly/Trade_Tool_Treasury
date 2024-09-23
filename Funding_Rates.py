import asyncio
import json
from datetime import datetime
from websockets import connect, ConnectionClosed
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Header, Footer
from textual.containers import Container
import logging
from tabulate import tabulate
import math
import pyfiglet
from termcolor import colored

# Konfiguration
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

# Initialisierung der Variablen
name_map = {
    'BTC': '🟡BTC', 'ETH': '💠ETH', 'SOL': '👾SOL', 'BNB': '🔶BNB', 'DOGE': '🐶DOGE',
    'USDC': '💵USDC', 'XRP': '⚫XRP', 'ADA': '🔵ADA', 'MATIC': '🟣MATIC',
    'TON': '🎮TON', 'LINK': '🔗LINK', 'TRX': '⚙️TRX', 'NEAR': '🔍NEAR', 'XLM': '🌟XLM',
    'RNDR': '🎨RNDR', 'DOT': '⚪DOT', 'UNI': '🦄UNI', 'ATOM': '⚛️ATOM', 'XMR': '👽XMR',
    'LDO': '🧪LDO', 'GMX': '🌀GMX', 'LTC': '🌕LTC', 'AVAX': '🏔️AVAX', 'BCH': '💰BCH',
    'VET': '♻️VET', 'FIL': '📁FIL', 'ETC': '⛏️ETC', 'ALGO': '🔺ALGO', 'XTZ': '🏺XTZ',
    'EOS': '🌐EOS', 'AAVE': '🏦AAVE', 'MKR': '🏭MKR', 'THETA': '📺THETA', 'AXS': '🕹️AXS',
    'SAND': '🏖️SAND', 'ICP': '🌐ICP', 'SHIB': '🐾SHIB', 'APT': '🚀APT', 'GRT': '📊GRT',
    'ENJ': '🎮ENJ', 'CHZ': '⚽CHZ', 'MANA': '🌐MANA', 'SUSHI': '🍣SUSHI', 'BAT': '🦇BAT',
    'ZEC': '💰ZEC', 'DASH': '⚡DASH', 'NEO': '💹NEO', 'IOTA': '🔗IOTA', 'OMG': '😮OMG',
    'CAKE': '🍰CAKE', 'STX': '📚STX', 'SNX': '💎SNX', 'COMP': '🏦COMP', 'ZIL': '💠ZIL',
    'KSM': '🪶KSM', 'REN': '🔄REN'
}

# Konfigurieren des Loggers
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

# Platzhalter für vom Benutzer ausgewählte Symbole
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
                    eight_hour_funding_rate = funding_rate * 100
                    yearly_funding_rate = funding_rate * 3 * 365 * 100

                    # Bestimmen der Sterne basierend auf dem Jahres-Finanzierungsrate
                    stars = '🟨    ' if -10 < yearly_funding_rate < 10 else (
                            '🟩    ' if -20 < yearly_funding_rate <= -10 else (
                            '🟩🟩  ' if -30 < yearly_funding_rate <= -20 else (
                            '🟩🟩🟩' if -40 < yearly_funding_rate <= -30 else (
                            '🟩🟩🟩🟩' if -50 < yearly_funding_rate <= -40 else (
                            '🟩🟩🟩🟩🟩' if yearly_funding_rate <= -50 else (
                            '🟥    ' if 20 > yearly_funding_rate >= 10 else (
                            '🟥🟥  ' if 30 > yearly_funding_rate >= 20 else (
                            '🟥🟥🟥' if 40 > yearly_funding_rate >= 30 else (
                            '🟥🟥🟥🟥' if 50 > yearly_funding_rate >= 40 else (
                            '🟥🟥🟥🟥🟥'))))))))))

                    async with print_lock:
                        previous_data = shared_symbol_data[symbol]
                        color = 'grey'
                        if previous_data:
                            previous_rate = previous_data.get('eight_hour_funding_rate', None)
                            if previous_rate is not None:
                                if yearly_funding_rate < previous_rate:
                                    color = 'green'
                                elif yearly_funding_rate > previous_rate:
                                    color = 'red'

                        shared_symbol_data[symbol] = {
                            'symbol_display': name_map.get(symbol_display, symbol_display),
                            'stars': stars,
                            'eight_hour_funding_rate': eight_hour_funding_rate,
                            'yearly_funding_rate': yearly_funding_rate,
                            'color': color
                        }
        except ConnectionClosed:
            logging.warning(f"WebSocket-Verbindung für {symbol} geschlossen. Wiederverbindung wird versucht...")
            await asyncio.sleep(5)
        except Exception as e:
            logging.error(f"Fehler bei {symbol}: {e}")
            await asyncio.sleep(1)


def select_symbols():
    """
    Allows the user to select which symbols to include in the query.
    """
    title = ' Funding Rates '

    # Färbe den ASCII-Text blau-weiß (blau als Textfarbe, weiß als Hintergrund)
    ascii_title = '🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏\n' + pyfiglet.figlet_format(title) + '🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏🃏'
    print(colored(ascii_title, 'green', 'on_white', attrs=['bold']))

    # Verwende pyfiglet, um den Titel in ASCII-Kunstform darzustellen
    print("""
                   🪙         
                 🟩🟩🟩       
                 🟩🟩🟩       
                 🟩🟩🟩      🪙   
                 🟩🟩🟩    🟨🟨🟨 
                 🟩🟩🟩    🟨🟨🟨 
                 🟩🟩🟩    🟨🟨🟨      🪙
                 🟩🟩🟩    🟨🟨🟨    🟥🟥🟥
                 🟩🟩🟩    🟨🟨🟨    🟥🟥🟥
                 🟩🟩🟩    🟨🟨🟨    🟥🟥🟥
""")
    print("             📊 Funding Rates get initialized 📊\n")
    
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

    global selected_symbols, selected_symbols_formatted, All_symbols
    selected_symbols = []

    while True:
        user_input = input("Select symbol: ").strip().upper()
        if user_input == 'ALL':
            selected_symbols = list(name_map.keys())  # Verwende alle Symbole
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

def get_sorted_symbols():
    # Sortieren der Symbole basierend auf ihrem Jahres-Finanzierungsrate
    return sorted(shared_symbol_data.items(), key=lambda x: x[1].get('yearly_funding_rate', float('-inf')), reverse=True)

class FundingRatesApp(App):
    """Textual App zur Anzeige der Funding Rates."""

    # Entfernen der CSS_PATH-Zeile
    # CSS_PATH = "funding_rates.css"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.table = DataTable()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(self.table)
        yield Footer()

    async def on_mount(self) -> None:
        # Definieren der Spalten der Tabelle mit fester Breite
        self.table.add_column("⭐Magnitude", width=15)
        self.table.add_column("⏱ 8-Hour", width=12)
        self.table.add_column("Symbol", width=10)
        # Optional: Weitere Spalten hinzufügen

        # Starten der Aktualisierungsintervalls
        self.set_interval(1, self.refresh_table)

    async def refresh_table(self) -> None:
        async with print_lock:
            sorted_symbols = get_sorted_symbols()
            self.table.clear()  # Entfernt alle vorhandenen Zeilen

            for sym, data in sorted_symbols:
                if data:
                    # Anwenden der Farbe auf das Symbol basierend auf dem Finanzierungsrate
                    if data['color'] == 'green':
                        symbol = f"[green]{data['symbol_display']}[/green]"
                    elif data['color'] == 'red':
                        symbol = f"[red]{data['symbol_display']}[/red]"
                    else:
                        symbol = data['symbol_display']

                    # Formatieren des Symbols mit Padding, um eine einheitliche Länge zu gewährleisten
                    symbol_padded = symbol.ljust(8)  # Passen Sie die Zahl an die gewünschte Länge an

                    # Rich-Markup für die Ausrichtung
                    symbol_aligned = f"[center]{symbol_padded}[/center]"
                    stars_aligned = f"[center]{data['stars']}[/center]"
                    funding_rate_aligned = f"[center]{data['eight_hour_funding_rate']:.6f}%[/center]"

                    # Hinzufügen der Zeile mit positional arguments
                    self.table.add_row(
                        stars_aligned,
                        funding_rate_aligned,
                        symbol_aligned,
                        key=sym  # Verwenden des Symbols als eindeutiger Schlüssel
                    )

    async def on_key(self, event):
        """Beenden der Anwendung durch Drücken der 'q' Taste."""
        if event.key == "q":
            await self.shutdown()

async def main():
    select_symbols()
    tasks = [binance_funding_stream(symbol) for symbol in selected_symbols]
    # Starten der Textual-App in einem separaten Task
    app = FundingRatesApp()
    tasks.append(app.run_async())

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())

