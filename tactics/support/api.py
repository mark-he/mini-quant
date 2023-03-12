import database.share as utils
import database.model as model
from database import db_template as db
from database import share as share_db
import back_test.engine as back_test
import back_test.fulltest_engine as full_test
import analysis.engine as analysis
import os
import sys

RUN_TYPE_BACKTEST = 'BACKTEST'
RUN_TYPE_ANALYSIS = 'ANALYSIS'
RUN_TYPE_FULLTEST = 'FULLTEST'

def subscribe(context, symbol, count, trigger):
    context.count = count
    context.trigger = trigger
    context.subscribe.append(symbol)


def subscribe_index(context, symbol):
    context.subscribe_index.append(symbol)


def get_share_basic(symbol, trade_date):
    return share_db.get_basic(symbol, trade_date)


def get_index_history(symbol, start_date, end_date, count):
    return utils.get_index_history_of(symbol, start_date, end_date, count)


def get_history_qfq(symbol, start_date, end_date, count):
    return utils.get_history_qfq_of(symbol, start_date, end_date, count)


def resample(df, rule='w'):
    return share_db.resample(df, rule)


def buy(context, symbol, price, order_type=model.ORDER_TYPE_MARKET,
        price_start=0, price_end=0, price_win=0, price_loss=0, percent_win=0,
        percent_loss=0, position_percent=0,target_date=None, weight=0, remark=''):
    if not target_date:
        target_date = context.target_date

    order = {
        'account_id' : context.account_id,
        'symbol' : symbol,
        'name' : context.share['name'],
        'price' : price,
        'side' : model.SIDE_BUY,
        'order_type' : order_type,
        'price_start' : price_start,
        'price_end' : price_end,
        'price_win' : price_win,
        'price_loss' : price_loss,
        'percent_win' : percent_win,
        'percent_loss' : percent_loss,
        'position_percent' : position_percent,
        'target_date' : target_date,
        'tactic' : context.tactic_code,
        'weight': weight,
        'remark': remark
    }
    current_time = context.now.strftime('%Y-%m-%d %H:%M:%S')
    context.trader_instance.open_order(order, current_time)
    context.on_buy(symbol, price, target_date)


def sell(context, symbol, price, order_type=model.ORDER_TYPE_MARKET, target_date=None):
    if not target_date:
        target_date = context.target_date

    order = {
        'account_id' : context.account_id,
        'symbol' : symbol,
        'name' : context.share['name'],
        'price' : price,
        'side' : model.SIDE_SELL,
        'order_type' : order_type,
        'target_date' : target_date,
        'tactic' : context.tactic_code
    }
    current_time = context.now.strftime('%Y-%m-%d %H:%M:%S')
    context.trader_instance.open_order(order, current_time)


def get_position(context, symbol):
    return context.trader_instance.get_position(context.account_id, symbol)


def next_business_day(date):
    return share_db.next_business_day(date, include_today=False)


def run(type='backtest', symbol=None, start_date=None, end_date=None, account=None):
    db.init(10)
    file, ext = os.path.splitext(sys.argv[0])
    path, tactic = os.path.split(file)
    print('working on: ',tactic)
    if type == RUN_TYPE_BACKTEST:
        if not start_date:
            print('Error: start_date is required for backtest')
            return
        back_test.start(tactic, start_date, end_date, symbol, account=account)
    elif type == RUN_TYPE_FULLTEST:
        if not start_date:
            print('Error: start_date is required for fulltest')
            return
        full_test.start(tactic, start_date, end_date, symbol)
    else:
        analysis.start(tactic, symbol, standalone=True, account=account)


def analyse(history_df, symbol, target_date, price, p1=3, p2=5):
    p = {}
    p['target_date'] = target_date
    p['price'] = price

    trade_df = history_df[history_df['trade_date'] >= target_date]
    if len(trade_df) > 0:
        trade_df_index = len(history_df) - len(trade_df) - 1

        to_index = min(len(history_df), trade_df_index + p1)
        p1_df = history_df[trade_df_index: to_index]
        if to_index <= len(history_df) - 1:
            p['p1'] = True
        to_index = min(len(history_df), trade_df_index + p2)
        if to_index <= len(history_df) - 1:
            p['p2'] = True
        p2_df = history_df[trade_df_index: to_index]

        p1_high = max(p1_df['high'].values)
        p2_high = max(p2_df['high'].values)
        p1_low = max(p1_df['low'].values)
        p2_low = max(p2_df['low'].values)
        p1_close = max(p1_df['close'].values)
        p2_close = max(p2_df['close'].values)

        p['p1_high'] = p1_high
        p['p2_high'] = p2_high
        p['p1_low'] = p1_low
        p['p2_low'] = p2_low
        p['p1_close'] = p1_close
        p['p2_close'] = p2_close
    return p