import pandas as pd
from binance.um_futures import UMFutures
from opt import SECRET, KEY

client = UMFutures(key=KEY, secret=SECRET)

symbol = 'NEARUSDT'
timeframe = '1h'

quantity = 106

klines = client.klines(symbol, timeframe)
df = pd.DataFrame(klines).iloc[:, :6]
df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
df['Time'] = pd.to_datetime(df['Time'], unit='ms')
df.set_index('Time', inplace=True)

fast_ma = df['Close'].rolling(window=50).mean()
slow_ma = df['Close'].rolling(window=200).mean()


def trend_following_strategy(df, fast_ma, slow_ma):
    signal = []
    for i in range(len(df)):
        if fast_ma[i] > slow_ma[i]:
            signal.append(1)
        elif fast_ma[i] < slow_ma[i]:
            signal.append(-1)
        else:
            signal.append(0)

    return signal


signals = trend_following_strategy(df, fast_ma, slow_ma)

df['signal'] = signals


def open_order(symbol, side, quantity):
    order = client.new_order(symbol=symbol, side=side, type='MARKET', quantity=quantity)
    print('Order opened: ', order)

in_position = False


while True:
    if df['signal'].iloc[-1] == 1 and in_position == False:
        open_order(symbol, 'BUY', quantity=quantity)
        in_position = True
    elif df['signal'].iloc[-1] == -1 and in_position == False:
        open_order(symbol, 'SELL', quantity=quantity)
        in_position = True
    else:
        pass


