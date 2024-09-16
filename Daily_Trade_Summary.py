import asyncio  # Imports the asyncio library for asynchronous programming
import json  # Imports the JSON library for working with JSON data
import logging  # Imports the logging library for logging messages
import requests  # Imports the requests library for sending HTTP requests
import sqlite3  # Imports the sqlite3 library for working with SQLite databases
from datetime import datetime, timedelta  # Imports datetime and timedelta for date and time manipulation
from websockets import connect  # Imports the connect function from the websockets library for WebSocket connections
from termcolor import cprint, colored  # Imports cprint and colored for colored terminal output
from multiprocessing import Process, Queue  # Imports Process and Queue for parallel processing
import subprocess  # Imports the subprocess library for executing external processes
import time  # Imports the time library for working with time functions

# Configuration parameters
symbols = [  # Defines the symbols to be monitored
    'btcusdt', 'ethusdt', 'solusdt', 'bnbusdt', 'dogeusdt', 'usdcusdt', 'xrpusdt',
    'adausdt', 'maticusdt', 'tonusdt', 'linkusdt', 'trxusdt', 'nearusdt', 'xlmusdt',
    'rndrusdt', 'dotusdt', 'uniusdt', 'atomusdt', 'xmrusdt', 'ldousdt', 'gmxusdt'
]
websocket_url_base_binance = 'wss://fstream.binance.com/ws/'  # Base URL for Binance WebSocket connections
websocket_url_base_coinbase = 'wss://ws-feed.pro.coinbase.com'  # Base URL for Coinbase WebSocket connections

# Defines the mapping of symbol names to emojis and colored texts
name_map = {
    'BTC': '🟡BTC  ', 'ETH': '💠ETH  ', 'SOL': '👾SOL  ', 'BNB': '🔶BNB  ',
    'DOGE': '🐶DOGE ', 'USDC': '💵USDC ', 'XRP': '⚫XRP  ', 'ADA': '🔵ADA  ',
    'MATIC': '🟣MATIC', 'TON': '🎮TON  ', 'LINK': '🔗LINK ', 'TRX': '⚙️TRX  ',
    'NEAR': '🔍NEAR ', 'XLM': '🌟XLM  ', 'RNDR': '🖥️RNDR ', 'DOT': '⚪DOT  ',
    'UNI': '🦄UNI  ', 'ATOM': '⚛️ATOM ', 'XMR': '👽XMR  ', 'LDO': '🧪LDO  ',
    'GMX': '🌀GMX  '
}

# Defines the mapping of symbol names to color values
color_map = {
    'BTC': 'grey', 'ETH': 'grey', 'SOL': 'grey', 'BNB': 'grey', 'DOGE': 'grey',
    'USDC': 'grey', 'XRP': 'grey', 'ADA': 'grey', 'MATIC': 'grey', 'TON': 'grey',
    'LINK': 'grey', 'TRX': 'grey', 'NEAR': 'grey', 'XLM': 'grey', 'RNDR': 'grey',
    'DOT': 'grey', 'UNI': 'grey', 'ATOM': 'grey', 'XMR': 'grey', 'LDO': 'grey',
    'GMX': 'grey'
}

CAP_MAP = {}  # Initializes an empty map for market capitalizations

# CoinGecko API interaction
coingecko_url = 'https://api.coingecko.com/api/v3/simple/price'  # Base URL for CoinGecko API
# Defines the mapping of symbols to CoinGecko IDs
coingecko_ids = {
    'BTC': 'bitcoin', 'ETH': 'ethereum', 'SOL': 'solana', 'BNB': 'binancecoin',
    'DOGE': 'dogecoin', 'USDC': 'usd-coin', 'XRP': 'ripple', 'ADA': 'cardano',
    'MATIC': 'matic-network', 'TON': 'the-open-network', 'LINK': 'chainlink',
    'TRX': 'tron', 'NEAR': 'near', 'XLM': 'stellar', 'RNDR': 'render-token',
    'DOT': 'polkadot', 'UNI': 'uniswap', 'ATOM': 'cosmos', 'XMR': 'monero',
    'LDO': 'lido-dao', 'GMX': 'gmx'
}

def get_market_cap(symbols):
    # Creates a comma-separated list of CoinGecko IDs of the symbols
    ids = ','.join([coingecko_ids[symbol.upper().replace('USDT', '')] for symbol in symbols if symbol.upper().replace('USDT', '') in coingecko_ids])
    # Sends a GET request to the CoinGecko API
    response = requests.get(f'{coingecko_url}?ids={ids}&vs_currencies=usd&include_market_cap=true')
    data = response.json()  # Parses the JSON response
    # Creates a map of the market capitalizations of the symbols
    market_caps = {symbol.upper().replace('USDT', ''): data[coingecko_ids[symbol.upper().replace('USDT', '')]]['usd_market_cap'] for symbol in symbols if symbol.upper().replace('USDT', '') in coingecko_ids}
    return market_caps  # Returns the market capitalizations

async def update_market_caps(symbols):
    while True:  # Infinite loop to update market capitalizations
        try:
            market_caps = get_market_cap(symbols)  # Fetches the current market capitalizations
            for symbol in market_caps:  # Updates the global market capitalization map
                CAP_MAP[symbol] = market_caps[symbol]
        except Exception as e:
            logging.error(f"Error updating market caps: {e}")  # Logs errors
        await asyncio.sleep(60)  # Waits 60 seconds before the next update

# Helper functions
def determine_stars(symbol_sum, symbol):
    cap = CAP_MAP.get(symbol, 1)  # Fetches the market capitalization of the symbol
    thresholds1 = [  # Defines thresholds for positive symbol changes
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
    thresholds2 = [  # Defines thresholds for negative symbol changes
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
    for threshold, star in thresholds1:  # Determines the star rating for positive changes
        if symbol_sum >= threshold:
            return star
    for threshold, star in thresholds2:  # Determines the star rating for negative changes
        if symbol_sum <= threshold:
            return star
    return "                     "  # Returns an empty string if no thresholds are met

def sort_symbols_by_market_cap():
    return sorted(symbols, key=lambda symbol: CAP_MAP.get(symbol.upper().replace('USDT', ''), 0), reverse=True)

# Setup logging
logging.basicConfig(filename='trading_bot.log', level=logging.INFO, 
                    format='%(asctime)s:%(levelname)s:%(message)s')  # Initializes logging

# Initializes data structures to track symbol sums and history
symbol_sum_map = {symbol.upper().replace('USDT', ''): 0 for symbol in symbols}  # Initializes the symbol sum map
symbol_history_map = {symbol.upper().replace('USDT', ''): [] for symbol in symbols}  # Initializes the symbol history map
trade_type_duration = {symbol.upper().replace('USDT', ''): None for symbol in symbols}  # Initializes the trade duration maps
stars_change_time_map = {symbol.upper().replace('USDT', ''): None for symbol in symbols}  # Initializes the stars change time maps
last_stars_map = {symbol.upper().replace('USDT', ''): None for symbol in symbols}  # Initializes the last stars maps

# WebSocket connections
async def binance_trade_stream(uri, symbol):
    while True:  # Infinite loop for the WebSocket connection
        try:
            async with connect(uri) as websocket:  # Connects to the WebSocket
                logging.info(f"Connected to {uri}")  # Logs the connection

                while True:
                    try:
                        message = await websocket.recv()  # Receives a message from the WebSocket
                        data = json.loads(message)  # Parses the JSON message
                        event_time = int(data['E'])  # Extracts the event time
                        price = float(data['p'])  # Extracts the price
                        quantity = float(data['q'])  # Extracts the quantity
                        is_buyer_maker = data['m']  # Determines if the buyer is the maker
                        usd_size = price * quantity  # Calculates the USD size
                        display_symbol = symbol.upper().replace('USDT', '')  # Formats the symbol for display

                        if usd_size > 100:  # Checks if the USD size is greater than 100
                            if is_buyer_maker:
                                symbol_sum_map[display_symbol] -= usd_size  # Decreases the symbol sum if the buyer is the maker
                            else:
                                symbol_sum_map[display_symbol] += usd_size  # Increases the symbol sum if the buyer is not the maker

                            symbol_history_map[display_symbol].append((datetime.now(), symbol_sum_map[display_symbol]))  # Adds the current timestamp and symbol sum to the history
                    except Exception as e:
                        logging.error(f"Error processing message: {e}")  # Logs errors in message processing
                        await asyncio.sleep(0.5)  # Waits 0.5 seconds before the next attempt
        except Exception as e:
            logging.error(f"Connection error: {e}")  # Logs connection errors
            await asyncio.sleep(5)  # Waits 5 seconds before the next connection attempt

async def coinbase_trade_stream(uri):
    while True:  # Infinite loop for the WebSocket connection
        try:
            async with connect(uri) as websocket:  # Connects to the WebSocket
                logging.info(f"Connected to {uri}")  # Logs the connection

                subscribe_message = json.dumps({  # Creates a JSON message to subscribe to ticker data
                    "type": "subscribe",
                    "channels": [{"name": "ticker", "product_ids": [
                        "BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "DOGE-USD", "USDC-USD", "XRP-USD",
                        "ADA-USD", "MATIC-USD", "TON-USD", "LINK-USD", "TRX-USD", "NEAR-USD", "XLM-USD",
                        "RNDR-USD", "DOT-USD", "UNI-USD", "ATOM-USD", "XMR-USD", "LDO-USD", "GMX-USD"
                    ]}]
                })
                await websocket.send(subscribe_message)  # Sends the subscription message

                while True:
                    try:
                        message = await websocket.recv()  # Receives a message from the WebSocket
                        data = json.loads(message)  # Parses the JSON message
                        if data['type'] == 'ticker':  # Checks if the message is of type "ticker"
                            symbol = data['product_id'].split('-')[0]  # Extracts the symbol
                            price = float(data['price'])  # Extracts the price
                            usd_size = price * float(data['last_size'])  # Calculates the USD size
                            display_symbol = symbol.upper()  # Formats the symbol for display

                            if usd_size > 1000:  # Checks if the USD size is greater than 1000
                                is_buyer_maker = data['side'] == 'buy'  # Determines if the buyer is the maker
                                if is_buyer_maker:
                                    symbol_sum_map[display_symbol] -= usd_size  # Decreases the symbol sum if the buyer is the maker
                                else:
                                    symbol_sum_map[display_symbol] += usd_size  # Increases the symbol sum if the buyer is not the maker

                                symbol_history_map[display_symbol].append((datetime.now(), symbol_sum_map[display_symbol]))  # Adds the current timestamp and symbol sum to the history
                    except Exception as e:
                        logging.error(f"Error processing message: {e}")  # Logs errors in message processing
                        await asyncio.sleep(0.1)  # Waits 0.1 seconds before the next attempt
        except Exception as e:
            logging.error(f"Connection error: {e}")  # Logs connection errors
            await asyncio.sleep(5)  # Waits 5 seconds before the next connection attempt

async def calculate_symbol_sums(queue, start_time):
    while True:
        try:
            sorted_symbols = sort_symbols_by_market_cap()  # Sorts the symbols by market capitalization
            readable_time = datetime.now().strftime('%H:%M:%S')  # Formats the current time as a readable string
            elapsed_time = str(datetime.now() - start_time).split('.')[0]  # Calculates the elapsed time since the start
            header =  f"⏱️ {elapsed_time}                                  Daily Cumulative Sum \n"  # Creates the header text with the timer
            header += f"                                               🕰️ {readable_time}🕰️\n|Symbol | 60 Minutes | 30 Minutes | 15 Minutes | 5 Minutes  | 1 Minute   |       Trade Size      |    ⏱️    | 🟰Sum🟰"
            
            results = [header]  # Initializes the results with the header
            for symbol in sorted_symbols:  # Iterates over the sorted symbols
                SYMBL = symbol.upper().replace('USDT', '')  # Formats the symbol for display
                symbol_sum = symbol_sum_map[SYMBL]  # Fetches the current sum for the symbol

                current_time = datetime.now()  # Gets the current time
                # Filters the history for various time ranges
                history_minute = [entry for entry in symbol_history_map[SYMBL] if current_time - entry[0] <= timedelta(seconds=60)]
                history_5_minute = [entry for entry in symbol_history_map[SYMBL] if current_time - entry[0] <= timedelta(seconds=300)]
                history_15_minute = [entry for entry in symbol_history_map[SYMBL] if current_time - entry[0] <= timedelta(minutes=15)]
                history_30_minute = [entry for entry in symbol_history_map[SYMBL] if current_time - entry[0] <= timedelta(minutes=30)]
                history_hour = [entry for entry in symbol_history_map[SYMBL] if current_time - entry[0] <= timedelta(minutes=60)]

                def determine_trade_type(initial_sum, symbol_sum):
                    if initial_sum > 0:
                        percentage_change = (symbol_sum - initial_sum) / initial_sum * 100  # Calculates the percentage change
                        if -5 <= percentage_change <= 5:
                            return '   🟨     '  # Return for a change between -5% and 5%
                        elif 5 < percentage_change < 10:
                            return '        🟩'  # Return for a change between 5% and 10%
                        elif percentage_change >= 10:
                            return '      🟩🟩'  # Return for a change greater than or equal to 10%
                        elif percentage_change >= 20:
                            return '    🟩🟩🟩'  # Return for a change greater than or equal to 20%
                        elif percentage_change >= 40:
                            return '  🟩🟩🟩🟩'  # Return for a change greater than or equal to 40%
                        elif percentage_change >= 80:
                            return '🟩🟩🟩🟩🟩'  # Return for a change greater than or equal to 80%
                        
                        elif -10 < percentage_change < -5:
                            return '🟥        '  # Return for a change between -5% and -10%
                        elif percentage_change <= -10:
                            return '🟥🟥      '  # Return for a change less than or equal to -10%
                        elif percentage_change <= -20:
                            return '🟥🟥🟥    '  # Return for a change less than or equal to -20%
                        elif percentage_change <= -40:
                            return '🟥🟥🟥🟥  '  # Return for a change less than or equal to -40%
                        elif percentage_change <= -80:
                            return '🟥🟥🟥🟥🟥'  # Return for a change less than or equal to -80%
                    return '          '  # Return for all other cases

                # Determines the trade types for various time ranges
                trade_type_minute = determine_trade_type(history_minute[0][1] if history_minute else 0, symbol_sum)
                trade_type_5_minute = determine_trade_type(history_5_minute[0][1] if history_5_minute else 0, symbol_sum)
                trade_type_15_minute = determine_trade_type(history_15_minute[0][1] if history_15_minute else 0, symbol_sum)
                trade_type_30_minute = determine_trade_type(history_30_minute[0][1] if history_30_minute else 0, symbol_sum)
                trade_type_hour = determine_trade_type(history_hour[0][1] if history_hour else 0, symbol_sum)

                cumulative_sum = symbol_sum_map[SYMBL]  # Fetches the cumulative sum for the symbol
                cumulative_sum_color = 'green' if cumulative_sum > 0 else 'red'  # Determines the color based on the cumulative sum
                cumulative_sum_str = colored(f"{cumulative_sum:,.0f}$", cumulative_sum_color, attrs=['bold'], on_color='on_grey')  # Formats the cumulative sum for display

                stars = determine_stars(symbol_sum, SYMBL)  # Determines the star rating for the symbol
                stars_change_time_map[SYMBL] = datetime.now() if stars != last_stars_map[SYMBL] else stars_change_time_map[SYMBL]  # Updates the time of the last star change
                last_stars_map[SYMBL] = stars  # Updates the last star rating

                stars_duration = str(datetime.now() - stars_change_time_map[SYMBL]).split('.')[0]  # Calculates the duration since the last star change
                if datetime.now() - stars_change_time_map[SYMBL] < timedelta(seconds=60):
                    stars_duration = colored(stars_duration, 'magenta')  # Colors the duration if it is less than 60 seconds
                elif datetime.now() - stars_change_time_map[SYMBL] > timedelta(minutes=60):
                    stars_duration = colored(stars_duration, 'yellow')  # Colors the duration if it is more than 60 minutes
                else:
                    stars_duration = colored(stars_duration, 'light_grey')  # Colors the duration in other cases

                # Creates the combined output for the symbol
                combined_output = f"{name_map[SYMBL]} | {trade_type_hour} | {trade_type_30_minute} | {trade_type_15_minute} | {trade_type_5_minute} | {trade_type_minute} | {stars} | {stars_duration} | {cumulative_sum_str}"
                results.append(combined_output)  # Adds the combined output to the results
            
            queue.put(results)  # Adds the results to the queue
        except Exception as e:
            logging.error(f"Error in calculate_symbol_sums: {e}")  # Logs errors

        await asyncio.sleep(0.5)  # Waits 0.5 seconds before the next iteration

async def display_symbol_sums(queue):
    while True:
        try:
            if not queue.empty():  # Checks if the queue is not empty
                results = queue.get()  # Retrieves the results from the queue
                for line in results:
                    cprint(line, 'white', attrs=['bold'])  # Prints each line in white
        except Exception as e:
            logging.error(f"Error in display_symbol_sums: {e}")  # Logs errors

        await asyncio.sleep(0.2)  # Waits 0.2 seconds before the next iteration


# Main function
async def main():
    start_time = datetime.now()  # Saves the start time of the program
    queue = Queue()  # Creates a new queue
    tasks = [
        calculate_symbol_sums(queue, start_time),  # Adds the calculation task to the task list
        display_symbol_sums(queue),  # Adds the display task to the task list
        update_market_caps(symbols)  # Adds the update task to the task list
    ]
    for symbol in symbols:  # Iterates over the symbols
        stream_url = f"{websocket_url_base_binance}{symbol}@aggTrade"  # Creates the WebSocket URL for Binance
        tasks.append(binance_trade_stream(stream_url, symbol))  # Adds the Binance stream task to the task list

    tasks.append(coinbase_trade_stream(websocket_url_base_coinbase))  # Adds the Coinbase stream task to the task list

    await asyncio.gather(*tasks)  # Executes all tasks asynchronously

if __name__ == "__main__":
    try:
        p = Process(target=asyncio.run, args=(main(),))  # Creates a new process for the main function
        p.start()
        p.join()
    except KeyboardInterrupt:
        logging.info("Program terminated by user.")  # Logs the termination by the user
    except Exception as e:
        logging.error(f"Unexpected error: {e}")  # Logs unexpected errors

