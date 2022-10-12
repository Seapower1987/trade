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

interval = '1h'
qty = '360m UTC'
symbol = 'DOGEUSDT'

trend_list = []
trade_qty = []

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
    # one = ("{:.10f}".format(float(num)))
    one = round(num, 10)

    return one


def strategy(strat=False):
    df = klines('DOGEUSDT')
    price = df.Close[-1]

    qty = round((9 / df.Close.iloc[-1]) * 20) / 2
    print(indicators())

    one = first_indicator() * 100000
    ind = float(one)
    print(ind)

    indicator = first_indicator() * 100000
    one1 = float(indicator)

    macd_list1 = []
    macd_list1.append(ind)

    macd1 = float(macd_list1[0])

    stop_target = macd1 - one1

    # prt('Robot is Running)

    if ind > 0.2 and ta.trend.macd_diff(df.Close).iloc[-2] < 0:
        prt(f'Найден сигнал: BUY!!!')
        prt('BUY')

        while True:
            print(str(one1))
            if one1 > 2.0:
                trade_qty.append(qty)
                quantity = int(trade_qty[0])
                order_buy = client.futures_create_order(symbol='DOGEUSDT', quantity=quantity, type='MARKET', side='BUY')
                prt(str(order_buy))
                print(indicators())
                trend_list.append('buy')
                break


    elif ind < -0.2 and ta.trend.macd_diff(df.Close).iloc[-2] > 0:
        prt('Найден сигнал: SELL!!!')
        prt('SELL')
        while True:
            print(str(one1))
            if one1 < -2.0:
                trade_qty.append(qty)
                quantity = int(trade_qty[0])
                order = client.futures_create_order(symbol=symbol, quantity=quantity, type='MARKET', side='SELL')
                prt(str(order))
                print(indicators())
                trend_list.append('sell')
                break

    print('Ждем индикатор MACD')


def trade():
    df = klines('DOGEUSDT')

    buy_price = df.Close.iloc[-1]

    if len(trend_list) == 0:
        strategy()
    else:
        quantity = int(trade_qty[0])
        print(f'Trade in progress')
        while True:
            prise = df.Close.iloc[-1]
            if trend_list == 'buy':
                tp = prise - buy_price
                if tp <= -0.0003:
                    order_buy = client.futures_create_order(symbol='DOGEUSDT', quantity=quantity,
                                                            type='MARKET',
                                                            side='BUY')
                    prt(order_buy)
                elif tp >= 0.00015:
                    order_sell = client.futures_create_order(symbol='DOGEUSDT', quantity=quantity,
                                                             type='MARKET',
                                                             side='SELL')
                    prt(order_sell)

            elif trend_list == 'sell':
                tp = prise - buy_price
                if tp <= 0.0003:
                    order_sell = client.futures_create_order(symbol='DOGEUSDT', quantity=quantity,
                                                             type='MARKET',
                                                             side='SELL')
                    prt(order_sell)
                elif tp >= -0.00015:
                    order_buy = client.futures_create_order(symbol='DOGEUSDT', quantity=quantity,
                                                            type='MARKET',
                                                            side='BUY')
                    prt(order_buy)


while True:
    trade()
