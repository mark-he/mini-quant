import datetime
import importlib
import pandas as pd
import os
import database.tactic as tactic
import database.db_template as db
import database.model as model
import utils.date_utils as date_utils

import database.share as share
import database.trade_test as trade_test
import utils.json_utils as json_utils

def analyse_order(id, p1=3, p2=5):
    ret = {}

    sql = "SELECT a.* FROM trade_order a WHERE a.id = %(p1)s "
    params = {"p1" : id}
    df = pd.read_sql(sql, db.engine(), params=params)
    if len(df) > 0:
        order_df = df.iloc[-1]
        tactic = order_df['tactic']
        symbol = order_df['symbol']
        order_target_date = order_df['target_date']
        history_df = share.get_history_qfq_of(symbol)
        ret['history'] = json_utils.dataframe2dict(history_df)
        sql = "SELECT a.* FROM test_account a WHERE a.ref_no = %(p1)s "
        params = {"p1": id}
        df = pd.read_sql(sql, db.engine(), params=params)
        if len(df) > 0:
            account = df.iloc[-1]
            points = []
            ret['analysis'] = True
            ret['points'] = points
            order_df = trade_test.get_order(account['id'], symbol)
            for index, row in order_df.iterrows():
                target_date = row['target_date']
                price = row['price']
                p = {}
                p['target_date'] = target_date
                p['price'] = price
                p['side'] = row['side']
                points.append(p)
                if row['side'] == model.SIDE_BUY:
                    trade_df = history_df[history_df['trade_date'] >= target_date]
                    if len(trade_df) > 0:
                        trade_df_index = len(history_df) - len(trade_df) - 1
                        trade_df = trade_df.iloc[0]
                        to_index = min(len(history_df), trade_df_index + p1)
                        p1_df = history_df[trade_df_index : to_index]
                        if to_index <= len(history_df) - 1:
                            p['p1'] = True
                        to_index = min(len(history_df), trade_df_index + p2)
                        if to_index <= len(history_df) - 1:
                            p['p2'] = True
                        p2_df = history_df[trade_df_index : to_index]

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
        return ret


def get_tactics():
    modules = tactic.get_modules()
    tactics = []
    for x in modules:
        base = importlib.import_module('tactics.' + x)
        if base.config.release:
            tactics.append({'name': base.config.name, 'code': x})
    return tactics


def get_orders(tactic=[], state=None, days=None):
    sql = "SELECT a.*, b.industry FROM trade_order a " \
          "LEFT JOIN share b ON a.symbol = b.symbol " \
          " WHERE 1 = 1  "
    params = {}
    i = 0
    if len(tactic) > 0:
        sql += " AND ("
        for x in tactic:
            if i > 0:
                sql += " OR "
            key = 't{}'.format(i)
            sql += " tactic = %(" + key + ")s "
            params[key] = x
            i += 1
        sql += ") "
    i = 0
    if len(state) > 0:
        sql += " AND ("
        for x in state:
            if i > 0:
                sql += " OR "
            key = 's{}'.format(i)
            sql += " state = %(" + key + ")s "
            params[key] = x
            i += 1
        sql += ") "
    if days:
        cutoff = date_utils.next_days(datetime.datetime.now(), -10)
        sql += " AND target_date =>= %(p4)s "
        params['p4'] = date_utils.date2str(cutoff)
    sql += " ORDER BY target_date DESC, weight DESC "

    df = pd.read_sql(
        sql, db.engine(), params=params)
    return df


def update_order_state(id, remark, state):
    session = db.session()
    data = {'state': state, 'remark': remark}
    session.query(model.TradeOrder).filter(model.TradeOrder.id == id).update(data)
    session.commit()

