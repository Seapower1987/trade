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

trend_list = ['sell']

telegram_delay = 12
bot_token = '5716671380:AAGBMesgbDX9VG3szrHzSLwf-TsQBlbzqL0'
chat_id = '1275941438'

trade_qty = []


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

    qty = round((6 / df.Close.iloc[-1]) * 20)
    print(indicators())

    one = first_indicator() * 100000
    ind = float(one)
    print(ind)



    # prt('Robot is Running)

    if ind > 0.2 and ta.trend.macd_diff(df.Close).iloc[-2] < 0:
        prt(f'Signal of MACD is BUY find!!!')
        prt('BUY')
        trade_qty.append(qty)
        quantity = int(trade_qty[0])
        order_buy = client.futures_create_order(symbol='DOGEUSDT', quantity=quantity, type='MARKET', side='BUY')
        prt(str(order_buy))
        print(indicators())

        trend_list.append('buy')



    elif ind < -0.2 and ta.trend.macd_diff(df.Close).iloc[-2] > 0:
        prt('Signal of MACD is SELL find!!!')
        prt('SELL')
        trade_qty.append(qty)
        quantity = int(trade_qty[0])
        order = client.futures_create_order(symbol=symbol, quantity=quantity, type='MARKET', side='SELL')
        prt(str(order))
        print(indicators())
        trend_list.append('sell')

    print('Wait Indicator MACD')


def trade():
    one = first_indicator() * 100000
    ind = float(one)

    df = klines('DOGEUSDT')
    price = df.Close[-1]

    macd_list1 = []
    macd_list1.append(ind)

    macd1 = float(macd_list1[0])

    if len(trend_list) == 0:
        strategy()
    else:

        print(f'Trade in progress')
        time.sleep(180)

        indicator = first_indicator() * 100000
        one1 = float(indicator)
        stop_target = macd1 - one1

        print(macd1, ' ', one1)
        print(stop_target)

        quantity = int(trade_qty[0])
        for trend in trend_list:
            if trend == 'buy':
                if one1 > 2.0:
                    while True:
                        print(stop_target)
                        if stop_target < 0:
                            macd_list1.clear()
                            break
                        elif stop_target > 0.5:
                            while True:
                                try:
                                    prt('Take Profit')
                                    order_sell = client.futures_create_order(symbol='DOGEUSDT', quantity=quantity,
                                                                             type='MARKET',
                                                                             side='SELL')
                                    prt(str(order_sell))
                                    print(price)
                                    macd_list1.clear()
                                    trend_list.clear()
                                    break
                                except Exception as error:
                                    print('Error 1022')
                                    
                        else:
                            break
                elif one1 < -0.5:
                    while True:
                        print(stop_target)
                        try:

                            prt('Stop Loss')
                            order_sell = client.futures_create_order(symbol='DOGEUSDT', quantity=quantity,
                                                                     type='MARKET',
                                                                     side='SELL')
                            prt(str(order_sell))
                            print(price)
                            trend_list.clear()
                            break
                        except Exception as error:
                            prt('Error 1022')
                            continue
                else:
                    prt(f'Trade in progress')
                    prt(f'MACD Indicator: {str(one1)}')
                    prt(f'Target MACD Indicator: {str(macd1)}')
                    macd_list1.clear()
                    macd_list1.append(one1)
                    break

            elif trend == 'sell':

                if one1 < -2.0:
                    while True:
                        print(macd1, ' ', one1)
                        print(stop_target)
                        if stop_target > 0:
                            macd_list1.clear()
                            prt('Waint Target')

                            break
                        elif stop_target < -0.5:
                            prt('Take Profit')

                            try:
                                order_buy = client.futures_create_order(symbol='DOGEUSDT', quantity=quantity,
                                                                        type='MARKET',
                                                                        side='BUY')
                                trend_list.clear()
                                prt(str(order_buy))
                                print(price)
                                print(macd1, ' ', one1)
                                break

                            except Exception as error:
                                print('Error 1022')

                        break
                elif one1 > 0.5:

                    try:
                        macd_list1.clear()
                        prt('Stop Loss')
                        order_buy = client.futures_create_order(symbol='DOGEUSDT', quantity=quantity, type='MARKET',
                                                                side='BUY')
                        prt(str(order_buy))
                        print(price)
                        trend_list.clear()
                        break

                    except Exception as error:
                        prt('Error 1022')

                else:
                    prt(f'Trade in progress')
                    prt(f'MACD Indicator: {str(one1)}')
                    prt(f'Target MACD Indicator: {str(macd1)}')
                    macd_list1.clear()
                    macd_list1.append(one1)
                    break


while True:
    trade()
