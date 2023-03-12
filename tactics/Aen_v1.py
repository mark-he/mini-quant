import numpy as np

from tactics.support.api import *
from tactics.support.objects import *
from tactics.support import indicator
import math
import datetime
from tactics.support import toolkit

config=Config(name='持有 10 天', release=True)

'''
数据测试
'''
def init(context):
    #print('analysing: ' + context.symbol)
    context.count=250
    subscribe(context, context.symbol, context.count, on_bar)
    return True

def on_bar(context, bars):
    #print('analysing: ' + date_utils.date2str(context.now))
    if len(bars) < context.count:
        return
    if context.share['name'].startswith('ST') or context.share['name'].startswith('*'): #非 ST
        return

    handle_buy(context, bars)


def finished(context, bars):
    pass


def handle_buy(context, bars):
    bar = bars.iloc[-1]
    suggest = 'None'

    c = bars['close'].values.tolist();
    matched = True

    ma5 = indicator.ma(bars['close'], 5)
    ma10 = indicator.ma(bars['close'], 10)
    ma20 = indicator.ma(bars['close'], 20)
    ma34 = indicator.ma(bars['close'], 34)
    ma60 = indicator.ma(bars['close'], 60)
    ma120 = indicator.ma(bars['close'], 120)
    low_index = 0

    V_LOW_START = 90
    V_LOW_END = 10
    if matched:
        matched = False
        min_c = min(c)
        # 出现低点
        low_index = c.index(min_c)
        if V_LOW_END < (len(c) - low_index) < V_LOW_START:
            matched = True
            print('{} pass 1'.format(context.share['name']))

    ma20_c = 0
    ma10_c = 0
    ma5_c = 0
    trade_date = None
    if matched:
        matched = False
        #近期金叉 20 + 34
        up_index, down_index = toolkit.find_cross_pins(ma20, ma34)
        if len(up_index) > 0 and up_index[-1] > down_index[-1]:
            ma20_c = up_index[-1]
            trade_date = bars['trade_date'].values.tolist()[ma20_c]
            if (len(c) - ma20_c) < 10:
                matched = True
                print('{} pass 2'.format(context.share['name']))

    if matched:
        matched = False
        #近期金叉 10 + 120
        up_index, down_index = toolkit.find_cross_pins(ma10, ma120)
        if len(up_index) > 0 and up_index[-1] > down_index[-1]:
            ma10_c = up_index[-1]
            matched = True
            print('{} pass 3'.format(context.share['name']))

    if matched:
        matched = False
        # 近期金叉 5 + 120
        up_index, down_index = toolkit.find_cross_pins(ma5, ma120)
        if len(up_index) > 0 and up_index[-1] > down_index[-1]:
            ma5_c = up_index[-1]
            matched = True
            print('{} pass 4'.format(context.share['name']))

    if matched:
        matched = False
        # 需要一个过程
        if ma5_c < ma10_c <= ma20_c:
            if 5 < ma20_c - ma5_c < 20:
                matched = True
                print('{} pass 5'.format(context.share['name']))

    if matched:
        matched = False
        # 近期金叉 5 + 10
        up_index, down_index = toolkit.find_cross_pins(ma5, ma10)
        if len(up_index) > 0 and up_index[-1] > down_index[-1]:
            matched = True
            print('{} pass 6'.format(context.share['name']))

    if matched:
        matched = False
        # 近期金叉 10 + 20
        up_index, down_index = toolkit.find_cross_pins(ma10, ma20)
        if len(up_index) > 0 and up_index[-1] > down_index[-1]:
            matched = True
            print('{} pass 7'.format(context.share['name']))

    if matched:
        suggest = 'Buy'

    if suggest == 'Buy':
        buy(context, context.symbol, bar['close'], target_date=trade_date)
        print('Buy {} on {}'.format(context.share['name'], context.now.strftime('%Y-%m-%d')))


def handle_sell(context, bars, position):
    pass

def reach_percent(prev, next, percent):
    upper_price = prev * (1 + percent)
    upper_price = round(math.floor(upper_price * 100) / 100, 2)  # 排除滑价
    return next >= upper_price

def keepdown(values, step = 10, count = 10):
    idx = len(values) - 1
    temp = values[idx]
    idx -= step
    while idx >= 0 and count > 0:
        if values[idx]:
            if temp > values[idx]:
                return False
            else:
                temp = values[idx]
                count -= 1
        else:
            return False
    if count > 0:
        return False
    else:
        return True

def compare(v1, v2, p):
    for i in range(len(v1)):
        if v1[i] is not None and v2[i] is not None:
            if abs((v1[i] - v2[i]) / v2[i]) > p:
                return False
    return True


def on_start_run(account):
    print('start=' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


def on_stop_run(account):
    print('end=' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


if __name__ == '__main__':
    run(
        type=RUN_TYPE_ANALYSIS,
        #symbol='002514',
        #start_date='20220620',
        #end_date='20220621'
    )