# Binance-Coinbase-Trade-and-Liquidation-Streams

## Important❗

### These Codes only provide the following symbols:                                      
- 🟡BTC, 💠ETH, 👾SOL, 🔶BNB, 🐶DOGE, 💵USDC, ⚫XRP, 🔵ADA 🟣MATIC, 🎮TON, 🔗LINK, ⚙️ TRX, 🔍NEAR, 🌟XLM, 🎨RNDR, ⚪DOT, 🦄UNI, ⚛️ ATOM, 👽XMR, 🧪LDO, 🌀GMX
- Some terminals represent the symbols "⚛️ ATOM, ⚙️ TRX, and 🎨RNDR" a bit differently such that you may have to indent them correctly (add or delete space between the emoji and the name in "name_map")
- I personally use the timestamp "Europe/Berlin". I don't think that this is the case for everybody. 
-----------------------------------------------------------------------

# **⭐🃏Liq's & Trades🃏⭐** 


This Code provides an Overview for every trade and liquidation that was made with Binance or Coinbase over a given threshold. These trades and liquidations will be saved in an excel file and calculated for more in depth comparison and a better market data interpretation

- At the beginning of the Code you have to set 3 requirements 

                                                                   
❓"Please enter the threshold value for 'usd_size' on trades: "❓                                                                                                 
❗ You will only see trades that are bigger than the specified value❗
                                                                          
❓"Please enter the threshold value for 'usd_size' on liquidations: "❓                                                                                                                        
❗ You will only see liquidations that are bigger than the specified value❗
                                                                          
❓"Please enter the interval for exportation and calculation: "❓                                                                                                            
❗ Here you can specify the Period in which the Code should export the data and calculate some Indicators (Total trades/liquidations, Differences, Avg. trades/liquidations, counts and sizes, time since starting the Program etc.)❗


 
  **Trade Magnitudes**                                         
       
  :         <  5,000$                                                
🐟:         >= 5,000$                                           
🐟🐟:       >= 10,000$                                           
🐟🐟🐟:     >= 20,000$                                          
🐟🐟🐟🐟:   >= 40,000$                                          
🐟🐟🐟🐟🐟: >= 80,000$                                          
🐠:         >= 160,000$                                          
🐠🐠:       >= 320,000$                                        
🐠🐠🐠:     >= 640,000$                                        
🐠🐠🐠🐠:   >= 1,280,000$                                        
🐠🐠🐠🐠🐠: >= 2,560,000$                                        
🦈:         >= 5,120,000$                                       
🦈🦈:       >= 12,400,000$                                        
🦈🦈🦈:     >= 25,000,000$                                       
🐳:         >= 50,000,000$                                                                                    
🐳🐳:       >= 80,000,000$                                                                 
🐳🐳🐳:     >= 120,000,000$                                                       
💸🌈🦄🌈💸: >= 250,000,000$                                                      
❓💰🃏💰❓: >= 500,000,000$                                                     


**Liquidation Magnitudes**

💧:          <  2,000$                                                      
💧💧:        >= 4,000$                                                         
💧💧💧:      >= 8,000$                                                         
💦:          >= 16,000$                                                        
💦💦:        >= 32,000$                                                           
💦💦💦:      >= 64,000$                                                             
💦💦💦💦:    >= 128,000$                                                                
💦💦💦💦💦:  >= 256,000$                                                            
🌊:          >= 512,000$                                                        
🌊🌊:        >= 1,240,000$                                                          
🌊🌊🌊:      >= 2,500,000$                                                       
🤿:          >= 5,000,000$                                                        
🌊🤿🌊:      >= 10,000,000$                                                        
💸🌊🤿🌊💸:  >= 25,000,000$                                                        
🌊💰🤿💰🌊:  >= 50,000,000$                                                          


- A green number for transactions means a Long-Trade (or Buy) was made
- A red number for transactions means a Short-Trade (or Sell) was made

- A green number for liquidations means somebodies Take-Profit got triggered
- A red number for liquidations means somebody got liquidated (Stop-Loss or max. Margin got triggered)
  
- On the right side of the liquidation and trade screener you can see the cumulative Sum since you started the program



### After a specified Interval you will get an Output like this:

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

🌊 A total of 0 Liquidations above 10000.0$                                                                                                                                                                                  
📈Total Count: 0  | 📈Total Size: 0.00$                                                                                                                                                                                    
📉Total Count: 0 | 📉Total Size: 0.00$                                                                                                                                                              
🔍 Liquidation Sizes:                                                                                                                                                      
Difference: 0.00$                                                                                                                                                                  
📊 Avg. Liquidations per interval: 0.00                                                                                                                                                                                
📊Avg. USD Size per interval: 0.00$ per minute                                                                                                                                  


### In this Overview you can see different Informations:

**🕰️Time Parameters🕰️**
- At wich point in time you started the program
- At which point in time the last Trade or Liquidation was recognized
- how long the program is running

**🎣Trade Parameters🎣**
- Total Trades
- Total amount of Long-Trades and the total USD size of them
- Total amount of Short-Trades and the total USd size of them
- In which magnitude the Trades where made
- difference between Long-Trades and Short-Trades
- average amount of Trades in a specified interval
- average USD size of Trades in a specified interval

**🌊Liquidation Parameters🌊**
- Total Liquidations
- Total amount of Take-Profit-Liquidations and the total USD size of them
- Total amount of Stop-Loss-Liquidations and the total USd size of them
- In which magnitude the Liquidations where made
- difference between Take-Profit-Liquidations and Stop-Loss-Liquidations
- average amount of Liquidations in a specified interval
- average USD size of Liquidations in a specified interval


### Definitions

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


-----------------------------------------------------------------------------------------------------------------------------------

# **🃏The Daily Trade Summary🃏**

This Code creates a cumulative sum over all trades that are made with the given symbol since starting the program and visualizes their time-dependent behavior. The longer the code is running the bigger the impact from the current trades must be to make significant changes on the indicators. You create a broader overview if you start this code every couple of hours. 

9️⃣ 📈📈📈📈📈📈📈📈📈   |The Cumulative Sum is >= to 1/10 of the market cap                                                                    
8️⃣ 📈📈📈📈📈📈📈📈     |The Cumulative Sum is >= to 1/100 of the market cap                                                                      
7️⃣ 📈📈📈📈📈📈📈       |The Cumulative Sum is >= to 1/1,000 of the market cap                                                                      
6️⃣ 📈📈📈📈📈📈         |The Cumulative Sum is >= to 1/10,000 of the market cap                                                                       
5️⃣ 📈📈📈📈📈           |The Cumulative Sum is >= to 1/100,000 of the market cap                                                                      
4️⃣ 📈📈📈📈             |The Cumulative Sum is >= to 1/1,000,000 of the market cap                                                                
3️⃣ 📈📈📈               |The Cumulative Sum is >= to 1/10,000,000 of the market cap                                                                  
2️⃣ 📈📈                 |The Cumulative Sum is >= to 1/100,000,000 of the market cap                                                                             
1️⃣ 📈                   |The Cumulative Sum is >= to 1/1,000,000,000 of the market cap                                                                  

9️⃣ 📉📉📉📉📉📉📉📉📉  |The Cumulative Sum is <= to -1/10 of the market cap                                                                
8️⃣ 📉📉📉📉📉📉📉📉    |The Cumulative Sum is <= to -1/100 of the market cap                                                                   
7️⃣ 📉📉📉📉📉📉📉      |The Cumulative Sum is <= to -1/1,000 of the market cap                                                                  
6️⃣ 📉📉📉📉📉📉        |The Cumulative Sum is <= to -1/10,000 of the market cap                                                                         
5️⃣ 📉📉📉📉📉          |The Cumulative Sum is <= to -1/100,000 of the market cap                                                                               
4️⃣ 📉📉📉📉            |The Cumulative Sum is <= to -1/1,000,000 of the market cap                                                                     
3️⃣ 📉📉📉              |The Cumulative Sum is <= to -1/10,000,000 of the market cap                                                                        
2️⃣ 📉📉                |The Cumulative Sum is <= to -1/100,000,000 of the market cap                                                                              
1️⃣ 📉                  |The Cumulative Sum is <= to -1/1,000,000,000 of the market cap    

🟨                     |The Cumulative Sum changed between -5% and 5%                                                                
🟩                     |The Cumulative Sum changed between 5% and 10%                                                                         
🟩🟩                   |The Cumulative Sum changed between 10% and 20%                                                                                 
🟩🟩🟩                 |The Cumulative Sum changed between 20% and 40%                                                                                    
🟩🟩🟩🟩               |The Cumulative Sum changed between 40% and 80%                                                                                 
🟩🟩🟩🟩🟩             |The Cumulative Sum changed more than 80%                                                                               
🟥                     |The Cumulative Sum changed between -5% and -10%                                                                                
🟥🟥                   |The Cumulative Sum changed between -10% and -20%                                                                                      
🟥🟥🟥                 |The Cumulative Sum changed between -20% and -40%                                                                                                                                                       
🟥🟥🟥🟥               |The Cumulative Sum changed between -40% and -80%                                                                                 
🟥🟥🟥🟥🟥             |The Cumulative Sum changed more than -80%                                                                        

------------------------------------------------------------------------------------------------------------------------------------------

 # **🃏Funding Rates🃏**
 
🟨| Funding Rate is between -5% to 5%                                                            
🟩| Funding Rate is between 5% to 10%                                                                
🟩🟩| Funding Rate is between 10% to 20%                                                                                    
🟩🟩🟩| Funding Rate is more than 20%                                                    
🟥|  Funding Rate is between -10% to -5%                                                  
🟥🟥| Funding Rate is between -10% to -20%                                                  
🟥🟥🟥| Funding Rate is less than -20%                                                   


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


I think these data streams will give you alternative informations, which can affect your trading decisions a lot. Trading with the smart money gets a lot easier and the cumulative trade summary gives you a good alternative way to interpret the changes that happen over time. The funding rates are especially important if you trade with contracts but give you also information about the behaviour in the spot market
