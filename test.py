import asyncio
import ccxt.async_support as ccxt
import time
import schedule
import time
import sys
import os
from pybit.unified_trading import HTTP


class Bybit(ccxt.bybit):
    def nonce(self):
        return self.safe_integer(self.options, 'customTimestamp')


async def test():
    bybit = ccxt.bybit({
    'apiKey': 'LQLW7aAhcalaYMAiUe',
    'secret': 'X02KF8x2VVXuXDQmoWAd8TCXx3dS7M7fAaKD',
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',
        'adjustForTimeDifference': True
    }
    })
    # You HAVE to fetch and set this every time before calling any private method
    customTimestamp = await bybit.fetch_time()
    bybit.options['customTimestamp'] = customTimestamp
    bybit.options["dafaultType"] = 'future'
    bybit.load_markets()
    ## YOUR CALL HERE
    #params ={'type':'swap', 'code':'USDT'}
   # account = bybit.fetch_balance(params)['USDT']['total']
    #print(account)
    
    positions = bybit.fetch_positions()
    #print(f"{positions}information")

    for position in positions:
        if abs(position['contracts']) > 0:

            ds = position['id']
            symbol = position['symbol']
            entryPrice = position['entryPrice']
            amount = position['contracts']

            type = 'market'
            orderbook = bybit.fetch_l2_order_book(symbol)
            price = orderbook['asks'][0][0]

            print(f"{symbol} and {entryPrice}, {amount}")

            if position['unrealizedPnl'] is None or position['initialMargin'] is None:
                print("Skipping position pnl due to value being zero")
                continue

            pnl = position['unrealizedPnl'] * 100

            print(f"pnl {pnl} percent")
            #10 x leverage= tp =1.02 and sl=0.71
    

            if pnl <= -14.4 or pnl >= 22:
                print(f"Closing position for {symbol} with PnL: {pnl}%")
            
                if position['side'] == 'short':
                    side = 'buy'
                    order = bybit.create_market_buy_order(symbol=symbol, amount=amount)
                    if order:
                        print(f"Position closed: {order}")
                else:
                    side = 'sell'
                    order = bybit.create_market_sell_order(symbol=symbol, amount=amount)
                    if order:
                        print(f"Position closed: {order}")
            else:
                break 
        else:
            break


    
    
    await bybit.close()

asyncio.run(test())


    
    
