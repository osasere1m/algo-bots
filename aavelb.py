# risk managment 1.47 = stoploss = 0.4 multiplied by leverage(10) = 4 percent takeprofit = 0.65* 10 = 6.5
# idea close below ema 50 short the close or high above ema20 with stochastic greater 70 and adx above 25
#idea long close above ema 50 and close or high below ema20 with stochastic greater 24 and adx above 25

import ccxt
import pandas as pd
import pandas_ta as ta
import numpy
import time
import schedule
from pybit.unified_trading import HTTP




# Step 3: Define the trading bot function

def trading_bot():
    bybit = ccxt.bybit()

    api_key = "LQLW7aAhcalaYMAiUe"
    api_secret = "X02KF8x2VVXuXDQmoWAd8TCXx3dS7M7fAaKD"

    session = HTTP(
        api_key=api_key,
        api_secret=api_secret,
        testnet= False,
    )
    #Fetch historical data
    symbol = 'AAVE/USDT'
    amount = 0.7 
    type = 'market'
    timeframe = '4h'
    limit = 200
    ohlcv = bybit.fetch_ohlcv(symbol, timeframe)

    # Convert the data into a pandas DataFrame for easy manipulation
    df = pd.DataFrame(ohlcv, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
    df.set_index('Timestamp', inplace=True)
    print(df)
    # Step 5: Calculate technical indicators

    #df.ta.ema(length=20, append=True)

    df.ta.ema(length=100, append=True)
    #df.ta.ema(length=21, append=True)
    df.ta.sma(length=12, append=True)
    df.ta.ema(length=50, append=True)
    

    print(df)

    # Define the conditions for short and long trades
    #signal
    df["signal"] = 0
    df.loc[(df["Close"] > df["EMA_50"]) & (df["Close"] > df["EMA_100"]), "signal" ]= 1 #buy

    
    print(df)
    #revesalsignal
    df["revesalsignal"] = 0

    df.loc[(df["SMA_12"] > df["EMA_50"]), "revesalsignal" ]= 1 #outside reversal
    df.loc[(df["SMA_12"] < df["EMA_50"]), "revesalsignal" ]= 2 #inside reversal

    print(df)


    #entry signal
    df["entrysignal"] = 0
 
    df.loc[df["Close"] < df["SMA_12"], "entrysignal" ]= 1 
    #df.loc[df["Low"] < df["SMA_12"], "entrysignal" ]= 2 
    print(df)


    # Define the conditions for short trades
    df["long_condition"] = 1
    df.loc[(df["entrysignal"] == 1 ) & (df["signal"] == 1) & (df["revesalsignal"] == 1), "long_condition"] = 2


    print(df)

    # Filter the DataFrame based on the conditions

    #print(long_trades)

    try:
        # Check if there is an open trade position
        response = session.get_positions(
        category="linear",
        symbol="AAVEUSDT",

        )
        #print(response)
        positions = response["result"]["list"]
    
        print(positions)
        check_positions = [position for position in positions if '0' in position['size']]
        

        
        if check_positions:
            # Step 6: Implement the trading strategy
            for i, row in df.iterrows():

                 # Step 7: Check for signals and execute trades
                if df['long_condition'].iloc[-1] == 2:

                    
                    response = session.place_order(
                        category="linear",
                        symbol="AAVEUSDT",
                        side="Buy",
                        orderType="Market",
                        qty="0.1",
                        timeInForce="GTC",
                    )
                    
                    
                    print(f"long order placed: {response}")
                    
                    #print(f"long order placed:")
                    time.sleep(60)
                    break

                   
                
                else:
                    print(f"checking for long signals")
                
                    time.sleep(60)
                    break
                        
                   
                    
        else:
            print("There is already an open position.")
            positions = response["result"]["list"]
            for position in positions :
                symbol =positions['symbol']
                unrealised =float (positions['unrealisedPnl'])
                positionim = float(positions['positionBalance'])
                if positions['unrealisedPnl'] is None or positions['positionIM'] is None:
                    print("Skipping position pnl due to value being zero")
                    continue
                pnl = (unrealised/ positionim )* 100
                print(pnl)
                print(f"pnl {pnl} percent")
                            #10 x leverage= tp =1.02 and sl=0.71
                    

                if pnl <= -14.4 or pnl >= 22:
                    print(f"Closing position for {symbol} with PnL: {pnl}%")
                    positions['size']
                    if positions['side'] == 'Sell':
                        side = 'Buy'
                        symbol =positions['symbol']
                        size =positions['size']
                        response = session.place_order(
                            category="linear",
                            symbol=symbol,
                            side=side,
                            orderType="Market",
                            qty=size,
                            timeInForce="GTC",
                        )
                        
                        if response:
                            print(f"Position closed: {positions}")
                    else:
                        side = 'Sell'
                        symbol =positions['symbol']
                        size =positions['size']
                        response = session.place_order(
                            category="linear",
                            symbol=symbol,
                            side=side,
                            orderType="Market",
                            qty=size,
                            timeInForce="GTC",
                        )
                        if response:
                            print(f"Position closed: {positions}")
                else:
                    pass
            
            

    except TypeError:
        print(f"An unexpected error occurred: ")
        pass

# Run the trading_bot function
trading_bot()

schedule.every(1).minutes.do(trading_bot)
# Call the trading_bot function every 2 minutes
while True:
    schedule.run_pending()
    time.sleep(20)

