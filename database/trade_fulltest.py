import pandas as pd
from database import db_template as db
from database import model as model
from database import share as share
from sqlalchemy import or_, and_

def create_account(name, amount):
    df = pd.DataFrame({'id': db.auto_id(), 'name': name, 'amount': amount, 'created_time': db.current_time()}, index=[0])
    df.to_sql('test_account', db.engine(), index=False, if_exists='append', index_label='id')
    return df.iloc[-1]


def place_order(order, current_time, release=True):
    order['id'] = db.auto_id()
    if release:
        order['source'] = model.SOURCE_BACKTEST
    else:
        order['source'] = model.SOURCE_TEST
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
    df.to_sql('position', db.engine(), index=False, if_exists='append', index_label='id')
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


def refresh_position(account_id, symbol, date, bars):
    sql = "SELECT * FROM test_position WHERE account_id = %(p1)s AND symbol = %(p2)s AND state = %(p3)s"
    params = {
        'p1': account_id,
        'p2': symbol,
        'p3': model.POSITION_STATE_OPEN
    }
    df = pd.read_sql(
        sql, db.engine(), params=params)

    df2 = bars[bars['trade_date'] == date]
    if len(df2) > 0:
        updated_close = df2.iloc[-1]['close']
        for index, row in df.iterrows():
            row['price'] = updated_close
            row['float_pnl'] = row['volume'] * (row['price'] - row['open'])
            _update_position(row['id'], row['price'], row['float_pnl'])


def _update_position(id, price, float_pnl):
    session = db.session()
    data = {'price': price, 'float_pnl': float_pnl}
    session.query(model.TestPosition)\
        .filter(model.Position.id == id)\
        .update(data)
    session.commit()


def process_orders(account_id):
    pass


def refresh_account(account_id):
    pass


def close_position(id, price):
    pass