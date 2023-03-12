import numpy as np

from tactics.support.api import *
from tactics.support.objects import *
from tactics.support import indicator
import math
import datetime
import utils.date_utils as date_utils

config=Config(name='测试', release=False)

'''
数据测试
'''

def init(context):
    print('analysing: ' + context.symbol)
    context.loss_percent = 0.03
    context.win_percent = 0.08
    context.count=200
    subscribe(context, context.symbol, context.count, on_bar)
    subscribe_index(context, '000001')

    return True

def on_bar(context, bars):
    print('analysing: ' + date_utils.date2str(context.now))
    if len(bars) < context.count:
        return
    if context.share['name'].startswith('ST') or context.share['name'].startswith('*'): #非 ST
        return

    position = get_position(context, context.symbol)
    if len(position) > 0:
        handle_sell(context, bars, position)
    else:
        handle_buy(context, bars)


def finished(context, bars):
    pass
    #print('============================Share')
    #print(bars['close'])
    #print('============================Index')
    #print(context.data_index['000001'])
    #print('============================Basic')
    #df = get_share_basic(context.symbol, date_utils.date2str(context.now))
    #print(df)


def handle_buy(context, bars):
    bar = bars.iloc[-1]
    suggest = 'None'
    if suggest == 'Buy':
        buy(context, context.symbol, bar['close'])
        print('Buy {} on {}'.format(context.share['name'], context.now.strftime('%Y-%m-%d')))


def handle_sell(context, bars, position):
    bar = bars.iloc[-1]
    suggest = 'None'
    if suggest == 'Sell':
        sell(context, context.symbol, bar['close'])
        print('Sell {} on {}'.format(context.share['name'], context.now.strftime('%Y-%m-%d')))


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
        type='fulltest',
        symbol='000100',
        start_date='20220801'
    )