import asyncio
import json
from datetime import datetime
from websockets import connect, ConnectionClosed
from termcolor import colored, cprint

symbols = [
    'btcusdt', 'ethusdt', 'solusdt', 'bnbusdt', 'dogeusdt', 'usdcusdt', 
    'xrpusdt', 'adausdt', 'maticusdt', 'tonusdt', 'linkusdt', 'trxusdt', 
    'nearusdt', 'xlmusdt', 'rndrusdt', 'dotusdt', 'uniusdt', 'atomusdt', 
    'xmrusdt', 'ldousdt', 'gmxusdt'
]
websocket_url_base_binance = 'wss://fstream.binance.com/ws/'

shared_symbol_data = {symbol: {} for symbol in symbols}
print_lock = asyncio.Lock()

name_map = {
    'BTC':  '🟡BTC     ',
    'ETH':  '💠ETH     ', 
    'SOL':  '👾SOL     ', 
    'BNB':  '🔶BNB     ', 
    'DOGE': '🐶DOGE    ',
    'USDC': '💵USDC    ', 
    'XRP':  '⚫XRP     ', 
    'ADA':  '🔵ADA     ', 
    'MATIC':'🟣MATIC   ',
    'TON':  '🎮TON     ', 
    'LINK': '🔗LINK    ', 
    'TRX':  '⚙️ TRX     ', 
    'NEAR': '🔍NEAR    ', 
    'XLM':  '🌟XLM     ',
    'RNDR': '🎨RNDR    ', 
    'DOT':  '⚪DOT     ', 
    'UNI':  '🦄UNI     ', 
    'ATOM': '⚛️ ATOM    ', 
    'XMR':  '👽XMR     ',
    'LDO':  '🧪LDO     ', 
    'GMX':  '🌀GMX     '
}

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
                    yearly_funding_rate = (funding_rate * 3 * 365) * 100
                    stars = '🟨    ' if -5 < yearly_funding_rate < 5 else (
                            '🟩    ' if -10 < yearly_funding_rate < -5 else (
                            '🟩🟩  ' if -20 < yearly_funding_rate < -10 else (
                            '🟩🟩🟩' if yearly_funding_rate < -20 else (
                            '🟥    ' if 10 > yearly_funding_rate > 5 else (
                            '🟥🟥  ' if 20 > yearly_funding_rate > 10 else 
                            '🟥🟥🟥')))))

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
                            'event_time': event_time,
                            'color': color
                        }
        except ConnectionClosed:
            print(f"WebSocket connection closed for {symbol}. Reconnecting...")
            await asyncio.sleep(5)  # wait before reconnecting
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(1)

def get_sorted_symbols():
    # Sort the symbols based on their yearly funding rate
    return sorted(shared_symbol_data.items(), key=lambda x: x[1].get('yearly_funding_rate', float('-inf')), reverse=True)

async def update_display(start_time):
    while True:
        await asyncio.sleep(60)
        #print("\033c", end="")  # Clear the terminal
        title = "Fund Rates"
        current_time = datetime.now().strftime("%H:%M:%S")
        cprint(f"{title} |🕰️|{current_time}|🕰️", 'white', attrs=['bold', 'underline'])
        
        sorted_symbols = get_sorted_symbols()

        for sym, data in sorted_symbols:
            if data:
                color = data.get('color', 'on_white')
                line = f"{data['symbol_display']} {data['stars']} {data['yearly_funding_rate']:.2f}%"
                cprint(line, 'white', color)

async def main():
    start_time = datetime.now().strftime("%H:%M:%S")
    tasks = [binance_funding_stream(symbol) for symbol in symbols]
    tasks.append(update_display(start_time))
    await asyncio.gather(*tasks)

asyncio.run(main())

