#!/usr/bin/env python
# coding: utf-8

import requests
from opt import KEY, SECRET
from binance.client import Client
import pandas as pd
import time
import ta
from binance.exceptions import BinanceAPIException

client = Client(KEY, SECRET)

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
        df = pd.DataFrame(client.get_historical_klines(symbol, '1m', '40m UTC'))
    except BinanceAPIException as error:
        print(error)
        time.sleep(60)
        df = pd.DataFrame(client.get_historical_klines(symbol, '1m', '40m UTC'))
    df = df.iloc[:, :6]
    df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    df = df.set_index('Time')
    df.index = pd.to_datetime(df.index, unit='ms')
    df = df.astype(float)
    return df


def strategy(symbol, qty, open_position=False):
    prt(symbol)
    df = klines(symbol)
    qty = round((qty / df.Close.iloc[-1]) * 20)
    prt(str(qty))


    print(ta.trend.macd_diff(df.Close).iloc[-1])
    print(ta.trend.macd_diff(df.Close).iloc[-2])
    prt('Find signal')
    if ta.trend.macd_diff(df.Close).iloc[-1] > 0 and ta.trend.macd_diff(df.Close).iloc[-2] < 0:
        prt(f'Signal of MACD is BUY find!!!    {symbol}')
        buyprice = df.Close.iloc[-1]
        prt(str(buyprice))
        order = client.futures_create_order(symbol=symbol, quantity=qty, type='MARKET', side='BUY')
        prt(str(order))
        while True:
            if ta.trend.macd_diff(df.Close).iloc[-1] < 0 and ta.trend.macd_diff(df.Close).iloc[-2] > 0:
                client.futures_cancel_orders()


    elif ta.trend.macd_diff(df.Close).iloc[-1] < 0 and ta.trend.macd_diff(df.Close).iloc[-2] > 0:
        prt(f'Signal of MACD is SELL find!!!    {symbol}')
        sellprice = df.Close.iloc[-1]
        prt(str(sellprice))
        order = client.futures_create_order(symbol=symbol, quantity=qty, type='MARKET', side='SELL')
        prt(str(order))
        while True:
            if ta.trend.macd_diff(df.Close).iloc[-1] > 0 and ta.trend.macd_diff(df.Close).iloc[-2] < 0:
                client.futures_cancel_orders()


while True:
    strategy('DOGEUSDT', qty=12)
