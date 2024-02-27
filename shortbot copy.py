
import ccxt
import pandas as pd
import pandas_ta as ta
import numpy
import time 
import schedule
from pybit.unified_trading import HTTP


bybit = ccxt.bybit()

api_key = "LQLW7aAhcalaYMAiUe"
api_secret = "X02KF8x2VVXuXDQmoWAd8TCXx3dS7M7fAaKD"

session = HTTP(
    api_key=api_key,
    api_secret=api_secret,
    testnet= False,
)

# Step 3: Define the trading bot function


def trading_bot():
    
    symbol = 'AAVEUSDT'
    
    type = 'market'
    timeframe = '1h'
    limit = 200
    ohlcv = bybit.fetch_ohlcv(symbol, timeframe)

    #higher timeframe market direction
    ohlcv = bybit.fetch_ohlcv(symbol, timeframe='1h')
    df = pd.DataFrame(ohlcv, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
    df.set_index('Timestamp', inplace=True)
    print(df)
    df.ta.ema(length=50, append=True)
    df.ta.ema(length=100, append=True)
    df.ta.vwma(length=21, append=True)
    df.ta.vwap(append=True)
    print(df)

    #signal
    df["signal"] = 0
    df.loc[(df["VWAP_D"] > df["EMA_50"]) & (df["Close"] > df["EMA_50"]) & (df["Close"] > df["EMA_100"]), "signal" ]= 1 #buy

    df.loc[(df["VWAP_D"] < df["EMA_50"]) & (df["Close"] < df["EMA_50"]) & (df["Close"] < df["EMA_100"]), "signal" ]= 2 #sell

    #short revesalsignal
    df["revesalsignal"] = 0

    #in a downtrend 
    df.loc[df["VWMA_21"] < df["VWAP_D"], "revesalsignal" ]= 1 #inside reversal
    df.loc[df["VWMA_21"] > df["VWAP_D"], "revesalsignal" ]= 2 #outside reversal
    print(df)


    #entry signal
    df["entrysignal"] = 0

    #in a downtrend 
    df.loc[df["Close"] > df["VWAP_D"], "entrysignal" ]= 1 
    df.loc[df["High"] > df["VWAP_D"], "entrysignal" ]= 2 
    print(df)

    # Define the conditions for short trades
    
    df["short_condition"] = 1

    df.loc[(df["entrysignal"] == 2 ) & (df["signal"] == 2) & (df["revesalsignal"] == 2),"short_condition" ] = 2
    #short_condition= ((df["entrysignal"] == 2 ) & (df["signal"] == 2) & (df["revesalsignal"] == 2)) 


    # Filter the DataFrame based on the conditions
    #short_trades = df.loc[short_condition]
    
    print(df)
    
    
    positions = session.get_positions(
        category="linear",
        symbol= symbol,
    )

    print(positions)
    check_positions = [position for position in positions if 'AAVE' in position['symbol']]
    #print(f"open position {positions}")
    #openorder = bybit.fetch_open_orders(symbol='AAVE/USDT')

        
    if not check_positions:
        # Step 6: Implement the trading strategy
        for i, row in df.iterrows():
            
            
            if df['short_condition'].iloc[-1] > 1:

                
                response = session.place_order(
                    category="linear",
                    symbol="AAVEUSDT",
                    side="Sell",
                    orderType="Market",
                    qty="0.1",
                    timeInForce="GTC",
                )
                
                
                print(f"short order placed: {response}")
                #print(f"short order placed:")
                time.sleep(60)
                break
                
                
            else:
                print(f"checking for short signals")
                
                time.sleep(60)
                break
                
                
                
    else:
        print("There is already an open position.")
            
        time.sleep(30)

    
    
# Run the trading_bot function
trading_bot()

schedule.every(1).minutes.do(trading_bot)
# Call the trading_bot function every 2 minutes
while True:
    schedule.run_pending()
    time.sleep(20)
    

