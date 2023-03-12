# coding=utf-8
import tushare as ts
from database import db_template as db
import pandas as pd
import datetime
from concurrent.futures import ThreadPoolExecutor
import traceback
import database.share as share_db
import utils.date_utils as date_utils
import time

HISTORY_START = '20150101'
MAX_WORKERS = 1

_pro = ts.pro_api('c0dc23fe02ad4020d6bb140e3501670b3a8a9508e0f150ff6c56b387')
_thread_pool = ThreadPoolExecutor(max_workers=MAX_WORKERS)

def update_share_list_into_db():
    df = update_share_list()
    df.to_sql('share', db.engine(), index=False, if_exists='replace')


def update_index_list_into_db():
    df = pd.DataFrame(
        [{'ts_code': '000001.SH', 'name': '上证指数', 'symbol': '000001'},
         {'ts_code': '399001.SZ', 'name': '深圳成指', 'symbol': '399001'},
         ]
    )
    df.to_sql('share_index', db.engine(), index=False, if_exists='replace')


def update_history_into_db():
    sql = "SELECT a.*, c.trade_date FROM share a LEFT JOIN (SELECT b.ts_code, MAX(b.trade_date) as trade_date FROM history b GROUP BY b.ts_code) c ON c.ts_code = a.ts_code WHERE a.list_status = %(p1)s ORDER BY a.symbol"
    df_share = pd.read_sql(
        sql,
        db.engine(), params={'p1': 'L'})
    update_time = datetime.datetime.now() #获取需要更新的日期
    if update_time.hour < 15:
        update_time = update_time + datetime.timedelta(days=-1)
    update_time = share_db.next_business_day(update_time, include_today=True, offset=-1)

    update_trade_date = update_time.strftime('%Y%m%d')
    df_update = df_share[(df_share['trade_date'] < update_trade_date) | (df_share['trade_date'].isnull())]
    i = 0
    for index, row in df_update.iterrows():
        i += 1
        if i % 3 == 1:
            time.sleep(1)
        _thread_pool.submit(_update_share_history_run, row)


def update_share_basic_into_db():
    sql = "SELECT a.*, c.trade_date FROM share a LEFT JOIN (SELECT b.ts_code, MAX(b.trade_date) as trade_date FROM share_basic b GROUP BY b.ts_code) c ON c.ts_code = a.ts_code WHERE a.list_status = %(p1)s ORDER BY a.symbol"
    df_share = pd.read_sql(
        sql,
        db.engine(), params={'p1': 'L'})
    update_time = datetime.datetime.now() #获取需要更新的日期
    if update_time.hour < 15:
        update_time = update_time + datetime.timedelta(days=-1)
    update_time = share_db.next_business_day(update_time, include_today=True, offset=-1)

    update_trade_date = update_time.strftime('%Y%m%d')
    df_update = df_share[(df_share['trade_date'] < update_trade_date) | (df_share['trade_date'].isnull())]

    i = 0
    for index, row in df_update.iterrows():
        i += 1
        if i % 3 == 1:
            time.sleep(1)
        _thread_pool.submit(_update_share_basic_run, row)


def update_index_history_into_db():
    sql = "SELECT a.*, c.trade_date FROM share_index a LEFT JOIN (SELECT b.ts_code, MAX(b.trade_date) as trade_date FROM index_history b GROUP BY b.ts_code) c ON c.ts_code = a.ts_code ORDER BY a.symbol"
    df_share = pd.read_sql(
        sql,
        db.engine(), params={})
    update_time = datetime.datetime.now() #获取需要更新的日期
    if update_time.hour < 15:
        update_time = update_time + datetime.timedelta(days=-1)
    update_time = share_db.next_business_day(update_time, include_today=True, offset=-1)

    update_trade_date = update_time.strftime('%Y%m%d')
    df_update = df_share[(df_share['trade_date'] < update_trade_date) | (df_share['trade_date'].isnull())]

    for index, row in df_update.iterrows():
        _thread_pool.submit(_update_index_history_run, row)


def _update_share_history_run(share):
    try:
        print('Downloading {}'.format(share['ts_code']))
        start_date = share['trade_date']
        if (not start_date):
            start_date = HISTORY_START
        else:
            date = date_utils.str2date(start_date)
            date = share_db.next_business_day(date, include_today=False, offset=1)
            start_date = date_utils.date2str(date)

        df = update_history(share['ts_code'], start_date)
        if len(df) > 0:
            df2 = update_adjust_factor(share['ts_code'], start_date)
            if len(df2) > 0:
                if df2.iloc[0]['trade_date'] < df.iloc[0]['trade_date']:
                    print('ERROR: history = {}, adj_factor = {}', df.iloc[0]['trade_date'], df2.iloc[0]['trade_date'])
                    return
                df3 = pd.merge(left=df, right=df2, how='left')
                df3['symbol'] = share['symbol']
                df3.to_sql('history', db.engine(), index=False, if_exists='append')
                print('Updated {}: {} records'.format(share['ts_code'], len(df3)))
    except:
        print(traceback.format_exc())


def _update_index_history_run(share):
    try:
        print('Downloading {}'.format(share['ts_code']))
        start_date = share['trade_date']
        if (not start_date):
            start_date = HISTORY_START
        else:
            date = date_utils.str2date(start_date)
            date = share_db.next_business_day(date, include_today=False, offset=1)
            start_date = date_utils.date2str(date)

        df = update_index_history(share['ts_code'], start_date)
        df['symbol'] = share['symbol']
        if len(df) > 0:
            df.to_sql('index_history', db.engine(), index=False, if_exists='append')
    except:
        print(traceback.format_exc())


def _update_share_basic_run(share):
    try:
        print('Downloading basic {}'.format(share['ts_code']))
        start_date = share['trade_date']
        if (not start_date):
            start_date = HISTORY_START
        else:
            date = date_utils.str2date(start_date)
            date = share_db.next_business_day(date, include_today=False, offset=1)
            start_date = date_utils.date2str(date)

        df = update_share_basic(share['ts_code'], start_date)
        df['symbol'] = share['symbol']
        if len(df) > 0:
            df.to_sql('share_basic', db.engine(), index=False, if_exists='append')
    except:
        print(traceback.format_exc())


def update_share_list():
    df = _pro.stock_basic(**{
        "ts_code": "",
        "name": "",
        "exchange": "",
        "market": "",
        "is_hs": "",
        "list_status": "",
        "limit": "",
        "offset": ""
    }, fields=[
        "ts_code",
        "symbol",
        "name",
        "area",
        "industry",
        "market",
        "list_date",
        "exchange",
        "list_status"
    ])
    return df


def update_history(ts_code, start_date):
    # 拉取数据
    df = _pro.daily(**{
        "ts_code": ts_code,
        "trade_date": "",
        "start_date": start_date,
        "end_date": "",
        "offset": "",
        "limit": ""
    }, fields=[
        "ts_code",
        "trade_date",
        "open",
        "high",
        "low",
        "close",
        "pre_close",
        "change",
        "pct_chg",
        "vol",
        "amount"
    ])
    return df


def update_share_basic(ts_code, start_date):
    df = _pro.daily_basic(**{
        "ts_code": ts_code,
        "trade_date": "",
        "start_date": start_date,
        "end_date": "",
        "limit": "",
        "offset": ""
    }, fields=[
        "ts_code",
        "trade_date",
        "close",
        "turnover_rate",
        "turnover_rate_f",
        "volume_ratio",
        "pe",
        "pe_ttm",
        "pb",
        "ps",
        "ps_ttm",
        "dv_ratio",
        "dv_ttm",
        "total_share",
        "float_share",
        "free_share",
        "total_mv",
        "circ_mv"
    ])
    return df


def update_adjust_factor(ts_code, start_date):
    df = _pro.adj_factor(**{
        "ts_code": ts_code,
        "trade_date": "",
        "start_date": start_date,
        "end_date": "",
        "limit": "",
        "offset": ""
    }, fields=[
        "ts_code",
        "trade_date",
        "adj_factor"
    ])
    return df


def update_daily_basic(ts_code, start_date):
    df = _pro.daily_basic(**{
        "ts_code": ts_code,
        "trade_date": "",
        "start_date": start_date,
        "end_date": "",
        "limit": "",
        "offset": ""
    }, fields=[
        "ts_code",
        "trade_date",
        "turnover_rate",
        "turnover_rate_f",
        "volume_ratio",
        "pe",
        "pe_ttm",
        "pb",
        "ps",
        "ps_ttm",
        "dv_ratio",
        "dv_ttm",
        "total_share",
        "float_share",
        "free_share",
        "total_mv",
        "circ_mv",
        "limit_status"
    ])
    print(df)


def update_index_history(ts_code, start_date):
    df = _pro.index_daily(**{
        "ts_code": ts_code,
        "trade_date": "",
        "start_date": start_date,
        "end_date": "",
        "limit": "",
        "offset": ""
    }, fields=[
        "ts_code",
        "trade_date",
        "close",
        "open",
        "high",
        "low",
        "pre_close",
        "change",
        "pct_chg",
        "vol",
        "amount"
    ])
    return df

