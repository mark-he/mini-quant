import pandas as pd
import numpy as np
import talib


def obv(df_close, df_volume, n):
    df = talib.OBV(df_close, df_volume)
    df2 = df.ewm(span=n).mean()
    return df.values, df2.values


def cci(df, n=14):
    mcci = []
    mma = []
    for index, value in df.iterrows():
        tp = (value['high'] + value['low'] + value['close']) / 3
        mma.append(tp)
        target = None
        if len(mma) <= n:
            target = mma
        else:
            target = mma[-1 * n:]
        ma = sum(target)/len(target)
        mmd = []
        for x in target:
            mmd.append(abs(ma - x))
        if len(mmd) <= n:
            target = mmd
        else:
            target = mmd[-1 * n:]
        md = sum(target)/len(target)
        cci = 0
        if md != 0:
            cci = (tp - ma) / md / 0.015
        mcci.append(cci)
    return np.array(mcci)


def macd(df, fast=12, slow=26, signal=9):
    values = df.values
    mdif = []
    mdea = []
    mhist = []
    dif = 0
    dea = 0
    hist = 0
    ema = 0
    ema2 = 0
    for value in values:
        if len(mdif) == 0:
            ema = value
            ema2 = ema
            dea = 0
        else:
            ema = (ema * (fast - 1) / (fast + 1)) + (value * 2 / (fast + 1))
            ema2 = (ema2 * (slow - 1) / (slow + 1)) + (value * 2 / (slow + 1))
            dif = ema - ema2
            dea = (dea * (signal - 1) / (signal + 1)) + (dif * 2 / (signal + 1))
            hist = dif - dea
        mdif.append(dif)
        mdea.append(dea)
        mhist.append(hist)
    return np.array(mdif), np.array(mdea), np.array(mhist)


def ma(df, n=5):
    m = []
    avg = []
    for value in df.tolist():
        avg.append(value)
        if len(avg) > n:
            avg.pop(0)
        m.append(sum(avg)/len(avg))
    return m


def ema(df, n=5):
    return df.ewm(span=n).mean().values
