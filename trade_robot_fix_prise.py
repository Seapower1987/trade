#!/usr/bin/env python
# coding: utf-8
import requests

from opt import KEY, SECRET
from binance.client import Client
import time
import sys

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


# Trade
symbol = 'ETHUSDT'
interval = '5m'
quantity = 10
short_ema = 9
long_ema = 21
leverage = 10
limit = '200'


def ema(s, n):
    ema = []
    j = 1
    sma = sum(s[:n]) / n
    multiplier = 2 / float(1 + n)
    ema.append(sma)
    ema.append(((s[n] - sma) * multiplier) + sma)

    for i in s[n + 1:]:
        tmp = ((i - ema[j]) * multiplier) + ema[j]
        j = j + 1
        ema.append(tmp)

    return ema


def check_decimals(symbol):
    info = client.get_symbol_info(symbol)
    val = info['filters'][2]['stepSize']
    decimal = 0
    is_dec = False
    for c in val:
        if is_dec is True:
            decimal += 1
        if c == '1':
            break
        if c == '.':
            is_dec = True
    return decimal


def get_quan(symbol):
    res = client.get_symbol_ticker(symbol=symbol)
    value = float(res['price'])
    return value


def get_data():
    res = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    return_data = []
    for each in res:
        return_data.append(float(each[4]))
    return return_data


def get_tick_and_step_size(symbol):
    tick_size = None
    step_size = None
    info = client.futures_exchange_info()
    for each in info['symbol']:
        if(each['symbol'] != symbol):
            continue

        symbol_info = each

        for filt in symbol_info['filters']:
            if filt['filterType'] == 'PRICE_FILTER':
                tick_size = float(filt['tickSize'])
            elif filt['filterType'] == 'LOT_SIZE':
                step_size = filt['stepSize']

        return str(step_size).rstrip('0')

def place_order(symbol, typ):
    if(typ == 'BUY'):
        try:
            client.futures_change_leverage(symbol=symbol, leverage=leverage)
            QUAN = float(quantity / get_quan(symbol))
            QUAN = round(QUAN,len(get_tick_and_step_size(symbol).split(".")[1]));print(QUAN)
        except Exception as error:
            print('Failed for some reason ', str(QUAN), str(error))
            return
        try:
            print(client.futures_create_order(symbol=symbol, quantity=QUAN, type='MARKET', side=typ,reduceOnly=True))
            prt(f'Open order {symbol}')
        except Exception as error:
            print('Order exit failed ', symbol, str(error))
        try:
            print(client.futures_create_order(symbol=symbol, quantity=QUAN, type='MARKET', side=typ))
            prt(f'Open order {symbol}')
        except Exception as error:
            print('Order opening failed ', symbol, str(error))

    elif(typ== 'SELL'):

        try:
            client.futures_change_leverage(symbol=symbol, leverage=leverage)
            QUAN = float(quantity / get_quan(symbol))
            QUAN = round(QUAN, len(get_tick_and_step_size(symbol).split(".")[1]));prt(QUAN)
            print(client.futures_create_order(symbol=symbol, quantity=QUAN, type='MARKET', side=typ,reduceOnly=True))
            prt(f'Open order {symbol}')
        except Exception as error:
            print('Order exit failed ', symbol, str(error))
        try:
            print(client.futures_create_order(symbol=symbol, quantity=QUAN, type='MARKET', side=typ))
            prt(f'Open order {symbol}')
        except Exception as error:
            print('Order opening failed ', symbol, str(error))


def main():
    last_ema50 = None
    last_ema200 = None
    buy = True
    sell = False
    prt("Script Running...")
    order_history = client.get_all_orders(symbol=symbol, limit=1)
    if (len(order_history)):
        if (order_history[0]['side'] == 'BUY'):
            buy = True
            sell = False
        else:
            buy = False
            sell = True

    prt("Looking for new Trades....");
    prt(f"Watching {symbol}")
    while True:
        data = get_data()
        price = get_quan(symbol)
        # print(price)
        ema50 = ema(data, short_ema)[-1]
        ema200 = ema(data, long_ema)[-1]
        # print(ema50, ema200)

        if (ema50 > ema200 and last_ema50 and not buy):
            if (last_ema50 < last_ema200):
                print("buy it")
                place_order(symbol, "BUY")
                buy = True
                sell = False

        if (ema200 > ema50 and last_ema50 and not sell):
            if (last_ema200 < last_ema50):
                place_order(symbol, "SELL")
                sell = True
                buy = False

        last_ema50 = ema50
        last_ema200 = ema200
        time.sleep(2)

if __name__ == '__main__':
    main()


