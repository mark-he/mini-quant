import datetime
import importlib
import time
import pandas as pd
import database.db_template as db
import database.share as utils
from concurrent.futures import ThreadPoolExecutor
from tactics.support.objects import Context
import database.trade_test as trader
import traceback
import utils.thread_support as ts
import utils.date_utils as date_utils
import database.share as db_share

MAX_WORKERS = 20
_thread_pool_keep = {}

def start(tactic, start_date, end_date=None, symbol=None, account=None, callback=None):
    try:
        _thread_pool_keep[tactic] = ThreadPoolExecutor(max_workers=MAX_WORKERS)
        base = importlib.import_module('tactics.' + tactic)
        if not account:
            df_account = trader.create_account('BACKTEST', 1000 * 1000)
            account = df_account['id']
        print('Account: {}'.format(account))
        base.on_start_run(account)
        df_share = None
        if symbol:
            df_share = utils.get_share(symbol)
        else:
            df_share = utils.get_shares(base.config.list_date, base.config.market, base.config.exchange)

        pro = ts.Progress(len(df_share))
        for index, row in df_share.iterrows():
            _thread_pool_keep[tactic].submit(_run, tactic, base, row, start_date, end_date, account, pro, callback)
    except:
        print(traceback.format_exc())
        k = tactic
        if _thread_pool_keep[k]:
            _thread_pool_keep[k].shutdown()


def _check(base, tactic, account, pro):
    if pro.is_completed():
        base.on_stop_run(account)
        _thread_pool_keep.pop(tactic)


def _run(tactic, base, share, start_date, end_date, account, pro, callback):
    try:
        context = Context()
        context.share = share
        context.symbol = share.symbol
        context.tactic_instance = base
        context.tactic_code = tactic
        context.trader_instance = trader
        context.account_id = account
        test = base.init(context)
        if test:
            keep = {}
            keep_index = {}
            data_start = start_date
            df_history = utils.get_history_qfq_of(context.symbol, end_date=data_start, count=context.count)
            context.data['full'] = df_history

            if len(df_history) > 0:
                data_start = df_history.iloc[0]['trade_date']

            for x in context.subscribe_index:
                context.data_index[x] = utils.get_index_history_of(x, data_start)
                keep_index[x] = df_history
            for x in context.subscribe:
                df_history = utils.get_history_qfq_of(x, data_start)
                keep[x] = df_history

            start = date_utils.str2date(start_date)
            end = datetime.datetime.now()
            if end_date:
                end = date_utils.str2date(end_date)

            bars = None
            while start <= end:
                context.now = start
                context.target_date = date_utils.date2str(db_share.next_business_day(context.now, False, 1))
                now_str = date_utils.date2str(start)

                test_df = df_history[df_history['trade_date'] == now_str]
                if len(test_df) > 0:
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
                start = start + datetime.timedelta(days=1)
        base.finished(context, bars)
        if callback:
            callback.on_finished(tactic, share, account)
        pro.pass_one()
        _check(base, tactic, account, pro)
        del context
    except Exception as e:
        pro.fail_one()
        _check(base, tactic, account, pro)
        print('ERROR: ' + context.symbol)
        print(traceback.format_exc())


