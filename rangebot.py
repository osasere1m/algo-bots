#  check adx in hft time 4 hr if greater than 25
# use stockcastic rsi in lower ft 30 or 1 hr



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
    #Fetch historical data for hft 

    hft_symbol = 'RNDR/USDT'
    amount = 0.7 
    type = 'market'
    hft_timeframe = '4h'
    limit = 200
    ohlcv = bybit.fetch_ohlcv(symbol=hft_symbol, timeframe= hft_timeframe)

    # Convert the data into a pandas DataFrame for easy manipulation
    df = pd.DataFrame(ohlcv, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
    df.set_index('Timestamp', inplace=True)
    print(df)
    a = ta.adx(df['high'], df['low'], df['close'], length = 14)
    df = df.join(a, append=True)
    print(df)


    symbol = 'RNDR/USDT'
    
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

    
    df.ta.stochrsi(length=14, append=True)
    

    print(df)

    # Define the conditions for short and long trades
    #signal
    df["signal"] = 0
    df.loc[(df["ADX_14"] > df["EMA_50"]) & (df["Close"] > df["EMA_50"]) & (df["Close"] > df["EMA_100"]), "signal" ]= 1 #buy

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
    df.loc[(df["entrysignal"] == 1 ) & (df["signal"] == 1) & (df["revesalsignal"] == 1), "long_condition"] = 2


    print(df)

    # Filter the DataFrame based on the conditions

    #print(long_trades)

    try:
        # Check if there is an open trade position
        positions = bybit.fetch_positions()
        print(positions)
        check_positions = [position for position in positions if 'RNDR' in position['symbol']]
        #print(f"open position {positions}")
        #openorder = bybit.fetch_open_orders(symbol='RNDR/USDT')

        
        if not check_positions:
            # Step 6: Implement the trading strategy
            for i, row in df.iterrows():

                 # Step 7: Check for signals and execute trades
                if df['long_condition'].iloc[-1] > 1:

                     
                    response = session.place_order(
                        category="linear",
                        symbol="RNDRUSDT",
                        side="Buy",
                        orderType="Market",
                        qty="2",
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

