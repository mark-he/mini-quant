import datetime
import time
import pandas as pd
import schedule as sched
import data_feed.share_feed as share_feed
import analysis.engine as analysis_engine
from concurrent.futures import ThreadPoolExecutor
import database.share as share
import database.db_template as db
import database.db_schedule as db_schedule
import utils.date_utils as date_utils
import trade.ptrade as ptrade
import analysis.fast_analysis as fast_analysis_engine
import database.share as share
import database.trade as trade

MAX_WORKERS = 10

def keep_history_updated():
    print('keep_history_updated starting ...')
    now = datetime.datetime.now()
    if not share.is_weekend_or_holiday(now) and now.hour > 8 and now.hour < 16:
        return
    print('{}: keep_history_updated...'.format(now.strftime('%Y-%m-%d %H:%M:%S')))
    #share_feed.update_share_list_into_db()
    share_feed.update_share_basic_into_db()
    share_feed.update_history_into_db()


def fast_analyse():
    print('fast_analyse starting ...')
    fast_analysis_engine.start()


def auto_analyse():
    print('auto_analyse starting ...')
    now = datetime.datetime.now()
    target_date = share.next_business_day(now, include_today=False, offset=1)

    key = date_utils.date2str(target_date)
    df = db_schedule.get_execution('auto_analyse', key)
    if len(df) > 0:
        print('auto analyse for {} was ran.'.format(key))
        return

    sql = "SELECT COUNT(*) as x FROM share a WHERE a.list_status = %(p1)s"
    df = pd.read_sql(
        sql,
        db.engine(), params={'p1': 'L'})
    total = df.iloc[-1]['x']


    sql = "SELECT COUNT(*) as x FROM share a LEFT JOIN (SELECT b.ts_code, MAX(b.trade_date) as trade_date FROM share_basic b GROUP BY b.ts_code) c ON c.ts_code = a.ts_code " \
          " WHERE a.list_status = %(p1)s AND c.trade_date >= %(p2)s;"
    df = pd.read_sql(
        sql,
        db.engine(), params={'p1': 'L', 'p2': target_date})
    basic_count = df.iloc[-1]['x']

    sql = "SELECT COUNT(*) as x FROM share a LEFT JOIN (SELECT b.ts_code, MAX(b.trade_date) as trade_date FROM history b GROUP BY b.ts_code) c ON c.ts_code = a.ts_code " \
          " WHERE a.list_status = %(p1)s AND c.trade_date >= %(p2)s;"
    df = pd.read_sql(
        sql,
        db.engine(), params={'p1': 'L', 'p2': target_date})
    history_count = df.iloc[-1]['x']

    if (basic_count > total * 0.99) and (history_count > total * 0.99):
        print('{}: auto_analyse...'.format(now.strftime('%Y-%m-%d %H:%M:%S')))
        trade.close_new_order(target_date)
        analysis_engine.start()
        db_schedule.add_execution('auto_analyse', key)
    else:
        print('{}: auto_analyse..., condition not matched: total {}, basic {}, history {}'.format(now.strftime('%Y-%m-%d %H:%M:%S'), total, basic_count, history_count))


def heartbeat(message='heartbeat...'):
    now = datetime.datetime.now()
    print('{}: {}'.format(now.strftime('%Y-%m-%d %H:%M:%S'), message))


def send_ptrade(test=False):
    print('send_ptrade starting ...')
    now = datetime.datetime.now()
    key = date_utils.date2str(now)
    df = db_schedule.get_execution('send_ptrade', key)
    if len(df) > 0:
        print('send_ptrade for {} was ran.'.format(key))
        return
    ptrade.generate(test)
    db_schedule.add_execution('send_ptrade', key)


def start():
    sched.every(1).hours.do(heartbeat)
    #sched.every().day.at("21:57").do(keep_history_updated)
    #sched.every().day.at("21:58").do(fast_analyse)
    #sched.every(10).seconds.do(send_ptrade)
    sched.every(60).minutes.do(keep_history_updated)
    #sched.every(30).minutes.do(auto_analyse)
    #sched.every(10).minutes.do(fast_analyse)
    sched.every().day.at("00:05").do(send_ptrade)

    while(True):
        sched.run_pending()
        time.sleep(1)


def stop():
    sched.clear('Cancel')