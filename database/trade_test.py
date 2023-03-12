import pandas as pd

from sqlalchemy import or_, and_
from database import db_template as db
from database import model as model

def create_account(name, amount, ref_no=None):
    df = pd.DataFrame({'id': db.auto_id(), 'name': name, 'amount': amount, 'created_time': db.current_time(), 'ref_no': ref_no}, index=[0])
    df.to_sql('test_account', db.engine(), index=False, if_exists='append', index_label='id')
    return df.iloc[-1]


def open_order(order, current_time):
    order['id'] = db.auto_id()
    order['state'] = model.ORDER_STATE_SENT
    order['created_time'] = current_time
    df = pd.DataFrame(order, index=[0])
    df.to_sql('test_order', db.engine(), index=False, if_exists='append', index_label='id')

    if order['side'] == model.SIDE_BUY:
        open_position(order['account_id'], order['symbol'], 1, order['price'], current_time)
    else:
        close_position(order['account_id'], order['symbol'], order['price'], current_time)
    return df.iloc[-1]


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
    df.to_sql('test_position', db.engine(), index=False, if_exists='append', index_label='id')
    return df.iloc[-1]


def close_position(account_id, symbol, price, current_time):
    session = db.session()
    data = {'state': model.POSITION_STATE_CLOSE, 'close': price, 'closed_time': current_time}
    session.query(model.TestPosition)\
        .filter(and_(model.TestPosition.symbol == symbol,
                     model.TestPosition.state == model.POSITION_STATE_OPEN,
                     model.TestPosition.account_id == account_id))\
        .update(data)
    session.commit()


def get_position(account_id, symbol):
    sql = "SELECT * FROM test_position WHERE account_id = %(p1)s AND symbol = %(p2)s AND state = %(p3)s"
    params = {
        'p1': account_id,
        'p2': symbol,
        'p3': model.POSITION_STATE_OPEN
    }
    df = pd.read_sql(
        sql, db.engine(), params=params)

    return df


def get_order(account_id, symbol=None):
    sql = "SELECT * FROM test_order WHERE account_id = %(p1)s "
    params = {
        'p1': account_id
    }
    if symbol:
        sql += " AND symbol = %(p2)s"
        params['p2'] = symbol
    df = pd.read_sql(
        sql, db.engine(), params=params)

    return df