from opt import SSECRET, SKEY
import time
import pandas as pd
from binance.exceptions import BinanceAPIException
from binance.client import Client



'''Options'''
INTERVAL = '15m'
qty = '1000m UTC'
client = Client(SKEY, SSECRET)


def klines(symbol):
    try:
        df = pd.DataFrame(client.get_historical_klines(symbol, INTERVAL, qty))
    except BinanceAPIException as error:
        print(error)
        time.sleep(60)
        df = pd.DataFrame(client.get_historical_klines(symbol, INTERVAL, qty))
    df = df.iloc[:, :6]
    df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    df = df.set_index('Time')
    df.index = pd.to_datetime(df.index, unit='ms')
    df = df.astype(float)
    return df

def price(symbol):
    df = klines(symbol)
    prise = df.Close.iloc[-1]
    return prise


