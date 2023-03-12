import numpy as np

from tactics.support.api import *
from tactics.support.objects import *
from tactics.support import indicator
from tactics.support import toolkit
import math
import datetime
import utils.date_utils as date_utils

config=Config(name='多方炮-市场景气度', release=True)

'''
多方炮就是“阳—阴—阳”这样3根K线的组合，即两阳加一阴的K线形态。但是，满足这一个条件并不代表接下来股价就一定会有一大波拉升，还要看成交量。
一定要满足放量反弹，缩量回调才行。需要注意的是，在K线形态上出现两阳夹一阴的同时，量能也是两根放量的量能和一个缩量的调整，
最后一根量能越大，K线形成大阳线，反弹的强度也就越大。
'''

def init(context):
    print('analysing: ' + context.symbol)
    context.loss_percent = 0.03
    context.win_percent = 0.08
    context.count=120
    subscribe(context, context.symbol, context.count, on_bar)

    return True


def on_bar(context, bars):
    #print(context.now.strftime('%Y-%m-%d'))
    if len(bars) < context.count:
        return
    if context.share['name'].startswith('ST') or context.share['name'].startswith('*'): #非 ST
        return

    position = get_position(context, context.symbol)
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

    week_df = resample(bars, 'w')
    dif, dea, hist = indicator.macd(week_df['close'])
    up_index, down_index = toolkit.find_cross_pins(dif, dea)
    if len(up_index) > 0 and len(down_index) > 0 and up_index[-1] > down_index[-1] and dif[-1] > dif[-2] and dif[-1] > 0:
        if  first_bar['pct_chg'] > 0 and prev_bar['pct_chg'] < 0 and bar['pct_chg'] > 0 and bar['close'] > first_bar['close'] and bar['high'] < bar['close'] * 1.02: #两阳夹一阴
            if prev_bar['pct_chg'] * -1 < first_bar['pct_chg'] and prev_bar['pct_chg'] * -1 < bar['pct_chg']:
                if first_bar['vol'] > prev_bar['vol'] * 1.1 and bar['vol'] > prev_bar['vol'] * 1.3: #中间缩量
                    ma5 = indicator.ma(bars['close'], 5)
                    ma10 = indicator.ma(bars['close'], 10)
                    ma30 = indicator.ma(bars['close'], 30)
                    ma60 = indicator.ma(bars['close'], 60)
                    maxMa = max(ma5[-1], ma10[-1],  ma30[-1], ma60[-1])
                    minMa = min(ma5[-1], ma10[-1],  ma30[-1], ma60[-1])
                    if maxMa < minMa * 1.08 and ma10[-1] > ma30[-1] and ma30[-1] > ma60[-1]:  # 五线合一
                        if bar['close'] > max([ma5[-1], ma10[-1], ma30[-1], ma60[-1]]): #在 四线上方
                            if ma30[-1] >= ma60[-1] and ma5[-1] > ma10[-1]:
                                if bar['pct_chg'] > 2:
                                    suggest = 'Buy'
                                    weight = bar['vol'] / prev_bar['vol']

    if suggest == 'Buy':
        buy(context, context.symbol, bar['close'], weight=weight, remark='同时选出 4 只以上代表市场景气度满足入场条件，选出越多景气度越高')
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
        start_date='20210101'
    )