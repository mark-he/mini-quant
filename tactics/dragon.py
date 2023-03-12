import numpy as np

from tactics.support.api import *
from tactics.support.objects import *
from tactics.support import indicator
from tactics.support import toolkit
import math
import datetime
import utils.date_utils as date_utils

config=Config(name='龙抬头(Beta)', release=True)

'''
寻找三个月翻倍股票
'''

def init(context):
    print('analysing: ' + context.symbol)
    context.loss_percent = 0.03
    context.win_percent = 0.08
    context.count=200
    subscribe(context, context.symbol, context.count, on_bar)

    return True

def on_bar(context, bars):
    #print(context.now.strftime('%Y-%m-%d'))
    if len(bars) < context.count:
        return
    if context.share['name'].startswith('ST') or context.share['name'].startswith('*'): #非 ST
        return
    #position = get_position(context, context.symbol)
    handle_buy(context, bars)


def finished(context, bars):
    pass


def handle_buy(context, bars):
    bar = bars.iloc[-1]
    prev_bar = bars.iloc[-2]
    first_bar = bars.iloc[-3]

    suggest = 'None'
    #pct_chg 涨幅
    #vol 成交量
    weight = 0.0

    ma5 = indicator.ma(bars['close'], 5)
    ma10 = indicator.ma(bars['close'], 10)
    ma20 = indicator.ma(bars['close'], 20)
    ma60 = indicator.ma(bars['close'], 60)

    test_bars = bars.iloc[-100:]
    test = bars['close'].values[-100:].tolist()
    test5 = ma20[-100:]
    test10 = ma20[-100:]
    test20 = ma20[-100:]

    low = test.index(min(test))
    low_5 = test5.index(min(test5))
    low_10 = test10.index(min(test10))
    low_20 = test20.index(min(test20))

    if ma5[-1] > ma20[-1] and ma10[-1] > ma20[-1]:
        arr = np.array([low_5, low_10, low_20, low])
        gap = arr.ptp()
        if gap < 20:
            max_low = max(low_20, low_10, low_5, low)
            if len(test) - max_low < 20:
                if ma20[-1] > ma20[-2] > ma20[-3] and ma10[-1] > ma10[-2] > ma10[-3] and ma5[-1] > ma5[-2]:
                    week_df = resample(bars, 'w')
                    dif, dea, hist = indicator.macd(week_df['close'])
                    up_index, down_index = toolkit.find_cross_pins(dif, dea)
                    if len(up_index) > 0 and len(down_index) > 0:
                        if up_index[-1] > down_index[-1] and hist[-1] > hist[-2] and dif[-1] > dif[-2]:
                            fast, slow = indicator.obv(bars['close'], bars['vol'], 30)
                            if fast[-1] > slow[-1] and fast[-2] > slow[-2] and (fast[-1] - slow[-1] > fast[-2] - slow[-2]):
                                fs = toolkit.slope(0, fast[-10], 10, fast[-1])
                                ss = toolkit.slope(0, slow[-10], 10, slow[-1])
                                if fs > 1 and ss > 1 and fs > ss * 1.05:
                                    bar_low = test_bars.iloc[low]
                                    bar_low_next = test_bars.iloc[low + 1]
                                    if bar_low_next['close'] > bar_low['open']:
                                        weight = 8
                                    suggest = 'Buy'

    if suggest == 'Buy':
        buy(context, context.symbol, bar['close'], weight=weight, remark='寻找三月翻倍股票')
        print('Buy {} on {}'.format(context.share['name'], context.now.strftime('%Y-%m-%d')))


def reach_percent(prev, next, percent):
    upper_price = prev * (1 + percent)
    upper_price = round(math.floor(upper_price * 100) / 100, 2)  # 排除滑价
    return next >= upper_price


def on_start_run(account):
    print('start=' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


def on_stop_run(account):
    print('end=' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


if __name__ == '__main__':
    run(
        type = RUN_TYPE_ANALYSIS,
        #symbol='002119',
        #start_date='20220101'
    )