import datetime
import importlib
import time

import database.share as utils
from concurrent.futures import ThreadPoolExecutor
import os
from tactics.support.objects import Context
import database.trade as trader
import database.trade_test as trader_test
import traceback
import utils.thread_support as ts
import database.share as db_share
import utils.date_utils as date_utils


MAX_WORKERS = 15
global _thread_pool_keep
_thread_pool_keep = {}

def start(tactic=None, symbol=None, standalone=False, account=None):
    modules = []
    try:
        if tactic:
            modules.append(tactic)
        else:
            modules = get_modules()

        if not account:
            df_account = trader.create_account('ANALYSIS', 1000 * 1000)
            account = df_account['id']
        print('Account: {}'.format(account))

        for tactic in modules:
            _thread_pool_keep[tactic] = ThreadPoolExecutor(max_workers=MAX_WORKERS)
            base = importlib.import_module('tactics.' + tactic)
            base.on_start_run(account)
            if not standalone:
                if not base.config.release:
                    continue
            df_share = None
            if symbol:
                df_share = utils.get_share(symbol)
            else:
                df_share = utils.get_shares(base.config.list_date, base.config.market, base.config.exchange)

            pro = ts.Progress(len(df_share))
            for index, row in df_share.iterrows():
                _thread_pool_keep[tactic].submit(_run, tactic, base, row, account, pro)
    except:
        print(traceback.format_exc())
        for k in modules:
            if _thread_pool_keep[k]:
                _thread_pool_keep[k].shutdown()


def _check(base, tactic, account, pro):
    try:
        if pro.is_completed():
            base.on_stop_run(account)
            _thread_pool_keep.pop(tactic)
    except:
        print(traceback.format_exc())


def _run(tactic, base, share, account, pro):
    try:
        context = Context()
        context.share = share
        context.symbol = share.symbol
        context.tactic_instance = base
        if base.config.release:
            context.trader_instance=trader
        else:
            context.trader_instance = trader_test
        context.tactic_code = tactic
        context.account_id = account
        test = base.init(context)
        if test:
            bars = None
            for x in context.subscribe_index:
                context.data_index[x] = utils.get_index_history_of(x, count=context.count)

            for x in context.subscribe:
                context.data[x] = utils.get_history_qfq_of(x, count=context.count)
                if x == context.symbol:
                    bars = context.data[x]
            context.now = datetime.datetime.now()
            if context.now.hour < 8:
                context.target_date = date_utils.date2str(db_share.next_business_day(context.now, True, 1))
            else:
                context.target_date = date_utils.date2str(db_share.next_business_day(context.now, False, 1))

            context.trigger(context, bars)
        base.finished(context, bars)
        del context
        pro.pass_one()
        _check(base, tactic, account, pro)
    except:
        pro.fail_one()
        _check(base, tactic, account, pro)
        print('ERROR: ' + context.symbol)
        print(traceback.format_exc())


def get_modules(package="tactics"):
    tactics = []
    files = os.listdir(package)

    for file in files:
        if not file.startswith("__"):
            name, ext = os.path.splitext(file)
            if ext == '.py':
                tactics.append(name)
    return tactics
