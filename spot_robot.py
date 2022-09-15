#!/usr/bin/env python
# coding: utf-8
import requests

from opt import KEY, SECRET
from binance.client import Client
import pandas as pd
import time

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
    print(message)

# Trade

def top_coin():
    all_tickers = pd.DataFrame(client.get_ticker())
    usdt = all_tickers[all_tickers.symbol.str.contains('USDT')]
    work = usdt[~((usdt.symbol.str.contains('UP')) | (usdt.symbol.str.contains('DOWN')))]
    top_coin = work[work.priceChangePercent == work.priceChangePercent.max()]
    top_coin = top_coin.symbol.values[0]
    return top_coin


# print(f'Find Spot:  {top_coin()}')


def last_data(symbol, interval, lookback):
    frame = pd.DataFrame(client.get_historical_klines(symbol, interval, lookback + 'min ago UTC'))
    frame = frame.iloc[:, :6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame


def strategy(by_amt, SL=0.985, Target=1.02, open_position=False):
    try:
        asset = top_coin()
        df = last_data(asset, '1m', '120')

    except:
        time.sleep(61)
        asset = top_coin()
        df = last_data(asset, '1m', '120')

    qty = round(by_amt / df.Close.iloc[-1], 1)
    if ((df.Close.pct_change() + 1).cumprod()).iloc[-1] > 1:
        prt(asset)
        prt(df.Close.iloc[-1])
        prt(qty)
        order = client.create_order(symbol=asset, side='BUY', type='MARKET', quantyty=qty)
        prt(order)
        buy_price = float(order['fills'][0]['price'])
        open_position = True

        while open_position:
            try:
                df = last_data(asset, '1m', '2')
            except:
                prt('Restart after 1 min')
                time.sleep(61)
                df = last_data(asset, '1m', '2')

            prt(f'Price ' + str(df.Close[-1]))
            prt(f'Target ' + str(buy_price * Target))
            prt(f'Stop ' + str(buy_price * SL))
            if df.Close[-1] <= buy_price * SL or df.Close[-1] >= buy_price * Target:
                order = client.create_order(symbol=asset, side='SELL', type='MARKET', quantyty=qty)
                prt(order)
                break
    else:
        prt('No find')
        time.sleep(20)


while True:
    strategy(10)


