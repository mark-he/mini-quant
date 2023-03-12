# coding=utf-8
from database import db_template as db
from database import model as model
from sqlalchemy import or_, and_
import pandas as pd
import datetime
import database.share as share
import utils.date_utils as date_utils

PTRADE_PATH='C:/FileImport/orders.csv'

def find_orders(target_date):
    sql = "SELECT * FROM trade_order WHERE state = %(p3)s AND target_date = %(p2)s"
    params = {
        'p2': target_date,
        'p3': model.ORDER_STATE_PASS
    }
    df = pd.read_sql(
        sql, db.engine(), params=params)
    return df


def generate(test=False):
    now = datetime.datetime.now()
    if not test and share.is_weekend_or_holiday(now):
        print('今天不是交易日，不进行上传')
        return
    target_date = date_utils.date2str(now)
    df = find_orders(target_date)
    if len(df) == 0:
        print('今天没有订单，不进行上传')
        return

    df.to_csv(PTRADE_PATH)

    now = db.current_time()
    session = db.session()
    data = {'state': model.ORDER_STATE_SENT}
    session.query(model.TradeOrder)\
        .filter(and_(
                     model.TradeOrder.state == model.ORDER_STATE_PASS,
                     model.TradeOrder.target_date == target_date),
                     model.TradeOrder.created_time <= now)\
        .update(data)
    session.commit()
    return df

def check():
    df = pd.read_csv(PTRADE_PATH)
    print(df)