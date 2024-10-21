# Trade Treasuries💰⚓


## Introductions🔰

My provided code offers a comprehensive understanding of cryptocurrency market flows, setting itself apart from standard trading indicators. Unlike typical tools, this code enables you to monitor each trade with greater detail, tracking direction, volume, and scale more effectively. You will get a closer look at "The Smart Money" and the "Big Whales" while keeping track of the overall market direction. While it does not replace Candlestick-Charts, it complements them by offering greater insights into the deep Ocean of cryptocurrency trading. Best of all, this advanced tool is available to you at no cost, giving you a significant edge in your trading strategy. If you find these tools valuable, please consider supporting my work so I can continue developing solutions that democratize access to vital market data for everyone.

## Important❗
- You can only choose between a given number of cryptocurrencies (more than enough)                       
- Some terminals represent the emojis a bit differently such that you may have to indent them correctly (add or delete space between the emoji and the name in "name_map")|Trade Trail🛤️ & Trade Trawler🚢: Line 47|
- I use the timezone "Europe/Berlin". I don't think that this is the case for everybody. |Trade Trail🛤️: Line 215|Trade Trawler🚢:Line 197|
- The market data for **trades** is provided via **Binance, Coinbase, Kraken and Bitfinex** WebSockets. The market data for **liquidations and funding rates** are only provided via **Binance** WebSocket
- Inside the **Trade Trail** Code at Line 38 is an absolute Path defined for exporting received data into a .xlsx file, which probably doesn't exist on your computer. Change this to any Path you want to save the data in 
- To be capable of starting these programs you need to install some Python libraries. I recommend creating a virtual environment via conda or env before installing, but this isn't necessary.
### 📚Library Installation Guide:
Global Installation:
```python
pip install asyncio jsonlib pytz websockets termcolor colorama rich pandas xlsxwriter tabulate pyfiglet
```
Installation in virtual Environment:
```python
pip install conda
```
```python
conda create --name Trade_Tools
conda activate Trade_Tools
conda install asyncio jsonlib pytz websockets termcolor colorama rich pandas xlsxwriter tabulate pyfiglet
```
If you want to start the Code after a global installation:
- open temrinal
```python
python <Path_of_the_code>
```
If you want to start the Code after installion in a virtaul environment:
-open terminal
```python
conda activate Trade_Tool_Treasury
python <Path_of_the_code>
```
-----------------------------------------------------------------------


# **Trade Trawler🚢      |⭐⭐⭐⭐|**


This masterpiece of market visualization allows you to catch every trade, going through Binance, Coinbase, Kraken and Bitfinex, and list them in a table. These trades and liquidations get listed and calculated in real-time. You can specify an interval in which the program should calculate and list the trades and liquidations to get a broader view of long-time and short-time market behavior. The border will be colored green if the spread between long-trades (ask) and short-trades (put) is positive and red if the spread is negative. The same is true for liquidations. The listed trades and liquidations are sorted after the Total-USD-Size. The Parameter "Avg. USD Size per minute" gives information about how much people bought or sold on average each minute and not how much was bought or sold the last minute. I guess the most is self-explanatory. Start the Code and you will be advised and delighted
                                                                                                          


### At the beginning of the Code you have to set 4 requirements:

❓"Choose Symbols: "❓                                                                                              
↪️ You can choose cryptocurrencies from a given list. if you chose every symbol you wanted you can write "done" to go to the next step. If you type "all" you choose all available symbols
                                                                   
❓"Please enter the threshold value for 'usd_size' on trades: "❓                                                                                              
↪️ You will only see trades that are bigger than the specified value
                                                                          
❓"Please enter the interval for exportation and calculation in seconds: "❓                                                                                                            
↪️ Here you can specify the Period in which the Code should export the data and calculate some Indicators (Total trades/liquidations, Differences, Avg. trades/liquidations, counts and sizes, time since starting the Program etc.). After the specified interval you will get an Overview of all trades and liquidation since starting the program



## Code Breakdown (Step by Step):

1. **Imports and Initialization**:
    - Imports essential modules for handling asynchronous tasks (`asyncio`), JSON processing (`json`), and time management (`datetime`, `pytz`). 
    - Websocket connections are managed using `websockets`, and terminal output is styled with `termcolor`, `colorama`, and `rich`.
    - Initializes `colorama` for colored terminal output and creates a `Console` instance from `rich`.

2. **Global Variables**:
    - `symbols`: List of cryptocurrency pairs from Binance to track.
    - `selected_symbols`: Empty list to hold user-selected symbols.
    - `websocket_url_base_*`: WebSocket URLs for Binance, Coinbase, Kraken, and Bitfinex.
    - `name_map`: Maps cryptocurrency names to their corresponding symbols and emojis.
    - `trades_data`, `liquidations_data`: Lists to store trade and liquidation data.
    - `trade_threshold`, `liquidation_threshold`: Variables for minimum trade/liquidation sizes.

3. **Utility Functions**:
    - `format_trade_time(trade_time)`: Converts timestamp into a human-readable time format using the Berlin timezone.
    - `calculate_time_difference(start_time, current_time)`: Calculates the time difference between two timestamps.
    - `collect_trade_data(symbol, used_trade_time, trade_type, usd_size, timestamp)`: Collects trade data and appends it to the `trades_data` list.
    - `collect_liquidation_data(symbol, used_trade_time, liquidation_type, usd_size, timestamp)`: Collects liquidation data and appends it to the `liquidations_data` list.
    - `get_stars(usd_size)`: Returns a visual representation (stars) for trades based on the USD size.
    - `get_liq_stars(usd_size)`: Similar to `get_stars`, but for liquidation sizes.

4. **`calculate_metrics` Function**:
    - Gathers and calculates statistical data from trades and liquidations over a specified time interval (including averages, counts, and USD sizes).
    - Categorizes trades and liquidations based on size, and stores results in dictionaries for further visualization.

5. **`create_output` Function**:
    - Uses the `rich` library to create a real-time dashboard layout displaying key metrics such as trades, liquidations, and average values.
    - The output is organized into panels for visual clarity and is updated dynamically.

6. **Trade and Liquidation Handlers**:
    - `process_trade(symbol, price, quantity, trade_time, is_buyer_maker)`: Processes each trade received, converts the trade time, and appends data if the size exceeds the threshold.
    - `process_liquidation(symbol, side, timestamp, usd_size)`: Similar to `process_trade`, but for liquidations.

7. **WebSocket Stream Functions**:
    - `binance_trade_stream`, `coinbase_trade_stream`, `kraken_trade_stream`, and `bitfinex_trade_stream`: These asynchronous functions establish WebSocket connections to the respective exchanges and handle trade data received in real-time.
    - `binance_liquidation`: This function listens for liquidation events on Binance.

8. **`select_symbols` Function**:
    - Allows the user to manually select symbols to track or select all available symbols.
    - Determines which symbols are available on Kraken and Bitfinex exchanges.

9. **Main Program Flow (`main` Function)**:
    - Initializes thresholds, selects symbols, and starts WebSocket streams to listen to trades and liquidations.
    - Uses `asyncio` to run the WebSocket streams concurrently.
    - Starts the real-time dashboard using the `Live` feature of `rich` to continuously display updated data.

### Function Descriptions:

1. **`format_trade_time(trade_time)`**:
   - Converts a given Unix timestamp to a human-readable time format using the Berlin timezone.

2. **`calculate_time_difference(start_time, current_time)`**:
   - Computes and returns the difference between two timestamps.

3. **`collect_trade_data(symbol, used_trade_time, trade_type, usd_size, timestamp)`**:
   - Stores trade information (symbol, trade time, type, size, and timestamp) in a global list.

4. **`collect_liquidation_data(symbol, used_trade_time, liquidation_type, usd_size, timestamp)`**:
   - Stores liquidation information (symbol, liquidation time, type, size, and timestamp) in a global list.

5. **`get_stars(usd_size)`**:
   - Returns a visual representation (using emojis) based on the USD size of a trade.

6. **`get_liq_stars(usd_size)`**:
   - Similar to `get_stars`, but for liquidation size, returning corresponding emojis.

7. **`calculate_metrics(trades_data, liquidations_data, trade_threshold, liquidation_threshold, average_interval, start_timestamp)`**:
   - Calculates statistical metrics for trades and liquidations, such as the number of trades, total USD size, and averages per minute within a given time interval.

8. **`create_output(layout, metrics, start_time, trade_threshold, liquidation_threshold)`**:
   - Generates and updates a visual dashboard to display trade and liquidation metrics using `rich` components.

9. **`process_trade(symbol, price, quantity, trade_time, is_buyer_maker)`**:
   - Processes trade data (price, quantity, and time), and appends it to the trade data list if the trade size exceeds the threshold.

10. **`process_liquidation(symbol, side, timestamp, usd_size)`**:
    - Processes liquidation data, storing it if the size exceeds the defined threshold.

11. **`binance_trade_stream(uri, symbol)`**:
    - Connects to Binance's WebSocket API to listen for trade data, processes it, and appends to the trade list.

12. **`coinbase_trade_stream(uri)`**:
    - Connects to Coinbase's WebSocket API to listen for trade data for selected symbols.

13. **`binance_liquidation(uri)`**:
    - Listens for liquidation events on Binance and processes them if they meet the threshold.

14. **`kraken_trade_stream(uri)`**:
    - Connects to Kraken's WebSocket API to listen for trade data for selected symbols.

15. **`bitfinex_trade_stream(uri)`**:
    - Connects to Bitfinex's WebSocket API to listen for trade data and process it.

16. **`select_symbols()`**:
    - Allows the user to select which cryptocurrency symbols to monitor.

17. **`main()`**:
    - The main function that coordinates symbol selection, threshold setting, and the initialization of WebSocket streams for data collection. It also manages the real-time display of trade and liquidation data using the `Live` component.


---------------------------------------------------------------------------------



# **Trade Trail🛤️    |⭐⭐⭐|** 


This Code provides a Stream for every specified symbol in which trades and liquidations are displayed if they reach the specified threshold. These trades and liquidations will be saved in an Excel file and calculated for more in-depth comparison and better market data interpretation

###  **Trade Magnitudes**                                         
      
'⁉️💰🃏💰⁉️'   >= 210,935,000 $
'  🐳🐳🐳  ' >= 130,365,000 $
'   🐳🐳   ' >= 80,570,000 $
'    🐳    ' >= 49,795,000 $
'  🦈🦈🦈  ' >= 30,775,000 $
'   🦈🦈   ' >= 19,020,000 $
'    🦈    ' >= 11,755,000 $
'  🦑🦑🦑  ' >= 7,265,000 $
'   🦑🦑   ' >= 4,490,000 $
'    🦑    ' >= 2,775,000 $
'  🐡🐡🐡  ' >= 1,715,000 $
'   🐡🐡   ' >= 1,060,000 $
'    🐡    ' >= 655,000 $
'🐠🐠🐠🐠🐠' >= 405,000 $
' 🐠🐠🐠🐠 ' >= 250,000 $
'  🐠🐠🐠  ' >= 155,000 $
'   🐠🐠   ' >= 95,000 $
'    🐠    ' >= 60,000 $
'🐟🐟🐟🐟🐟' >= 35,000 $
' 🐟🐟🐟🐟 ' >= 25,000 $
'  🐟🐟🐟  ' >= 15,000 $
'   🐟🐟   ' >= 10,000 $
'    🐟    ' >= 5,000 $


### **Liquidation Magnitudes**


'🌊💰♒💰🌊'  > 46,368,000 $
 '  ♒♒♒  '   > 28,657,000 $
'    ♒♒    ' > 17,711,000 $
'    ♒     ' > 10,946,000 $
'  🌊🌊🌊  ' > 6,765,000 $
'   🌊🌊   ' > 4,181,000 $
'    🌊    ' > 2,584,000 $
'  ⛲⛲⛲  ' > 1,597,000 $
'   ⛲⛲   ' > 987,000 $
'    ⛲    ' > 610,000 $
'  🪣🪣🪣  ' > 377,000 $
'   🪣🪣   ' > 233,000 $
'    🪣    ' > 144,000 $
'💦💦💦💦💦' > 89,000 $
' 💦💦💦💦 ' > 55,000 $
'  💦💦💦  ' > 34,000 $
'   💦💦   ' > 21,000 $
'    💦    ' > 13,000 $
'💧💧💧💧💧' > 8,000 $
' 💧💧💧💧 ' > 5,000 §
'  💧💧💧  ' > 3,000 $
'   💧💧   ' > 2,000 $
'    💧    ' > 1,000 $


### At the beginning of the Code you have to set 4 requirements:

❓"Choose Symbols: "❓                                                                                              
↪️ You can choose cryptocurrencies from a given list. if you chose every symbol you wanted you can write "done" to go to the next step. If you type "all" you choose all available symbols
                                                                   
❓"Please enter the threshold value for 'usd_size' on trades: "❓                                                                                              
↪️ You will only see trades that are bigger than the specified value
                                                                          
❓"Please enter the interval for exportation and calculation in seconds: "❓                                                                                                            
↪️ Here you can specify the Period in which the Code should export the data and calculate some Indicators (Total trades/liquidations, Differences, Avg. trades/liquidations, counts and sizes, time since starting the Program etc.). After the specified interval you will get an Overview of all trades and liquidation since starting the program
 

- A **green number** for transactions means a Long-Trade (or Buy) was made
- A **red number** for transactions means a Short-Trade (or Sell) was made
  
- On the right side of the liquidation and trade screener you can see the cumulative Sum since you started the program


## After a specified Interval you will get an Output like this:

📅 Start Time: 2024-09-17 12:09:49                                                                                                                  
🕰️ Current Time: 2024-09-17 12:10:19                                                                                            
⏳0:00:30 since start⏳                                                                                                                                      

🎣 A total of 203 Trades above 10000.0$                                                                                                                          
📈Total Count: 102  | 📈Total Size: 5,104,487.80$                                                                                                                        
📉Total Count: 101 | 📉Total Size: 3,303,344.57$                                                                                                                      
🔍 Trade Sizes:                                                                                                                                                      
      🐠    : 📈 3 Trades | Total USD Size: 669,459.49$                                                                                                                    
     🐟🐟   : 📈 35 Trades | Total USD Size: 488,669.52$                                                                                                                    
    🐟🐟🐟  : 📈 32 Trades | Total USD Size: 877,985.05$                                                                                                                                  
   🐟🐟🐟🐟 : 📈 19 Trades | Total USD Size: 1,005,109.28$                                                                                                                        
  🐟🐟🐟🐟🐟: 📈 11 Trades | Total USD Size: 1,198,481.59$                                                                                                                                  
     🐠🐠   : 📈 2 Trades | Total USD Size: 864,782.87$                                                                                                                                                                                       
      🐠    : 📉 3 Trades | Total USD Size: 764,492.32$                                                                                                                                        
     🐟🐟   : 📉 47 Trades | Total USD Size: 627,271.66$                                                                                                                                                                  
    🐟🐟🐟  : 📉 40 Trades | Total USD Size: 1,160,777.67$                                                                                                                                                                
   🐟🐟🐟🐟 : 📉 9 Trades | Total USD Size: 521,872.89$                                                                                                                                                                      
  🐟🐟🐟🐟🐟: 📉 2 Trades | Total USD Size: 228,930.03$                                                                                                                                                                            
Difference: 1,801,143.23$                                                                                                                                                                              
📊 Avg. Trades per minute: 203.00                                                                                                                                                                      
📊 Avg. USD Size per minute: 1801143.23$                                                                                                                                                                                          

### In this Overview you can see different Information:

**🕰️Time Parameters🕰️**
- At which point in time you started the program
- At which point in time the last Trade or Liquidation was recognized
- how long the program is running

**🎣Trade Parameters🎣**
- Total Trades
- Total amount of Long-Trades and the total USD size of them
- Total amount of Short-Trades and the total USD size of them
- In which magnitude were the Trades where made
- difference between Long-Trades and Short-Trades
- the average amount of Trades in a specified interval
- average USD size of Trades in a specified interval

## Code Breakdown (Step by Step):

1. **Library Imports**:
   - Imports necessary libraries such as `asyncio` for asynchronous tasks, `json` for handling JSON data, and `pytz` for time zone handling, among others.

2. **Initialize Colorama**:
   ```python
   init()
   print("🗄️ Libraries successfully loaded")
   ```
   This initializes the `colorama` module to handle colored terminal outputs and confirms that libraries are loaded.

3. **Configuration**:
   ```python
   symbols = [ ... ]  # List of symbols for various cryptocurrency pairs.
   selected_symbols = []  # Placeholder for symbols that will be chosen by the user.
   ```
   This defines default cryptocurrency symbols, which are later selected by the user for tracking.

4. **Ensure Output Directory**:
   ```python
   os.makedirs(output_directory, exist_ok=True)
   ```
   This creates a directory for storing data, ensuring it exists.

5. **Initialize Symbol Maps**:
   ```python
   name_map = { ... }  # Maps currency symbols to their respective icons.
   ```
   This provides a dictionary mapping for symbols to emojis, making it easier to display symbol names in a more intuitive way.

6. **Exchange-Specific Mappings**:
   ```python
   kraken_symbol_map = { ... }  # Kraken exchange-specific symbol mapping.
   bitfinex_symbol_map = { ... }  # Bitfinex exchange-specific symbol mapping.
   ```
   This sets up symbol mappings for specific exchanges like Kraken and Bitfinex.

7. **Initialize Variables**:
   ```python
   cumulative_sum_map = {}
   trades_data = []  # List to hold trade data.
   liquidations_data = []  # List to hold liquidation data.
   ```
   This initializes dictionaries and lists to track cumulative sums and store trade or liquidation data.

8. **Main Function Definitions**:
   
   - **initialize_maps**: Initializes the cumulative sum maps for the selected symbols.
   - **format_trade_time**: Formats the trade time to the `Europe/Berlin` time zone.
   - **add_cumulative_sum_column**: Adds a cumulative sum column to a DataFrame based on the trade or liquidation type.
   - **export_to_excel**: Exports data to an Excel file and applies formatting such as colored cells based on conditions.
   - **calculate_time_difference**: Calculates the time difference between the start time and the trade or liquidation time.
   - **periodic_export**: Periodically exports trade and liquidation data to Excel at a given interval.
   - **collect_trade_data**: Collects trade data and appends it to the `trades_data` list.
   - **collect_liquidation_data**: Collects liquidation data and appends it to the `liquidations_data` list.
   - **process_trade**: Processes incoming trade data by calculating `usd_size`, updating cumulative sums, and printing the formatted output.
   - **process_liquidation**: Processes liquidation data similarly to `process_trade`.
   
9. **WebSocket Streams**:
   - Functions like `binance_trade_stream`, `coinbase_trade_stream`, and `kraken_trade_stream` handle live data streams from different exchanges.
   
10. **Main Function**:
   ```python
   async def main(): 
       select_symbols()  # User selects the cryptocurrency symbols to track.
       asyncio.run(main())
   ```
   This function initiates the process, allowing users to select symbols, set thresholds, and start multiple WebSocket connections for real-time data collection and processing.

### Function Descriptioin

1. **initialize_maps**:
   Initializes the cumulative sum maps for tracking the cumulative trade or liquidation size for each selected symbol.

2. **format_trade_time**:
   Converts a timestamp to a formatted string in the `Europe/Berlin` time zone, used for displaying trade times.

3. **add_cumulative_sum_column**:
   Adds a column to a DataFrame that shows the running total (cumulative sum) based on trade or liquidation types.

4. **export_to_excel**:
   Exports collected trade or liquidation data into an Excel file, creating a new file if it doesn't exist and adding color formatting based on conditions.

5. **calculate_time_difference**:
   Calculates the time difference between the program start time and a given trade or liquidation time.

6. **periodic_export**:
   Periodically exports collected data to Excel files at specified intervals and prints a summary of the data collected so far.

7. **collect_trade_data**:
   Appends trade data to the global list `trades_data`, storing details about each trade.

8. **collect_liquidation_data**:
   Appends liquidation data to the global list `liquidations_data`, storing details about each liquidation event.

9. **process_trade**:
   Processes a trade event, updates cumulative sums, formats and displays the trade information with colored output.

10. **process_liquidation**:
   Processes a liquidation event, updates cumulative sums, formats and displays the liquidation information with colored output.

11. **binance_trade_stream**:
   Connects to Binance's WebSocket API to receive real-time trade data for the selected symbols and process each trade.

12. **coinbase_trade_stream**:
   Connects to Coinbase's WebSocket API to receive real-time trade data and processes each trade for selected symbols.

13. **kraken_trade_stream**:
   Connects to Kraken's WebSocket API to receive and process real-time trade data for the selected symbols. 

14. **main**:
   The main function that initializes the WebSocket streams and periodically exports collected data to Excel files while printing summaries to the terminal.


------------------------------------------------------------------------------------------------------------------------------------------

 # **Funding Rates📊      |⭐⭐⭐|**


This Code provides the Funding Rates for contracts. 
- If the Funding Rate is **low or 0** you will get a relatively smaller fee.
- If the Funding Rate is **positive** you have to pay a relatively higher fee.
- If the Funding Rate is **negative** you will get a a negative fee (they will fund you a bit instead of demanding fees such that the amount will come to an equilibrium)
 
🟨| Funding Rate is between -5% to 5%                                                            
🟩| Funding Rate is between 5% to 10%                                                                
🟩🟩| Funding Rate is between 10% to 20%                                                                                    
🟩🟩🟩| Funding Rate is more than 20%                                                    
🟥|  Funding Rate is between -10% to -5%                                                  
🟥🟥| Funding Rate is between -10% to -20%                                                  
🟥🟥🟥| Funding Rate is less than -20%                                                   



## Step-by-Step Explanation of the Code

This Python script connects to a WebSocket on Binance and continuously fetches market data (funding rates) for various cryptocurrency pairs. It uses `asyncio` to handle asynchronous operations and libraries like `rich` for rendering output in a table format. Let's break down the code:

---

### 1. **Import Statements**
```python
import asyncio
import json
from datetime import datetime
from websockets import connect, ConnectionClosed
from rich.console import Console
from rich.table import Table
from rich.live import Live
from termcolor import colored
```
- **`asyncio`**: Enables asynchronous programming, allowing multiple tasks (such as WebSocket connections) to run concurrently.
- **`json`**: Used for parsing JSON data received from the WebSocket.
- **`datetime`**: Handles date and time manipulation.
- **`websockets`**: Manages WebSocket connections to fetch real-time data from Binance.
- **`rich`**: Provides functionalities for creating tables (`Table`) and live console updates (`Live`).
- **`termcolor`**: Adds colored output to terminal messages.

---

### 2. **Symbols and Initial Configuration**
```python
symbols = ['btcusdt', 'ethusdt', 'solusdt', ...]
websocket_url_base_binance = 'wss://fstream.binance.com/ws/'
shared_symbol_data = {symbol: {} for symbol in symbols}
print_lock = asyncio.Lock()
console = Console()
```
- **`symbols`**: A list of trading pairs (cryptocurrencies paired with USDT) from Binance, like `btcusdt`, `ethusdt`.
- **`websocket_url_base_binance`**: The base WebSocket URL for connecting to Binance.
- **`shared_symbol_data`**: A dictionary where each key is a symbol, and its value will store the latest market data.
- **`print_lock`**: An asyncio lock to ensure safe concurrent access to the console.
- **`console`**: A `rich` object to handle the rendering of tables and other text to the terminal.

---

### 3. **Symbol Mapping for Display**
```python
name_map = {
    'BTC': '🟡BTC     ', 'ETH': '💠ETH     ', ...
}
```
- **`name_map`**: A dictionary mapping cryptocurrency tickers (like `BTC`, `ETH`) to a visually enriched display name (including emojis for styling).

---

### 4. **User-Selected Symbols Placeholder**
```python
selected_symbols = []
selected_symbols_formatted = []
All_symbols = False
```
- **`selected_symbols`**: A list that will store the symbols selected by the user.
- **`selected_symbols_formatted`**: The formatted version of the selected symbols for display.
- **`All_symbols`**: A flag indicating if the user selects all available symbols.

---

### 5. **WebSocket Data Stream (binance_funding_stream)**
```python
async def binance_funding_stream(symbol):
    websocket_url = f'{websocket_url_base_binance}{symbol}@markPrice'
    ...
```
This function continuously connects to the WebSocket for a specific symbol, fetches the data, and processes it:
- **`connect(websocket_url)`**: Establishes the WebSocket connection for the symbol's funding rate.
- **`message = await websocket.recv()`**: Asynchronously waits to receive a new message.
- **`data = json.loads(message)`**: Parses the JSON data received.
- **`funding_rate`**: Extracts the funding rate and calculates related rates for different time periods (8-hour, daily, weekly, monthly, yearly).
- **`shared_symbol_data[symbol]`**: Updates the `shared_symbol_data` dictionary with the latest data for this symbol.

If the WebSocket connection is closed, the script will try to reconnect after a delay.

---

### 6. **Sorting Symbols by Funding Rate (get_sorted_symbols)**
```python
def get_sorted_symbols():
    return sorted(shared_symbol_data.items(), key=lambda x: x[1].get('yearly_funding_rate', float('-inf')), reverse=True)
```
This function sorts all symbols based on their yearly funding rate (from highest to lowest).

---

### 7. **Creating the Table (create_table)**
```python
def create_table():
    table = Table(show_header=True, header_style="bold white", title=f"🚀 Funding Rates {current_time} ️🚀", show_lines=True)
    ...
```
This function creates a table using the `rich` library:
- **`Table()`**: Defines a new table with a header.
- **`add_column`**: Adds columns for symbol name, funding rates over different periods (8-hour, daily, weekly, etc.).
- **`add_row`**: Adds rows of data, populated with the latest market data from `shared_symbol_data`.

---

### 8. **Live Table Update (update_display)**
```python
async def update_display():
    with Live(create_table(), refresh_per_second=1, console=console) as live:
        while True:
            await asyncio.sleep(1)
            live.update(create_table())
```
This function continuously updates the table on the console:
- **`Live()`**: Manages the live update of the table on the terminal.
- **`live.update()`**: Refreshes the table display with the latest data.

---

### 9. **User Symbol Selection (select_symbols)**
```python
def select_symbols():
    print(colored("\n♠️♦️Choose your symbols♣️♥️", 'black', 'on_white'))
    ...
```
This function allows the user to choose which symbols they want to query:
- **`input()`**: The user can type a symbol or choose 'ALL' to select all symbols.
- **`selected_symbols`**: Stores the symbols the user selects.

---

### 10. **Main Function (main)**
```python
async def main():
    select_symbols()
    tasks = [binance_funding_stream(symbol) for symbol in selected_symbols]
    tasks.append(update_display())
    await asyncio.gather(*tasks)
```
This is the entry point of the program:
- **`select_symbols()`**: Calls the function to let the user select which symbols to track.
- **`tasks`**: Creates a list of asyncio tasks—one task for each selected symbol to fetch data, plus one task to update the display.
- **`asyncio.gather(*tasks)`**: Runs all tasks concurrently.

---

### 11. **Program Execution**
```python
asyncio.run(main())
```
This runs the `main()` function, starting the entire process asynchronously.

---

### Summary:
- This code connects to Binance's WebSocket API and fetches real-time funding rates for selected cryptocurrency pairs.
- The data is displayed in a dynamic, continuously updated table.
- The user can choose which symbols they want to track.


 ---------------------------------------------------------------------------------------------------------------------------------------


# Definitions and Education🃏📖

**Liquidation:** In the world of cryptocurrencies, liquidation refers to the process where a position is automatically closed to limit losses to the trader's capital. This occurs when the market price of an asset moves so strongly against the trader's position that the available margin (the collateral the trader has posted) is no longer sufficient to cover the losses. Liquidations are particularly common in leveraged positions, where borrowed funds are used to increase the size of the trade.

**Transaction:** A transaction in the cryptocurrency space is the transfer of crypto assets from one address to another. Each transaction is recorded on the blockchain, making it immutable and traceable. Transactions can involve buying or selling cryptocurrencies, transferring between wallets, or using cryptocurrencies in decentralized finance applications (DeFi).

### The Principle Behind Liquidations and Transactions

1. **Liquidation:**
   - A liquidation occurs when a trader opens a position based on borrowed money (leverage), and the market price moves so strongly against the position that the losses exceed or endanger the margin capital.
   - Exchanges or brokers have mechanisms in place that automatically close positions before all the capital is lost. This protects both the trader and the exchange.
   - Liquidations typically happen on platforms offering margin trading, futures, or other derivative products where traders can take on highly leveraged positions.
   - Liquidations can be partial or complete, depending on how far the price moves against the position and what safety mechanisms the exchange has implemented.

2. **Transaction:**
   - A transaction occurs when cryptocurrencies are transferred between two parties. These transactions are stored on the blockchain and secured by cryptographic methods.
   - Each transaction requires a sender, a receiver, and a signature that ensures the authenticity and authorization of the transaction.
   - Transactions can take various forms: simple transfers between wallets, buying and selling on exchanges, or more complex operations such as smart contract interactions in DeFi protocols.
   - Unlike liquidations, which are typically involuntary and automatic, transactions are deliberate actions taken by the participants.

### Differences and Similarities

**Differences:**
- **Purpose:** Liquidations are for risk mitigation and capital protection, while transactions are for exchanging or moving assets.
- **Voluntariness:** Transactions are voluntary actions, while liquidations happen automatically and often involuntarily.
- **Triggers:** Liquidations are triggered by market movements and leverage, while transactions are triggered by user decisions.
- **Risk Involvement:** Liquidations often involve only the trader and the trading platform, while transactions directly involve two or more parties.

**Similarities:**
- Both processes are integral to the crypto ecosystem and rely on blockchain technology.
- Liquidations and transactions are regulated by smart contracts and protocols that ensure these operations are executed correctly.
- Both are unavoidable in their respective contexts: liquidations in high-risk trading scenarios and transactions in everyday cryptocurrency use.

### When Does Each Phenomenon Occur?

- **Liquidations:** Liquidations mainly occur in highly volatile markets and when using margin trading and leverage products. They are particularly common during rapid, unpredictable price movements where the market moves against the open position of the trader.
  
- **Transactions:** Transactions occur whenever cryptocurrencies are moved—whether buying goods and services, trading on exchanges, sending coins to friends, or interacting with DeFi protocols.

### Examples

1. **Liquidation:** A trader has opened a long position in Bitcoin with 10x leverage. If the price of Bitcoin falls by 10%, the position is automatically liquidated because the loss exceeds the margin amount.
   
2. **Transaction:** A person buys Ethereum on an exchange and sends it to their own wallet. This action is a transaction and is recorded on the blockchain as a transfer.

### What Does It Mean if My Portfolio Was Liquidated?

If your portfolio was liquidated, it means that one or more of your positions were forcibly closed due to unfavorable market movements and the use of leverage. The liquidation occurs because the margin amount you posted was no longer sufficient to cover the losses. As a result, you lose the entire margin amount you posted for the leveraged position, and the position was closed to prevent further debt.





**Funding Rates** are a mechanism primarily used in crypto derivatives markets, especially in perpetual futures contracts. They play a crucial role in maintaining the price alignment between the perpetual futures market and the underlying spot market.

### **How Funding Rates Work**

1. **Definition**: Funding rates are periodic payments between long (buyers) and short (sellers) positions in perpetual futures markets. These payments typically occur every 8 hours, but the frequency can vary depending on the exchange.

2. **Mechanism**:
   - When the funding rate is positive, long positions (buyers) pay short positions (sellers).
   - When the funding rate is negative, short positions (sellers) pay long positions (buyers).

3. **Purpose**: The primary purpose of funding rates is to keep the price of perpetual futures closely aligned with the price of the underlying asset. This is achieved by adjusting the demand for long or short positions:
   - If the perpetual price is higher than the spot price, positive funding rates discourage long positions because they incur additional costs.
   - If the perpetual price is lower than the spot price, negative funding rates discourage short positions because they incur additional costs.

### **Interpretation of Funding Rates**

1. **Positive Funding Rates**:
   - Indicates that most traders hold long positions and the market is generally bullish.
   - A high positive funding rate may suggest that the market is overheated and a correction could be imminent.

2. **Negative Funding Rates**:
   - Indicates that most traders hold short positions and the market is generally bearish.
   - A high negative funding rate may suggest that the market is oversold and a rally could be forthcoming.

3. **Extreme Values**:
   - Extremely high or low funding rates can signal an impending trend reversal, as such extremes often indicate excessive market positioning.

4. **Strategic Use**:
   - Traders can use funding rates as an indicator to assess market sentiment and identify potential trend reversal points.
   - In cases of extremely positive or negative funding rates, a strategy might be to trade in the opposite direction, as the market may be preparing for a correction.

In summary, funding rates are an important tool for maintaining the balance between futures and spot markets and can be used as an indicator of market sentiment and potential future price movements.



-----------------------------------------------------------------
## **🃏Own Opinion🃏**


These data streams will give you detailed information about the stream of transactions, which can affect your trading decisions a lot. Trading with the smart money gets a lot easier. You will gain a bird's view over the ocean of cryptocurrencies. Swim with the Stream of the big fishes and not based on chart formations. The funding rates are significant if you trade with contracts, but they also give you information about the behavior of the overall market. This information can also be used to build algorithmic trading bots around it (buy if some 40,000,000$ Whale bought or something like that). Use several different intervals with a different amount of symbols for a perfect Overview of the deep Crypto-Market Sea. If you like what I am doing you can support me by liking my content, sharing my account and my projects with your friends, or you can pay me a coffee if you like. Happy trading👍
