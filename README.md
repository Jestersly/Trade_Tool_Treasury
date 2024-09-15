# Binance-Coinbase-Trade-and-Liquidation-Streams
This Code visualizes every Trade and Liquidation that was made or triggered through Binance and Coinbase, over a   given Treshhold. There are 3 different codes for 3 different scales of trades and Liquidations. 
 
  **Trade Magnitudes**                                         
       
  :         >  25,000$                                                
🐟:         <= 25,000$                                           
🐟🐟:       <= 50,000$                                           
🐟🐟🐟:     <= 100,000$                                          
🐟🐟🐟🐟:   <= 200,000$                                          
🐟🐟🐟🐟🐟: <= 400,000$                                          
🐠:         <= 500,000$                                          
🐠🐠:       <= 1,000,000$                                        
🐠🐠🐠:     <= 1,500,000$                                        
🐠🐠🐠🐠:   <= 2,500,000$                                        
🐠🐠🐠🐠🐠: <= 5,000,000$                                        
🦈:         <= 10,000,000$                                       
🦈🦈:       <= 20,000,000$                                        
🦈🦈🦈:     <= 30,000,000$                                       
🐳:         <= 50,000,000$                                                                                    
🐳🐳:       <= 80,000,000$                                                                 
🐳🐳🐳:     <= 120,000,000$                                                       
💸🌈🦄🌈💸: <= 250,000,000$                                                      
❓💰🃏💰❓: <= 500,000,000$                                                     


**Liquidation Magnitudes**

💧:          >  5,000$                                                      
💧💧:        <= 5,000$                                                         
💧💧💧:      <= 10,000$                                                         
💦:          <= 15,000$                                                        
💦💦:        <= 25,000$                                                           
💦💦💦:      <= 50,000$                                                             
💦💦💦💦:    <= 100,000$                                                                
💦💦💦💦💦:  <= 250,000$                                                            
🌊:          <= 500,000$                                                        
🌊🌊:        <= 1,000,000$                                                          
🌊🌊🌊:      <= 2,500,000$                                                       
🤿:          <= 5,000,000$                                                        
🌊🤿🌊:      <= 10,000,000$                                                        
💸🌊🤿🌊💸:  <= 25,000,000$                                                        
🌊💰🤿💰🌊:  <= 50,000,000$                                                          


- A green number for transactions means a Long-Trade (or Buy) was made
- A green number for liquidations means somebody got liquidated (Portfolio Stop-Loss got triggered)
- A red number for transactions means a Short-Trade (or Sell) was made
- A red number for liquidations means somebody has closed his/her portfolio with profits (Portfolio Take-Profit got triggered or manual close with profits)

- On the right side of the liquidation and trade screener you can see the cumulative Sum since you started the program
- Thi Code only provides the following symbols:
  'BTC': '🟡BTC     ', 'ETH': '💠ETH     ', 'SOL': '👾SOL     ', 'BNB': '🔶BNB     ', 'DOGE': '🐶DOGE    ',
  'USDC': '💵USDC    ', 'XRP': '⚫XRP     ', 'ADA': '🔵ADA     ', 'MATIC': '🟣MATIC   ',
  'TON': '🎮TON     ', 'LINK': '🔗LINK    ', 'TRX': '⚙️ TRX     ', 'NEAR': '🔍NEAR    ', 'XLM': '🌟XLM     ',
  'RNDR': '🎨RNDR    ', 'DOT': '⚪DOT     ', 'UNI': '🦄UNI     ', 'ATOM': '⚛️ ATOM    ', 'XMR': '👽XMR     ',
  'LDO': '🧪LDO     ', 'GMX': '🌀GMX     


**❓But what are Liquidations and Transactions❓**


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
