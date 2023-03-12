import datetime
import importlib
import time
import pandas as pd
import database.db_template as db
import database.share as utils
from concurrent.futures import ThreadPoolExecutor
from tactics.support.objects import Context
import database.trade_fulltest as trader
import traceback
import utils.thread_support as ts
import utils.date_utils as date_utils
import database.share as db_share

MAX_WORKERS = 5
global _thread_pool_keep
_thread_pool_keep = {}


def start(tactic, start_date, end_date=None, symbol=None, account=None):
    run_id = str(db.auto_id())
    try:
        _thread_pool_keep[run_id] = ThreadPoolExecutor(max_workers=MAX_WORKERS)

        base = importlib.import_module('tactics.' + tactic)
        if not account:
            df_account = trader.create_account('BACKTEST', 1000 * 1000)
            account = df_account['id']
        base.on_start_run(account)

        df_share = None
        if symbol:
            df_share = utils.get_share(symbol)
        else:
            df_share = utils.get_shares(base.config.list_date, base.config.market, base.config.exchange)

        start = date_utils.str2date(start_date)
        end = datetime.datetime.now()
        if end_date:
            end = date_utils.str2date(end_date)

        while start <= end:
            temp = start + datetime.timedelta(days=1)
            _run_nextday(run_id, tactic, base, account, df_share, start)
            start = temp

        base.on_stop_run(account)
        _thread_pool_keep.pop(run_id)
    except:
        print(traceback.format_exc())
        _thread_pool_keep.pop(run_id)


def _run_nextday(run_id, tactic, base, account, df_share, date):
    pro = ts.Progress(len(df_share))
    for index, share in df_share.iterrows():
        _thread_pool_keep[run_id].submit(_run_nextday_share, tactic, base, account, share, date, pro)
    while True:
        if pro.is_completed():
            break;
        else:
            time.sleep(1)


def _run_nextday_share(tactic, base, account, share, date, pro):
    try:
        context = Context()
        context.share = share
        context.symbol = share.symbol
        context.tactic_instance = base
        context.tactic_code = tactic
        context.trader_instance = trader
        context.account_id = account
        base.init(context)

        keep = {}
        keep_index = {}

        data_start = date_utils.date2str(date)
        now_str = date_utils.date2str(date)
        df_history = utils.get_history_qfq_of(context.symbol, end_date=data_start, count=context.count)

        test_df = df_history[df_history['trade_date'] == now_str]
        if len(test_df) > 0:
            if len(df_history) > 0:
                data_start = df_history.iloc[0]['trade_date']

            for x in context.subscribe_index:
                context.data_index[x] = utils.get_index_history_of(x, data_start)
                keep_index[x] = df_history
            for x in context.subscribe:
                df_history = utils.get_history_qfq_of(x, data_start)
                keep[x] = df_history

            context.now = date
            context.target_date = date_utils.date2str(db_share.next_business_day(context.now, False, 1))
            for x in context.subscribe_index:
                df_history = keep_index[x]
                if context.count > 0:
                    context.data_index[x] = df_history[df_history['trade_date'] <= now_str].tail(context.count)
                else:
                    context.data_index[x] = df_history[df_history['trade_date'] <= now_str]

            for x in context.subscribe:
                df_history = keep[x]
                if context.count > 0:
                    context.data[x] = df_history[df_history['trade_date'] <= now_str].tail(context.count)
                else:
                    context.data[x] = df_history[df_history['trade_date'] <= now_str]
                if x == context.symbol:
                    bars = context.data[x]
            context.trigger(context, bars)
            base.finished(context, bars)

        pro.pass_one()
        del context
    except Exception as e:
        pro.fail_one()
        print('ERROR: ' + context.symbol)
        print(traceback.format_exc())


