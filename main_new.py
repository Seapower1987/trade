import sys
from opt import SECRET, KEY
from binance.um_futures import UMFutures
import time
import numpy as np
import talib
from source import price

from apiLib import cryptoApi

'''Options'''
INTERVAL = '15m'
client = UMFutures(key=KEY, secret=SECRET)

crypto = cryptoApi({
    'APIURI': 'http://185.232.164.52:3000/api',
    'APIKEY': 'testapikey'
})

crypto.sendLog({
    'text': 'BOT STARTED'
})

SYMBOL_list = crypto.getPaares()
if len(SYMBOL_list) == 0:
    crypto.sendLog({
        "text": "No cryptopares returned from API"
    })

def get_data(symbol):
    SYMBOL = symbol
    klines = client.klines(symbol=SYMBOL, interval=INTERVAL, limit=100)
    return_data = []
    for each in klines:
        return_data.append(float(each[4]))
    return np.array(return_data)


''' Trade options '''

sl = [0]
tp = [0]

QNTY_list = []

def place_order(order_type, symbol):
    buy_price = price(symbol)
    summ = (30 * 20) / buy_price
    QNTY_list.append(summ)
    QNTY = int(QNTY_list[0])
    print(QNTY)

    if (order_type == 'BUY'):
        order = client.new_order(symbol=symbol, side=order_type, type='MARKET', quantity=QNTY)
        print(order)

        stop = buy_price - ((buy_price / 100) * 0.5)
        sl.clear()
        sl.append(stop)
        target = buy_price + ((buy_price / 100) * 2)
        tp.clear()
        tp.append(target)
        print('____________________________________________________________________')

    if (order_type == 'SELL'):
        order = client.new_order(symbol=symbol, side=order_type, type='MARKET', quantity=QNTY)
        print(order)


def trade_rsi(sym):
    SYMBOL = sym
    closing_data = get_data(SYMBOL)
    rsi = talib.RSI(closing_data, 7)[-1]
    return rsi


def main(sym):
    buy = False
    sell = True
    SYMBOL = sym

    while True:
        try:
            closing_data = get_data(SYMBOL)
            rsi = talib.RSI(closing_data, 7)[-1]
            print(SYMBOL)
            print('RSI: ' + str(rsi))

            if (rsi <= 30 and not buy):
                place_order('BUY', SYMBOL)
                buy = not buy
                sell = not sell
                crypto.sendLog({
                    "text": "Бот закупается(__BUY__)",
                    "symbol": SYMBOL,
                    "addit": ['Take Profit: ' + str(tp[0]), 'Stop Loss: ' + str(sl[0])]
                })
                #print('___BUY__')
                #print(SYMBOL)
                #print('Take Profit: ' + str(tp[0]))
                #print('Stop Loss: ' + str(sl[0]))

                while True:
                    try:
                        if (rsi >= 70 and not sell):
                            place_order('SELL', SYMBOL)
                            buy = not buy
                            sell = not sell
                            crypto.sendLog({
                                "text": "Профит! TAKE PROFIT!!!"
                            })
                            #print('TAKE PROFIT!!!')
                            break

                        elif price(SYMBOL) <= sl[0]:
                            place_order('SELL', SYMBOL)
                            crypto.sendLog({
                                "text": "STOP LOSS"
                            })
                            #print('STOP LOSS')
                            break

                        else:
                            continue

                    except Exception as error:
                        crypto.sendLog({
                                "text": "Error occured in main. 2nd while loop", 
                                "addit": [str(error)]
                        })
                        print(error)
                        time.sleep(60)
                        continue
            else:
                break
        except Exception as error:
            crypto.sendLog({
                "text": "Error occured in main. 1st while loop", 
                "addit": [str(error)]
            })
            print(error)
            continue


while True:
    try:
        for i in SYMBOL_list:
            main(sym=i)
            time.sleep(1)

    except Exception as error:
        crypto.sendLog({
            "text": "Error occured in while loop", 
            "addit": [str(error)]
        })
        print(error)
        time.sleep(60)
        continue
