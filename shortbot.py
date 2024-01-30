
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
bybit.options["dafaultType"] = 'future'
bybit.load_markets()
def get_balance():
    params ={'type':'swap', 'code':'USDT'}
    account = bybit.fetch_balance(params)['USDT']['total']
    print(account)
get_balance()
#stoploss



#Step 4: Fetch historical data
symbol = 'AAVE/USDT'
amount = 0.7 
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
df.loc[df["VWAP_D"] < df["Close"], "entrysignal" ]= 1 
df.loc[df["VWAP_D"] < df["High"], "entrysignal" ]= 2 
print(df)

# Define the conditions for short trades

short_condition= ((df["entrysignal"] >= 1 ) & (df["signal"] == 2) & (df["revesalsignal"] == 2)) 


  
# Filter the DataFrame based on the conditions
short_trades = df.loc[short_condition]
print(df)

# Step 3: Define the trading bot function

def trading_bot(df):
    try:

        positions = bybit.fetch_positions()
        print(positions)
        check_positions = [position for position in positions if 'AAVE' in position['symbol']]
        #print(f"open position {positions}")
        openorder = bybit.fetch_open_orders(symbol='AAVE/USDT')

        
        if not check_positions:
            # Step 6: Implement the trading strategy
            for i, row in df.iterrows():
                
                if not short_trades.empty:
                    
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
            positions = bybit.fetch_positions()
            #print(f"{positions}information")
    
            for position in positions:
                if abs(position['contracts']) > 0:
                    

                    ids = position['id']
                    symbol = position['symbol']
                    entryPrice = position['entryPrice']
                    amount = position['contracts']
                    
                    print(f"{symbol} and {entryPrice}, {amount}")
                    
                    if position['unrealizedPnl'] is None or position['initialMargin'] is None:
                        print("Skipping position pnl due to value being zero")
                        continue
                    
                    #pnl = position['unrealizedPnl'] / position['initialMargin'] * 100
                    pnl = position['unrealizedPnl'] * 100

                    
                    print(f"pnl {pnl} percent")
                    
                     #6X LEVERAGAE stopless = 2.39 X 6= and tp= 3.62 x 6= 20.34  
                    if pnl <= -23.8 or pnl >=  35.6:
                    #print(f"Closing position for {symbol} with PnL: {pnl}%")
                    
                        print(f"Closing position for {symbol} with PnL: {pnl}%")
                    
                        response = session.get_positions(
                            category="linear",
                            symbol="AAVEUSDT",
                        )
                        print(f"{response}information")
                        positions = response['result']['list']
                        for position in positions:
                            unrealized_pnl = position['unrealisedPnl']
                            size = position['size']
                            
                            side = 'Buy'
                            symbol = position['symbol']
                            order = session.place_order(
                                category="linear",
                                symbol=symbol,
                                side=side,
                                orderType="Market",
                                qty=size,
                                timeInForce="GTC",
                            )
                            
                            
                        print(f"long order placed: {order}")
                        if order:
                            print(f"Position closed: {order}")
                    
                
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
trading_bot(df)

schedule.every(1).minutes.do(trading_bot, df)
# Call the trading_bot function every 2 minutes
while True:
    schedule.run_pending()
    time.sleep(20)

