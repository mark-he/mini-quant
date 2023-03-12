import numpy as np

from tactics.support.api import *
from tactics.support.objects import *
from tactics.support import indicator
from tactics.support import toolkit
import math
import datetime
import utils.date_utils as date_utils

config=Config(name='妖车炮(Beta)', release=False)

'''
# 计算是否匹配
# 1、昨日是中阳线
# 2、今天是孕育线
# 3、开盘价或最低价金叉5日平均线
# 4、20日平均线上行
# 5、5日平均线大于20日平均线
# 6、今天成交量小于昨天成交量，昨天成交量大于前天成交量
# 7、MACD周金叉且张口
# 8、昨日收盘价小于10日最低价*1.15，5日最高价小于10日最低价*1.25
'''

def init(context):
    print('analysing: ' + context.symbol)
    context.count=200
    subscribe(context, context.symbol, context.count, on_bar)
    return True


def on_bar(context, bars):
    #print(context.now.strftime('%Y-%m-%d'))
    if len(bars) < context.count:
        return
    if context.share['name'].startswith('ST') or context.share['name'].startswith('*'): #非 ST
        return
    handle_buy(context, bars)


def finished(context, bars):
    pass


def check(context, bars, bar, prev_bar, first_bar):
    suggest = 'None'
    #pct_chg 涨幅
    #vol 成交量
    weight = 0.0
    #df = get_share_basic(context.symbol, date_utils.date2str(context.now))
    #basic = df.iloc[-1]
    upper_percent = 0.095
    if bar['symbol'].startswith('3'): #创业板
        upper_percent = 0.195
    trace_count = 40
    reach_count = 0
    while trace_count > 2:
        prev = bars.iloc[0 - trace_count]
        next = bars.iloc[1 - trace_count]
        if reach_percent(prev['close'], next['close'], upper_percent):
            reach_count += 1
        trace_count -= 1
    if reach_count == 0:
        return suggest, weight
    # 、市值在 15 亿到 100 亿
    #if basic['circ_mv'] > 150 * 1000 and basic['circ_mv'] < 1000 * 1000 and bar['close'] < 30:
        # 1、昨日是中阳线
    if prev_bar['pct_chg'] >= 2.5 and prev_bar['pct_chg'] <= 7.5 and prev_bar['high'] < prev_bar['close'] * 1.02 and prev_bar['low'] > prev_bar['open'] * 0.98:
        # 2、今天是孕育线
        if abs(bar['close'] - bar['open']) / bar['open'] < 0.025:
            # 3、开盘价或最低价金叉5日平均线
            ma5 = indicator.ma(bars['close'], 5)
            ma10 = indicator.ma(bars['close'], 10)
            ma20 = indicator.ma(bars['close'], 20)
            ma60 = indicator.ma(bars['close'], 60)
            if (bar['open'] > ma5[-1] and prev_bar['open'] < ma5[-2]) \
                or (bar['low'] > ma5[-1] and prev_bar['low'] < ma5[-2]):
                # 4、20日平均线上行
                if ma20[-1] > ma20[-2] > ma20[-3]:
                    # 5、5日平均线大于20日平均线
                    if ma5[-1] > ma10[-1] > ma20[-1]:
                        # 6、今天成交量小于昨天成交量，昨天成交量大于前天成交量
                        if ((bar['pct_chg'] > 0 and bar['vol'] > prev_bar['vol']) or (bar['pct_chg'] < 0 and bar['vol'] < prev_bar['vol'])) and prev_bar['vol'] > first_bar['vol']:
                            # 8、昨日收盘价小于10日最低价*1.15，5日最高价小于10日最低价*1.25
                            if prev_bar['close'] < min(bars.iloc[-10:]['low'].values) * 1.15 \
                                    and max(bars.iloc[-5:]['high'].values) < min(bars.iloc[-10:]['low'].values) * 1.25:
                                # 7、MACD周金叉且张口
                                week_df = resample(bars, 'w')
                                dif, dea, hist = indicator.macd(week_df['close'])
                                up_index, down_index = toolkit.find_cross_pins(dif, dea)
                                if len(up_index) > 0 and len(down_index) > 0:
                                    if up_index[-1] > down_index[-1] and hist[-1] > hist[-2] > hist[-3] and dif[-1] > dif[-2] > dif[-3]:
                                        suggest = 'Buy'
                                        weight = prev_bar['vol'] / bar['vol']
                                        # 四线合一
                                        maxMa = max(ma5[-1], ma10[-1], ma20[-1], ma60[-1])
                                        minMa = min(ma5[-1], ma10[-1], ma20[-1], ma60[-1])
                                        if maxMa < minMa * 1.08:  # 五线合一
                                            if bar['close'] > maxMa:
                                                if ma5[-1] > ma10[-1] > ma20[-1] > ma60[-1] and ma10[-1] > ma10[-2] and ma20[-1] > ma20[-2]:
                                                    weight = 8.00
    return suggest, weight


def handle_buy(context, bars):
    bar = bars.iloc[-1]
    prev_bar = bars.iloc[-2]
    first_bar = bars.iloc[-3]

    suggest, weight = check(context, bars, bar, prev_bar, first_bar)
    if suggest == 'None':
        bar = bars.iloc[-1]
        temp1 = bars.iloc[-3]
        temp2 = bars.iloc[-2]
        first_bar = bars.iloc[-4]
        prev_bar = {}
        prev_bar['open'] = temp1['open']
        prev_bar['close'] = temp2['close']
        prev_bar['high'] = max(temp1['high'], temp2['high'])
        prev_bar['low'] = min(temp1['low'], temp2['low'])
        prev_bar['vol'] = (temp1['vol'] + temp2['vol']) / 2
        prev_bar['pct_chg'] = (prev_bar['close'] - first_bar['close'])/ first_bar['close']
        suggest, weight = check(context, bars, bar, prev_bar, first_bar)

    if suggest == 'Buy':
        print('*' * 50)
        buy(context, context.symbol, bar['close'], weight=weight, remark='提前识别反弹标的，需在早盘（9:45后）走稳后再择机入场')
        print('Buy {} on {}'.format(context.share['name'], context.now.strftime('%Y-%m-%d')))


def handle_sell(context, bars, position):
    bar = bars.iloc[-1]
    buy_price = position.iloc[-1]['open']
    price = bar['close']

    suggest = 'None'
    if price < buy_price * (1 - context.loss_percent):
        suggest = 'Sell'
    if price > buy_price * (1 + context.win_percent):
        suggest = 'Sell'

    if suggest == 'Sell':
        sell(context, context.symbol, price)
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
        type = RUN_TYPE_ANALYSIS,
        #symbol='000728',
        start_date='20210101'
    )