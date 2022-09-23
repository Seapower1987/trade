#!/usr/bin/env python
# coding: utf-8
import requests

import requests
from opt import KEY, SECRET
from binance.client import Client
import pandas as pd
import time
import ta
from binance.exceptions import BinanceAPIException

client = Client(KEY, SECRET)

interval = '5m'
qty = '200m UTC'
symbol = 'DOGEUSDT'

'''order_buy = client.futures_create_order(symbol='DOGEUSDT', quantity=8, type='MARKET', side='BUY')
order_sell = client.futures_create_order(symbol='DOGEUSDT', quantity=8, type='MARKET', side='SELL')
close = client.futures_cancel_orders()'''


telegram_delay = 12
bot_token = '5716671380:AAGBMesgbDX9VG3szrHzSLwf-TsQBlbzqL0'
chat_id = '1275941438'


def getTPSLfrom_telegram():
    strr = 'https://api.telegram.org/bot' + bot_token + '/getUpdates'
    response = requests.get(strr)
    rs = response.json()
    # print(rs)
    if (len(rs['result']) > 0):
        rs2 = rs['result'][-1]
        rs3 = rs2['message']
        textt = rs3['text']
        datet = rs3['date']

        if (time.time() - datet) < telegram_delay:
            if 'quit' in textt:
                quit()
            if 'exit' in textt:
                exit()
            if 'hello' in textt:
                telegram_bot_sendtext('Hello. How are you?')


def telegram_bot_sendtext(bot_message):
    bot_token2 = bot_token
    bot_chatID = chat_id
    send_text = 'https://api.telegram.org/bot' + bot_token2 + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()


def prt(message):
    # telegram message
    telegram_bot_sendtext(message)
    print(str(message))


def klines(symbol):
    try:
        df = pd.DataFrame(client.get_historical_klines(symbol, interval, qty))
    except BinanceAPIException as error:
        print(error)
        time.sleep(60)
        df = pd.DataFrame(client.get_historical_klines(symbol, interval, qty))
    df = df.iloc[:, :6]
    df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    df = df.set_index('Time')
    df.index = pd.to_datetime(df.index, unit='ms')
    df = df.astype(float)
    return df


def indicators():
    df = klines('DOGEUSDT')
    one = ta.trend.macd_diff(df.Close).iloc[-1]
    two = ta.trend.macd_diff(df.Close).iloc[-2]
    prise = df.Close.iloc[-1]

    return one, two, prise


def first_indicator():
    df = klines('DOGEUSDT')
    num = ta.trend.macd_diff(df.Close).iloc[-1]
    one = ("{:.10f}".format(float(num)))
    return one

def strategy(strat=False):
    df = klines('DOGEUSDT')


    while True:

        if ta.trend.macd_diff(df.Close).iloc[-1] > 0 and ta.trend.macd_diff(df.Close).iloc[-2] < 0:
            prt(f'Signal of MACD is BUY find!!!')
            #order_buy = client.futures_create_order(symbol='DOGEUSDT', quantity=5, type='MARKET', side='BUY')
            #prt(str(order_buy))
            strat = True
            return strat



        elif ta.trend.macd_diff(df.Close).iloc[-1] < 0 and ta.trend.macd_diff(df.Close).iloc[-2] > 0:
            prt('Signal of MACD is SELL find!!!')
            prt('SELL: ', str(df.Close[-1]))
            #order = client.futures_create_order(symbol=symbol, quantity=5, type='MARKET', side='SELL')
            #prt(str(order))
            strat = True
            return strat

        
        break




def trade():
    df = klines('DOGEUSDT')
    one = float(ta.trend.macd_diff(df.Close).iloc[-1])
    if strategy() == True:
        if one > 2.0:
            prt('one > 2')
        elif one < -2.0:
            prt('one < -2')
    else:
        prt('Signal MACD its not found')

while True:
    trade()
