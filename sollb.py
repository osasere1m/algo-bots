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

bybit = ccxt.bybit({
    'apiKey': 'LQLW7aAhcalaYMAiUe',
    'secret': 'X02KF8x2VVXuXDQmoWAd8TCXx3dS7M7fAaKD',
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',
        'adjustForTimeDifference': True
    }
})

api_key = "LQLW7aAhcalaYMAiUe"
api_secret = "X02KF8x2VVXuXDQmoWAd8TCXx3dS7M7fAaKD"

session = HTTP(
    api_key=api_key,
    api_secret=api_secret,
    testnet= False,
)
#bybit.set_sandbox_mode(True) # activates testnet mode

#bybit future contract enable
bybit.options["dafaultType"] = 'future'
#load market
bybit.load_markets()

#get future account balance
def get_balance():
    params ={'type':'swap', 'code':'USDT'}
    account = bybit.fetch_balance(params)['USDT']['total']
    print(account)
get_balance()










# Step 3: Define the trading bot function

def trading_bot():
    #Fetch historical data
    symbol = 'SOL/USDT'
    amount = 0.7 
    type = 'market'
    timeframe = '1h'
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
    df.ta.ema(length=21, append=True)
    df.ta.ema(length=50, append=True)
    df.ta.vwap(append=True)
    df.ta.vwma(length=21, append=True)

    print(df)

    # Define the conditions for short and long trades
    #signal
    df["signal"] = 0
    df.loc[(df["VWAP_D"] > df["EMA_50"]) & (df["Close"] > df["EMA_50"]) & (df["Close"] > df["EMA_100"]), "signal" ]= 1 #buy

    df.loc[(df["VWAP_D"] < df["EMA_50"]) & (df["Close"] < df["EMA_50"]) & (df["Close"] < df["EMA_100"]), "signal" ]= 2 #sell
    print(df)
    #revesalsignal
    df["revesalsignal"] = 0


    df.loc[df["VWAP_D"] > df["VWMA_21"], "revesalsignal" ]= 1 #end of reversal
    df.loc[df["VWAP_D"] < df["VWMA_21"], "revesalsignal" ]= 2 #inside reversal
    print(df)


    #entry signal
    df["entrysignal"] = 0

    #in a downtrend 
    df.loc[df["Close"] < df["VWAP_D"], "entrysignal" ]= 1 
    df.loc[df["Low"] < df["VWAP_D"], "entrysignal" ]= 2 
    print(df)


    # Define the conditions for short trades
    df["long_condition"] = 1
    df.loc[(df["entrysignal"] >= 1 ) & (df["signal"] == 1) & (df["revesalsignal"] == 1), "long_condition"] = 2


    print(df)

    # Filter the DataFrame based on the conditions

    #print(long_trades)

    try:
        # Check if there is an open trade position
        positions = bybit.fetch_positions()
        print(positions)
        check_positions = [position for position in positions if 'SOL' in position['symbol']]
        #print(f"open position {positions}")
        #openorder = bybit.fetch_open_orders(symbol='RNDR/USDT')

        
        if not check_positions:
            # Step 6: Implement the trading strategy
            for i, row in df.iterrows():

                 # Step 7: Check for signals and execute trades
                if df['long_condition'].iloc[-1] > 1:

                     
                    response = session.place_order(
                        category="linear",
                        symbol="SOLUSDT",
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
            
            time.sleep(30)

    except ccxt.RequestTimeout as e:
        print(f"A request timeout occurred: {e}")
        # Handle request timeout error

    except ccxt.AuthenticationError as e:
        print(f"An authentication error occurred: {e}")
        # Handle authentication error

    except ccxt.ExchangeError as e:
        print(f"An exchange error occurred: {e}")
        # Handle exchange error

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # Handle all other unexpected errors

# Run the trading_bot function
trading_bot()

schedule.every(1).minutes.do(trading_bot)
# Call the trading_bot function every 2 minutes
while True:
    schedule.run_pending()
    time.sleep(20)

