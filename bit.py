import schedule
import time
from pybit.unified_trading import HTTP

api_key = "i1UQddbDArbewF1ETS"
api_secret = "VHyrOH6gKFjyyPf3zkceaNskQOEWM1Vj63bP"

session = HTTP(
    api_key=api_key,
    api_secret=api_secret,
    testnet= True,
)

def kill_switch():
    try:

        response = session.get_positions(
        category="linear",
        symbol="DOGEUSDT",

        )
        #print(response)
        orders = response["result"]["list"]
        for order in orders:
            symbol =order['symbol']
            unrealised =float (order['unrealisedPnl'])
            positionim = float(order['positionBalance'])
            if order['unrealisedPnl'] is None or order['positionIM'] is None:
                print("Skipping position pnl due to value being zero")
                continue
            pnl = (unrealised/ positionim )* 100
            print(pnl)
            print(f"pnl {pnl} percent")
                        #10 x leverage= tp =1.02 and sl=0.71
                

            if pnl <= -14.4 or pnl >= 22:
                print(f"Closing position for {symbol} with PnL: {pnl}%")
                order['size']
                if order['side'] == 'Sell':
                    side = 'Buy'
                    symbol =order['symbol']
                    size =order['size']
                    response = session.place_order(
                        category="linear",
                        symbol=symbol,
                        side=side,
                        orderType="Market",
                        qty=size,
                        timeInForce="GTC",
                    )
                    
                    if response:
                        print(f"Position closed: {order}")
                else:
                    side = 'Sell'
                    symbol =order['symbol']
                    size =order['size']
                    response = session.place_order(
                        category="linear",
                        symbol=symbol,
                        side=side,
                        orderType="Market",
                        qty=size,
                        timeInForce="GTC",
                    )
                    if order:
                        print(f"Position closed: {order}")
            else:
                pass
    except:
        pass
kill_switch()
schedule.every(20).seconds.do(kill_switch)

while True:
    

    kill_switch()
    time.sleep(20)
    

