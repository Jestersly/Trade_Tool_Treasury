import asyncio  # Importiert die asyncio-Bibliothek für asynchrone Programmierung
import json  # Importiert die JSON-Bibliothek zum Arbeiten mit JSON-Daten
import logging  # Importiert die logging-Bibliothek zum Protokollieren von Nachrichten
import requests  # Importiert die requests-Bibliothek zum Senden von HTTP-Anfragen
import sqlite3  # Importiert die sqlite3-Bibliothek zum Arbeiten mit SQLite-Datenbanken
from datetime import datetime, timedelta  # Importiert datetime und timedelta für Datums- und Zeitmanipulation
from websockets import connect  # Importiert die connect-Funktion aus der websockets-Bibliothek für WebSocket-Verbindungen
from termcolor import cprint, colored  # Importiert cprint und colored für farbige Terminalausgaben
from multiprocessing import Process, Queue  # Importiert Process und Queue für parallele Verarbeitung
import subprocess  # Importiert die subprocess-Bibliothek zum Ausführen externer Prozesse
import time  # Importiert die time-Bibliothek zum Arbeiten mit Zeitfunktionen

# Konfigurationsparameter
symbols = [  # Definiert die Symbole, die überwacht werden sollen
    'btcusdt', 'ethusdt', 'solusdt', 'bnbusdt', 'dogeusdt', 'usdcusdt', 'xrpusdt',
    'adausdt', 'maticusdt', 'tonusdt', 'linkusdt', 'trxusdt', 'nearusdt', 'xlmusdt',
    'rndrusdt', 'dotusdt', 'uniusdt', 'atomusdt', 'xmrusdt', 'ldousdt', 'gmxusdt'
]
websocket_url_base_binance = 'wss://fstream.binance.com/ws/'  # Basis-URL für Binance-WebSocket-Verbindungen
websocket_url_base_coinbase = 'wss://ws-feed.pro.coinbase.com'  # Basis-URL für Coinbase-WebSocket-Verbindungen

# Definiert das Mapping von Symbolnamen zu Emojis und farbigen Texten
name_map = {
    'BTC': '🟡BTC  ', 'ETH': '💠ETH  ', 'SOL': '👾SOL  ', 'BNB': '🔶BNB  ',
    'DOGE': '🐶DOGE ', 'USDC': '💵USDC ', 'XRP': '⚫XRP  ', 'ADA': '🔵ADA  ',
    'MATIC': '🟣MATIC', 'TON': '🎮TON  ', 'LINK': '🔗LINK ', 'TRX': '⚙️ TRX  ',
    'NEAR': '🔍NEAR ', 'XLM': '🌟XLM  ', 'RNDR': '🖥️ RNDR ', 'DOT': '⚪DOT  ',
    'UNI': '🦄UNI  ', 'ATOM': '⚛️ ATOM ', 'XMR': '👽XMR  ', 'LDO': '🧪LDO  ',
    'GMX': '🌀GMX  '
}

# Definiert das Mapping von Symbolnamen zu Farbwerten
color_map = {
    'BTC': 'grey', 'ETH': 'grey', 'SOL': 'grey', 'BNB': 'grey', 'DOGE': 'grey',
    'USDC': 'grey', 'XRP': 'grey', 'ADA': 'grey', 'MATIC': 'grey', 'TON': 'grey',
    'LINK': 'grey', 'TRX': 'grey', 'NEAR': 'grey', 'XLM': 'grey', 'RNDR': 'grey',
    'DOT': 'grey', 'UNI': 'grey', 'ATOM': 'grey', 'XMR': 'grey', 'LDO': 'grey',
    'GMX': 'grey'
}

CAP_MAP = {}  # Initialisiert eine leere Karte für Marktkapitalisierungen

# CoinGecko API-Interaktion
coingecko_url = 'https://api.coingecko.com/api/v3/simple/price'  # Basis-URL für CoinGecko-API
# Definiert das Mapping von Symbolen zu CoinGecko-IDs
coingecko_ids = {
    'BTC': 'bitcoin', 'ETH': 'ethereum', 'SOL': 'solana', 'BNB': 'binancecoin',
    'DOGE': 'dogecoin', 'USDC': 'usd-coin', 'XRP': 'ripple', 'ADA': 'cardano',
    'MATIC': 'matic-network', 'TON': 'the-open-network', 'LINK': 'chainlink',
    'TRX': 'tron', 'NEAR': 'near', 'XLM': 'stellar', 'RNDR': 'render-token',
    'DOT': 'polkadot', 'UNI': 'uniswap', 'ATOM': 'cosmos', 'XMR': 'monero',
    'LDO': 'lido-dao', 'GMX': 'gmx'
}

def get_market_cap(symbols):
    # Erzeugt eine kommagetrennte Liste der CoinGecko-IDs der Symbole
    ids = ','.join([coingecko_ids[symbol.upper().replace('USDT', '')] for symbol in symbols if symbol.upper().replace('USDT', '') in coingecko_ids])
    # Sendet eine GET-Anfrage an die CoinGecko-API
    response = requests.get(f'{coingecko_url}?ids={ids}&vs_currencies=usd&include_market_cap=true')
    data = response.json()  # Parst die JSON-Antwort
    # Erzeugt eine Karte der Marktkapitalisierungen der Symbole
    market_caps = {symbol.upper().replace('USDT', ''): data[coingecko_ids[symbol.upper().replace('USDT', '')]]['usd_market_cap'] for symbol in symbols if symbol.upper().replace('USDT', '') in coingecko_ids}
    return market_caps  # Gibt die Marktkapitalisierungen zurück

async def update_market_caps(symbols):
    while True:  # Endlosschleife zum Aktualisieren der Marktkapitalisierungen
        try:
            market_caps = get_market_cap(symbols)  # Ruft die aktuellen Marktkapitalisierungen ab
            for symbol in market_caps:  # Aktualisiert die globale Marktkapitalisierungskarte
                CAP_MAP[symbol] = market_caps[symbol]
        except Exception as e:
            logging.error(f"Error updating market caps: {e}")  # Protokolliert Fehler
        await asyncio.sleep(60)  # Wartet 60 Sekunden vor der nächsten Aktualisierung

# Hilfsfunktionen
def determine_stars(symbol_sum, symbol):
    cap = CAP_MAP.get(symbol, 1)  # Ruft die Marktkapitalisierung des Symbols ab
    thresholds1 = [  # Definiert Schwellenwerte für positive Symboländerungen
        (cap / 10, '9️⃣ 📈📈📈📈📈📈📈📈📈 '),
        (cap / 100, '8️⃣ 📈📈📈📈📈📈📈📈   '),
        (cap / 1000, '7️⃣ 📈📈📈📈📈📈📈     '),
        (cap / 10000, '6️⃣ 📈📈📈📈📈📈       '),
        (cap / 100000, '5️⃣ 📈📈📈📈📈         '),
        (cap / 1000000, '4️⃣ 📈📈📈📈           '),
        (cap / 10000000, '3️⃣ 📈📈📈             '),
        (cap / 100000000, '2️⃣ 📈📈               '),
        (cap / 1000000000, '1️⃣ 📈                 '),
    ]
    thresholds2 = [  # Definiert Schwellenwerte für negative Symboländerungen
        (-cap / 10, '9️⃣ 📉📉📉📉📉📉📉📉📉 '),
        (-cap / 100, '8️⃣ 📉📉📉📉📉📉📉📉   '),
        (-cap / 1000, '7️⃣ 📉📉📉📉📉📉📉     '),
        (-cap / 10000, '6️⃣ 📉📉📉📉📉📉       '),
        (-cap / 100000, '5️⃣ 📉📉📉📉📉         '),
        (-cap / 1000000, '4️⃣ 📉📉📉📉           '),
        (-cap / 10000000, '3️⃣ 📉📉📉             '),
        (-cap / 100000000, '2️⃣ 📉📉               '),
        (-cap / 1000000000, '1️⃣ 📉                 '),
    ]
    for threshold, star in thresholds1:  # Bestimmt das Star-Rating für positive Änderungen
        if symbol_sum >= threshold:
            return star
    for threshold, star in thresholds2:  # Bestimmt das Star-Rating für negative Änderungen
        if symbol_sum <= threshold:
            return star
    return "                     "  # Gibt eine leere Zeichenkette zurück, wenn keine Schwellenwerte erreicht werden

def sort_symbols_by_market_cap():
    return sorted(symbols, key=lambda symbol: CAP_MAP.get(symbol.upper().replace('USDT', ''), 0), reverse=True)

# Setup logging
logging.basicConfig(filename='trading_bot.log', level=logging.INFO, 
                    format='%(asctime)s:%(levelname)s:%(message)s')  # Initialisiert das Logging

# Initialisiert Datenstrukturen zur Verfolgung der Symbolsummen und -historie
symbol_sum_map = {symbol.upper().replace('USDT', ''): 0 for symbol in symbols}  # Initialisiert die Symbolsummenkarte
symbol_history_map = {symbol.upper().replace('USDT', ''): [] for symbol in symbols}  # Initialisiert die Symbolhistoriekarte
trade_type_duration = {symbol.upper().replace('USDT', ''): None for symbol in symbols}  # Initialisiert die Handelsdauerkarten
stars_change_time_map = {symbol.upper().replace('USDT', ''): None for symbol in symbols}  # Initialisiert die Karten für Sternänderungszeiten
last_stars_map = {symbol.upper().replace('USDT', ''): None for symbol in symbols}  # Initialisiert die Karten für die letzten Sterne

# WebSocket-Verbindungen
async def binance_trade_stream(uri, symbol):
    while True:  # Endlosschleife für die WebSocket-Verbindung
        try:
            async with connect(uri) as websocket:  # Verbindet sich mit dem WebSocket
                logging.info(f"Connected to {uri}")  # Protokolliert die Verbindung

                while True:
                    try:
                        message = await websocket.recv()  # Empfängt eine Nachricht vom WebSocket
                        data = json.loads(message)  # Parst die JSON-Nachricht
                        event_time = int(data['E'])  # Extrahiert die Ereigniszeit
                        price = float(data['p'])  # Extrahiert den Preis
                        quantity = float(data['q'])  # Extrahiert die Menge
                        is_buyer_maker = data['m']  # Bestimmt, ob der Käufer der Maker ist
                        usd_size = price * quantity  # Berechnet die USD-Größe
                        display_symbol = symbol.upper().replace('USDT', '')  # Formatiert das Symbol zur Anzeige

                        if usd_size > 100:  # Überprüft, ob die USD-Größe größer als 100 ist
                            if is_buyer_maker:
                                symbol_sum_map[display_symbol] -= usd_size  # Verringert die Symbolsumme, wenn der Käufer der Maker ist
                            else:
                                symbol_sum_map[display_symbol] += usd_size  # Erhöht die Symbolsumme, wenn der Käufer nicht der Maker ist

                            symbol_history_map[display_symbol].append((datetime.now(), symbol_sum_map[display_symbol]))  # Fügt den aktuellen Zeitstempel und die Symbolsumme zur Historie hinzu
                    except Exception as e:
                        logging.error(f"Error processing message: {e}")  # Protokolliert Fehler beim Nachrichtenverarbeiten
                        await asyncio.sleep(0.5)  # Wartet 0,5 Sekunden vor dem nächsten Versuch
        except Exception as e:
            logging.error(f"Connection error: {e}")  # Protokolliert Verbindungsfehler
            await asyncio.sleep(5)  # Wartet 5 Sekunden vor dem nächsten Verbindungsversuch

async def coinbase_trade_stream(uri):
    while True:  # Endlosschleife für die WebSocket-Verbindung
        try:
            async with connect(uri) as websocket:  # Verbindet sich mit dem WebSocket
                logging.info(f"Connected to {uri}")  # Protokolliert die Verbindung

                subscribe_message = json.dumps({  # Erzeugt eine JSON-Nachricht zum Abonnieren von Ticker-Daten
                    "type": "subscribe",
                    "channels": [{"name": "ticker", "product_ids": [
                        "BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "DOGE-USD", "USDC-USD", "XRP-USD",
                        "ADA-USD", "MATIC-USD", "TON-USD", "LINK-USD", "TRX-USD", "NEAR-USD", "XLM-USD",
                        "RNDR-USD", "DOT-USD", "UNI-USD", "ATOM-USD", "XMR-USD", "LDO-USD", "GMX-USD"
                    ]}]
                })
                await websocket.send(subscribe_message)  # Sendet die Abonnementnachricht

                while True:
                    try:
                        message = await websocket.recv()  # Empfängt eine Nachricht vom WebSocket
                        data = json.loads(message)  # Parst die JSON-Nachricht
                        if data['type'] == 'ticker':  # Überprüft, ob die Nachricht vom Typ "ticker" ist
                            symbol = data['product_id'].split('-')[0]  # Extrahiert das Symbol
                            price = float(data['price'])  # Extrahiert den Preis
                            usd_size = price * float(data['last_size'])  # Berechnet die USD-Größe
                            display_symbol = symbol.upper()  # Formatiert das Symbol zur Anzeige

                            if usd_size > 1000:  # Überprüft, ob die USD-Größe größer als 1000 ist
                                is_buyer_maker = data['side'] == 'buy'  # Bestimmt, ob der Käufer der Maker ist
                                if is_buyer_maker:
                                    symbol_sum_map[display_symbol] -= usd_size  # Verringert die Symbolsumme, wenn der Käufer der Maker ist
                                else:
                                    symbol_sum_map[display_symbol] += usd_size  # Erhöht die Symbolsumme, wenn der Käufer nicht der Maker ist

                                symbol_history_map[display_symbol].append((datetime.now(), symbol_sum_map[display_symbol]))  # Fügt den aktuellen Zeitstempel und die Symbolsumme zur Historie hinzu
                    except Exception as e:
                        logging.error(f"Error processing message: {e}")  # Protokolliert Fehler beim Nachrichtenverarbeiten
                        await asyncio.sleep(0.1)  # Wartet 0,1 Sekunden vor dem nächsten Versuch
        except Exception as e:
            logging.error(f"Connection error: {e}")  # Protokolliert Verbindungsfehler
            await asyncio.sleep(5)  # Wartet 5 Sekunden vor dem nächsten Verbindungsversuch

async def calculate_symbol_sums(queue, start_time):
    while True:
        try:
            sorted_symbols = sort_symbols_by_market_cap()  # Sortiert die Symbole nach Marktkapitalisierung
            readable_time = datetime.now().strftime('%H:%M:%S')  # Formatiert die aktuelle Zeit als lesbare Zeichenkette
            elapsed_time = str(datetime.now() - start_time).split('.')[0]  # Berechnet die vergangene Zeit seit dem Start
            header =  f"⏱️ {elapsed_time}                                  Daily Cumulative Sum \n"  # Erstellt den Header-Text mit dem Timer
            header += f"                                               🕰️ {readable_time}🕰️\n|Symbol | 60 Minutes | 30 Minutes | 15 Minutes | 5 Minutes  | 1 Minute   |       Trade Size      |    ⏱️    | 🟰Sum🟰"
            
            results = [header]  # Initialisiert die Ergebnisse mit dem Header
            for symbol in sorted_symbols:  # Iteriert über die sortierten Symbole
                SYMBL = symbol.upper().replace('USDT', '')  # Formatiert das Symbol zur Anzeige
                symbol_sum = symbol_sum_map[SYMBL]  # Ruft die aktuelle Summe für das Symbol ab

                current_time = datetime.now()  # Holt die aktuelle Zeit
                # Filtert die Historie für verschiedene Zeiträume
                history_minute = [entry for entry in symbol_history_map[SYMBL] if current_time - entry[0] <= timedelta(seconds=60)]
                history_5_minute = [entry for entry in symbol_history_map[SYMBL] if current_time - entry[0] <= timedelta(seconds=300)]
                history_15_minute = [entry for entry in symbol_history_map[SYMBL] if current_time - entry[0] <= timedelta(minutes=15)]
                history_30_minute = [entry for entry in symbol_history_map[SYMBL] if current_time - entry[0] <= timedelta(minutes=30)]
                history_hour = [entry for entry in symbol_history_map[SYMBL] if current_time - entry[0] <= timedelta(minutes=60)]

                def determine_trade_type(initial_sum, symbol_sum):
                    if initial_sum > 0:
                        percentage_change = (symbol_sum - initial_sum) / initial_sum * 100  # Berechnet die prozentuale Änderung
                        if -5 <= percentage_change <= 5:
                            return '   🟨     '  # Rückgabe für eine Änderung zwischen -5% und 5%
                        elif 5 < percentage_change < 10:
                            return '        🟩'  # Rückgabe für eine Änderung zwischen 5% und 10%
                        elif percentage_change >= 10:
                            return '      🟩🟩'  # Rückgabe für eine Änderung größer oder gleich 10%
                        elif percentage_change >= 20:
                            return '    🟩🟩🟩'  # Rückgabe für eine Änderung größer oder gleich 20%
                        elif percentage_change >= 40:
                            return '  🟩🟩🟩🟩'  # Rückgabe für eine Änderung größer oder gleich 40%
                        elif percentage_change >= 80:
                            return '🟩🟩🟩🟩🟩'  # Rückgabe für eine Änderung größer oder gleich 80%
                        
                        elif -10 < percentage_change < -5:
                            return '🟥        '  # Rückgabe für eine Änderung zwischen -5% und -10%
                        elif percentage_change <= -10:
                            return '🟥🟥      '  # Rückgabe für eine Änderung kleiner oder gleich -10%
                        elif percentage_change <= -20:
                            return '🟥🟥🟥    '  # Rückgabe für eine Änderung kleiner oder gleich -20%
                        elif percentage_change <= -40:
                            return '🟥🟥🟥🟥  '  # Rückgabe für eine Änderung kleiner oder gleich -40%
                        elif percentage_change <= -80:
                            return '🟥🟥🟥🟥🟥'  # Rückgabe für eine Änderung kleiner oder gleich -80%
                    return '          '  # Rückgabe für alle anderen Fälle

                # Bestimmt die Handelstypen für verschiedene Zeiträume
                trade_type_minute = determine_trade_type(history_minute[0][1] if history_minute else 0, symbol_sum)
                trade_type_5_minute = determine_trade_type(history_5_minute[0][1] if history_5_minute else 0, symbol_sum)
                trade_type_15_minute = determine_trade_type(history_15_minute[0][1] if history_15_minute else 0, symbol_sum)
                trade_type_30_minute = determine_trade_type(history_30_minute[0][1] if history_30_minute else 0, symbol_sum)
                trade_type_hour = determine_trade_type(history_hour[0][1] if history_hour else 0, symbol_sum)

                cumulative_sum = symbol_sum_map[SYMBL]  # Ruft die kumulative Summe für das Symbol ab
                cumulative_sum_color = 'green' if cumulative_sum > 0 else 'red'  # Bestimmt die Farbe basierend auf der kumulativen Summe
                cumulative_sum_str = colored(f"{cumulative_sum:,.0f}$", cumulative_sum_color, attrs=['bold'], on_color='on_grey')  # Formatiert die kumulative Summe zur Anzeige

                stars = determine_stars(symbol_sum, SYMBL)  # Bestimmt die Sternbewertung für das Symbol
                stars_change_time_map[SYMBL] = datetime.now() if stars != last_stars_map[SYMBL] else stars_change_time_map[SYMBL]  # Aktualisiert die Zeit der letzten Sternänderung
                last_stars_map[SYMBL] = stars  # Aktualisiert die letzte Sternbewertung

                stars_duration = str(datetime.now() - stars_change_time_map[SYMBL]).split('.')[0]  # Berechnet die Dauer seit der letzten Sternänderung
                if datetime.now() - stars_change_time_map[SYMBL] < timedelta(seconds=60):
                    stars_duration = colored(stars_duration, 'magenta')  # Färbt die Dauer, wenn sie weniger als 60 Sekunden beträgt
                elif datetime.now() - stars_change_time_map[SYMBL] > timedelta(minutes=60):
                    stars_duration = colored(stars_duration, 'yellow')  # Färbt die Dauer, wenn sie mehr als 60 Minuten beträgt
                else:
                    stars_duration = colored(stars_duration, 'light_grey')  # Färbt die Dauer in anderen Fällen

                # Erstellt die kombinierte Ausgabe für das Symbol
                combined_output = f"{name_map[SYMBL]} | {trade_type_hour} | {trade_type_30_minute} | {trade_type_15_minute} | {trade_type_5_minute} | {trade_type_minute} | {stars} | {stars_duration} | {cumulative_sum_str}"
                results.append(combined_output)  # Fügt die kombinierte Ausgabe zu den Ergebnissen hinzu
            
            queue.put(results)  # Fügt die Ergebnisse zur Queue hinzu
        except Exception as e:
            logging.error(f"Error in calculate_symbol_sums: {e}")  # Protokolliert Fehler

        await asyncio.sleep(0.5)  # Wartet 0,5 Sekunden vor dem nächsten Durchlauf

async def display_symbol_sums(queue):
    while True:
        try:
            if not queue.empty():  # Überprüft, ob die Queue nicht leer ist
                results = queue.get()  # Holt die Ergebnisse aus der Queue
                for line in results:
                    cprint(line, 'white', attrs=['bold'])  # Druckt jede Zeile in Weiß
        except Exception as e:
            logging.error(f"Error in display_symbol_sums: {e}")  # Protokolliert Fehler

        await asyncio.sleep(0.2)  # Wartet 0,2 Sekunden vor dem nächsten Durchlauf


# Hauptfunktion
async def main():
    start_time = datetime.now()  # Speichert die Startzeit des Programms
    queue = Queue()  # Erstellt eine neue Queue
    tasks = [
        calculate_symbol_sums(queue, start_time),  # Fügt die Berechnungsaufgabe zur Aufgabenliste hinzu
        display_symbol_sums(queue),  # Fügt die Anzeigeaufgabe zur Aufgabenliste hinzu
        update_market_caps(symbols)  # Fügt die Aktualisierungsaufgabe zur Aufgabenliste hinzu
    ]
    for symbol in symbols:  # Iteriert über die Symbole
        stream_url = f"{websocket_url_base_binance}{symbol}@aggTrade"  # Erstellt die WebSocket-URL für Binance
        tasks.append(binance_trade_stream(stream_url, symbol))  # Fügt die Binance-Stream-Aufgabe zur Aufgabenliste hinzu

    tasks.append(coinbase_trade_stream(websocket_url_base_coinbase))  # Fügt die Coinbase-Stream-Aufgabe zur Aufgabenliste hinzu

    await asyncio.gather(*tasks)  # Führt alle Aufgaben asynchron aus

if __name__ == "__main__":
    try:
        p = Process(target=asyncio.run, args=(main(),))  # Erstellt einen neuen Prozess für die Hauptfunktion
        p.start()
        p.join()
    except KeyboardInterrupt:
        logging.info("Program terminated by user.")  # Protokolliert die Beendigung durch den Benutzer
    except Exception as e:
        logging.error        (f"Unexpected error: {e}")  # Protokolliert unerwartete Fehler
