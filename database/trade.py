import pandas as pd

from sqlalchemy import or_, and_
from database import db_template as db
from database import model as model

def update_order_analysis_flag(id):
    session = db.session()
    data = {'analysis_flag': model.ANALYSIS_FLAG_DONE}
    session.query(model.TradeOrder) \
        .filter(model.TradeOrder.id == id) \
        .update(data)
    session.commit()


def get_orders_pending_analysis():
    sql = "SELECT * FROM trade_order WHERE analysis_flag is NULL OR analysis_flag <> %(p1)s"
    params = {
        'p1': model.ANALYSIS_FLAG_DONE,
    }
    df = pd.read_sql(
        sql, db.engine(), params=params)
    return df


def create_account(name, amount):
    df = pd.DataFrame({'id': db.auto_id(), 'name': name, 'amount': amount, 'created_time': db.current_time()}, index=[0])
    df.to_sql('account', db.engine(), index=False, if_exists='append', index_label='id')
    return df.iloc[-1]


def open_order(order, current_time):
    order['id'] = db.auto_id()
    order['state'] = model.ORDER_STATE_NEW
    order['created_time'] = current_time
    df = pd.DataFrame(order, index=[0])
    df.to_sql('trade_order', db.engine(), index=False, if_exists='append', index_label='id')

    if order['side'] == model.SIDE_BUY:
        open_position(order['account_id'], order['symbol'], 1, order['price'], current_time)
    else:
        close_position(order['account_id'], order['symbol'], order['price'], current_time)
    return df.iloc[-1]


def close_new_order(target_date):
    session = db.session()
    data = {'state': model.ORDER_STATE_FAIL}
    session.query(model.TradeOrder)\
        .filter(and_(model.TradeOrder.state == model.ORDER_STATE_NEW,
                     model.TradeOrder.target_date <= target_date))\
        .update(data)
    session.commit()


def open_position(account_id, symbol, volume, price, current_time):
    df = pd.DataFrame({
        'id':  db.auto_id(),
        'account_id': account_id,
        'symbol': symbol,
        'volume': volume,
        'price' : price,
        'amount': volume * price,
        'open': price,
        'float_pnl': 0.0,
        'state': model.POSITION_STATE_OPEN,
        'created_time':  current_time
    }, index=[0])
    df.to_sql('position', db.engine(), index=False, if_exists='append', index_label='id')
    return df.iloc[-1]


def close_position(account_id, symbol, price, current_time):
    session = db.session()
    data = {'state': model.POSITION_STATE_CLOSE, 'close': price, 'closed_time': current_time}
    session.query(model.Position)\
        .filter(and_(model.Position.symbol == symbol,
                     model.Position.state == model.POSITION_STATE_OPEN,
                     model.Position.account_id == account_id))\
        .update(data)
    session.commit()


def get_position(account_id, symbol):
    sql = "SELECT * FROM position WHERE account_id = %(p1)s AND symbol = %(p2)s AND state = %(p3)s"
    params = {
        'p1': account_id,
        'p2': symbol,
        'p3': model.POSITION_STATE_OPEN
    }
    df = pd.read_sql(
        sql, db.engine(), params=params)

    return df

def get_order(account_id, symbol=None):
    sql = "SELECT * FROM trade_order WHERE account_id = %(p1)s "
    params = {
        'p1': account_id
    }
    if symbol:
        sql += " AND symbol = %(p2)s"
        params['p2'] = symbol
    df = pd.read_sql(
        sql, db.engine(), params=params)

    return df

