import calendar
import datetime
import math
import pandas as pd
import numpy as np

DATE_FORMAT = '%Y%m%d'
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def is_weekend(date):
    calendar_day = calendar.weekday(date.year, date.month, date.day)
    return calendar_day >= 5


def date2str(date, format=DATE_FORMAT):
    return datetime.datetime.now().strftime(format)


def str2date(str, format=DATE_FORMAT):
    return datetime.datetime.now().strptime(str, format)


def next_days(date, days=1):
    return date.timedelta(days=days)


def reach_percent(prev, next, percent):
    upper_price = prev * (1 + percent)
    upper_price = round(math.floor(upper_price * 100) / 100, 2)  # 排除滑价
    return next >= upper_price


def find_topdown_fastslow(fast, slow):
    up_index, down_index =  find_cross_pins(fast, slow)
    return find_topdown(fast, up_index, down_index)


def find_cross_pins(fast, slow):
    df = pd.DataFrame({'fast': fast, 'slow': slow})
    df = shift_i(df, ['fast', 'slow'], 1, suffix='a')
    df = df.fillna({'fast': 0, 'slow': 0, 'fast_1a': 0, 'slow_1a': 0})
    return df[(df['fast'] > df['slow']) & (df['fast_1a'] < df['slow_1a'])].index.values, \
           df[(df['fast'] < df['slow']) & (df['fast_1a'] > df['slow_1a'])].index.values


def find_topdown(values, up_index, down_index):
    topdown = []
    i,j = 0, 0
    while True:
        if i > len(up_index) - 1 or j > len(down_index) - 1:
            break;
        first = up_index[i]
        second = down_index[j]
        if first < second:
            # find max value
            idx = first
            max_idx = idx
            max_value = values[max_idx]
            while idx < second:
                idx += 1
                if (values[idx] >= max_value):
                    max_idx = idx
                    max_value = values[max_idx]
            topdown.append({'top': True, 'value': max_value, 'pos': max_idx})
            i += 1
        else:
            # find min value
            idx = second
            min_idx = idx
            min_value = values[min_idx]
            while idx < first:
                idx += 1
                if (values[idx] < min_value):
                    min_idx = idx
                    min_value = values[min_idx]
            topdown.append({'top': False, 'value': min_value, 'pos': min_idx})
            j += 1
    return topdown


def shift_i(df, factor_list, i, fill_value=None, suffix='a'):
    """
    计算移动因子，用于获取前i日或者后i日的因子
    :param df: 待计算扩展因子的DataFrame
    :param factor_list: 待移动的因子列表
    :param i: 移动的步数
    :param fill_value: 用于填充NA的值，默认为0
    :param suffix: 值为a(ago)时表示移动获得历史数据，用于计算指标；值为l(later)时表示获得未来数据，用于计算收益
    :return: 包含扩展因子的DataFrame
    """
    # 选取需要shift的列构成新的DataFrame，进行shift操作
    shift_df = df[factor_list].shift(i, fill_value=fill_value)
    # 对新的DataFrame列进行重命名
    shift_df.rename(columns={x: '{}_{}{}'.format(x, i, suffix) for x in factor_list}, inplace=True)
    # 将重命名后的DataFrame合并到原始DataFrame中
    df = pd.concat([df, shift_df], axis=1)
    return df


def slope(x1, y1, x2, y2):
    return (y2 - y1) / (x2 - x1)
