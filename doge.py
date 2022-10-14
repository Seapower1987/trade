#!/usr/bin/env python
# coding: utf-8


from opt import KEY, SECRET
from binance.client import Client
import pandas as pd
import time
import ta
from binance.exceptions import BinanceAPIException
from bot import prt

client = Client(KEY, SECRET)

interval = '1h'
qty = '3600m UTC'
symbol = 'DOGEUSDT'

trend_list = []
price_list = []

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

def strategy():

    df = klines('DOGEUSDT')

    price = df.Close.iloc[-1]

    if ta.trend.macd_diff(df.Close).iloc[-1] > 0 and ta.trend.macd_diff(df.Close).iloc[-2] < 0:
        prt(f'Найден сигнал: BUY!!!')
        trend_list.append('buy')
        price_list.append(price + 2)


    elif ta.trend.macd_diff(df.Close).iloc[-1] < 0 and ta.trend.macd_diff(df.Close).iloc[-2] > 0:
        prt('Найден сигнал: SELL!!!')
        trend_list.append('sell')
        price_list.append(price + 2)

    print('Ждем индикатор MACD')


def trade():
    if len(trend_list) == 0:
        strategy()
    else:
        if trend_list == 'buy':
            tp_20 = price_list[0] + 0.0002
            tp_30 = price_list[0] + 0.0003
            tp_40 = price_list[0] + 0.0004
            sl = price_list[0] - 0.00015
            prt(f'Цели:\n'
                f'{tp_20}\n'
                f'{tp_30}\n'
                f'{tp_40}\n'
                f'Стоп:\n'
                f'{sl}\n')
            time.sleep(300)
            trend_list.clear()
            price_list.clear()

        elif trend_list == 'sell':
            tp_20 = price_list[0] - 0.0002
            tp_30 = price_list[0] - 0.0003
            tp_40 = price_list[0] - 0.0004
            sl = price_list[0] + 0.00015
            prt(f'Цели:\n'
                f'{tp_20}\n'
                f'{tp_30}\n'
                f'{tp_40}\n'
                f'Стоп:\n'
                f'{sl}\n')
            time.sleep(300)
            trend_list.clear()
            price_list.clear()



while True:
    trade()