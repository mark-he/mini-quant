
import pandas as pd
from database import db_template as db
import utils.date_utils as date_utils

def get_shares(list_date=None, market=[], exchange=[], list_status='L'):
    sql = "SELECT a.* FROM share a WHERE 1 = 1 "
    if list_status:
        sql += ' AND a.list_status = %(p1)s '
        params = {'p1': 'L'}
    if list_date:
        sql += ' AND a.list_date >= %(p2)s '
        params['p2'] = list_date

    i = 0
    if len(market) > 0:
        sql += " AND ("
        for x in market:
            if i > 0:
                sql += " OR "
            key = 't{}'.format(i)
            sql += " market = %(" + key + ")s "
            params[key] = x
            i += 1
        sql += ") "

    i = 0
    if len(exchange) > 0:
        sql += " AND ("
        for x in exchange:
            if i > 0:
                sql += " OR "
            key = 'm{}'.format(i)
            sql += " exchange = %(" + key + ")s "
            params[key] = x
            i += 1
        sql += ") "

    sql += ' ORDER BY a.symbol '
    df_share = pd.read_sql(
        sql,
        db.engine(), params=params)
    return df_share


def get_share(symbol):
    sql = "SELECT * FROM share WHERE symbol = %(p1)s "
    params = {'p1': symbol}
    df_share = pd.read_sql(
        sql, db.engine(), params=params)
    return df_share


#start_date 与 end_date 二选一
def get_history(symbol, start_date=None, end_date=None, count=0):
    sql = "SELECT * FROM history WHERE symbol = %(p1)s "
    params = {'p1': symbol}

    if start_date:
        sql += " AND trade_date >= %(p3)s "
        params['p3'] = start_date

    if end_date:
        sql += " AND trade_date <= %(p2)s "
        params['p2'] = end_date
    sql += " ORDER BY trade_date DESC "

    if count > 0:
        sql += " limit {}".format(count)
    df_history = pd.read_sql(
        sql, db.engine(), params=params)
    return df_history


def get_index_history(symbol, start_date=None, end_date=None, count=0):
    sql = "SELECT * FROM index_history WHERE symbol = %(p1)s "
    params = {'p1': symbol}

    if start_date:
        sql += " AND trade_date >= %(p3)s "
        params['p3'] = start_date

    if end_date:
        sql += " AND trade_date <= %(p2)s "
        params['p2'] = end_date
    sql += " ORDER BY trade_date DESC "

    if count > 0:
        sql += " limit {}".format(count)
    df_history = pd.read_sql(
        sql, db.engine(), params=params)
    return df_history


def get_basic(symbol, trade_date):
    sql = "SELECT * FROM share_basic WHERE symbol = %(p1)s AND trade_date <= %(p2)s ORDER BY trade_date DESC limit 1"
    params = {'p1': symbol}
    params['p2'] = trade_date

    df_basic = pd.read_sql(
        sql, db.engine(), params=params)
    return df_basic


PRICE_COLS = ['open', 'close', 'high', 'low', 'pre_close']
FORMAT = lambda x: '%.4f' % x


def calc_adjust(data, adj):
    new_factor = data.iloc[0]['adj_factor']
    data['adj_factor'] = data['adj_factor'].fillna(method='bfill')
    for col in PRICE_COLS:
        if adj == 'hfq':
            data[col] = data[col] * data['adj_factor']
        if adj == 'qfq':
            data[col] = data[col] * data['adj_factor'] / float(new_factor)
        data[col] = data[col].map(FORMAT)
        data[col] = data[col].astype(float)


def qfq(df_history):
    calc_adjust(df_history, 'qfq')
    return df_history
    '''
    new_factor_value = -1
    adj_factor = 1

    for index, row in df_history.iterrows():
        if new_factor_value == -1:
            new_factor_value = row['adj_factor']
        adj_factor = row['adj_factor'] / new_factor_value

        bfq = row['close']
        df_history.loc[index, 'close'] = _calc_adjust_value(row['close'], adj_factor)
        df_history.loc[index, 'open'] = _calc_adjust_value(row['open'], adj_factor)
        df_history.loc[index, 'high'] = _calc_adjust_value(row['high'], adj_factor)
        df_history.loc[index, 'low'] = _calc_adjust_value(row['low'], adj_factor)
        df_history.loc[index, 'pre_close'] = _calc_adjust_value(row['pre_close'], adj_factor)
        qfq = df_history.loc[index, 'close']
        print('{},{},{},{}'.format(row['trade_date'], bfq, qfq, row['adj_factor']))
    return df_history

    '''

def older_first(df_history):
    return df_history.sort_index(ascending=False)


def resample(df, rule='w'):
    week_df = pd.DataFrame()
    week_df['date_index'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
    week_df = pd.concat([df, week_df], axis=1)
    week_df = week_df.set_index('date_index')
    #week_df = week_df.resample('W').agg({'close': 'last', 'date': 'last'})

    # ===周期转换方法：resample
    week_df = week_df.resample(rule=rule).last()
    # 'w'意思是week，意味着转变为周线；
    # last意思是取最后一个值
    # 查看week_df中2009-11-08这一行的数据
    # print df.iloc[:7]
    # print week_df
    # exit()

    # 这一周的开、高、低的价格
    week_df['open'] = week_df['open'].resample('w').first()
    week_df['high'] = week_df['high'].resample('w').max()
    week_df['low'] = week_df['low'].resample('w').min()
    week_df['vol'] = week_df['vol'].resample('w').sum()
    week_df['amount'] = week_df['amount'].resample('w').sum()
    week_df['close'] = week_df['close'].resample('w').last()
    # 计算这一周的涨跌幅
    # 不能使用：（最后一天的收盘价 - 第一天的收盘价） / 第一天的收盘价
    # 使用每天的涨跌幅连乘，没有现成的函数，使用apply方式，prod（）连乘
    week_df['pct_chg'] = week_df['pct_chg'].resample('w').apply(lambda x: (x + 1.0).prod() - 1.0)
    # 计算这一周的交易天数
    week_df['days'] = week_df['close'].resample('w').size()
    week_df.dropna(subset=['vol'], how='any', inplace=True)

    week_df = week_df[week_df['ts_code'].notnull()]
    week_df.reset_index(inplace=True)

    # ===保留这一周最后一个交易期
    # week_df的index并不是这一周最后一个交易日，而是这一周星期天的日期。
    # 如何才能保留这周最后一个交易日的日期？
    # 在将'交易日期'set_index之前，先增加df['最后交易日'] = df['交易日期']，然后在resample的时候取'最后交易日'的last就是最后一个交易日
    # 这个操作可以自己尝试完成

    # ===为什么在一开始时候需要set_index？
    # 因为进行resample操作的前提：以时间变量作为index
    # 在0.19版本的pandas开始，resample函数新增on参数，可以不事先将时间变量设置为index。
    # 具体可见：http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.resample.html
    # 如何查看自己的pandas版本？
    # print pd.__version__  # 所有package都可以通过这个方式来查看版本。或者在PyCharm中查看

    # ===rule的取值
    # rule='w'代表转化为周
    # 'm'代表月，'q'代表季度，'y'代表年份。'5min'代表5分钟，'1min'，等等

    # 非常人性化的ohlc函数
    # print df['收盘价'].resample(rule='w').ohlc()  # 直接将收盘价这个序列，转变为周线，并且计算出open、high、low、close
    return week_df


def get_history_qfq_of(symbol, start_date=None, end_date=None, count=0):
    df = get_history(symbol, start_date, end_date, count)
    return older_first(qfq(df))


def get_index_history_of(symbol, start_date=None, end_date=None, count=0):
    return older_first(get_index_history(symbol, start_date, end_date, count))


def _calc_adjust_value(value, adj_factor):
    return round(value * adj_factor, 4)



def is_weekend_or_holiday(date):
    if date_utils.is_weekend(date):
        return True
    sql = "SELECT * FROM calendar WHERE holiday = %(p1)s"
    params = {
        'p1': date_utils.date2str(date),
    }
    df = pd.read_sql(
        sql, db.engine(), params=params)
    return len(df) > 0


def next_business_day(date, include_today=True, offset=1):
    if include_today:
        if not is_weekend_or_holiday(date):
            return date
    while True:
        date = date_utils.next_days(date, offset)
        if not is_weekend_or_holiday(date):
            break
    return date
