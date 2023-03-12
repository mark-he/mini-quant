
import pandas as pd
from database import db_template as db
from database import model as model
from sqlalchemy import or_, and_

def get_user(name):
    sql = "SELECT * FROM user WHERE name = %(p1)s "
    params = {'p1': name}
    df = pd.read_sql(
        sql, db.engine(), params=params)
    return df


def create_token(name):
    df = pd.DataFrame({'id': db.auto_id(), 'token': db.auto_uuid(), 'name': name, 'created_time': db.current_time(), 'state': model.TOKEN_STATE_NEW}, index=[0])
    df.to_sql('access_token', db.engine(), index=False, if_exists='append', index_label='id')
    return df.iloc[-1]


def find_token(token):
    sql = "SELECT * FROM access_token WHERE token = %(p1)s AND state = %(p2)s"
    params = {'p1': token, 'p2': model.TOKEN_STATE_NEW}
    df = pd.read_sql(
        sql, db.engine(), params=params)
    return df


def overdue_tokens(name):
    session = db.session()
    data = {'state': model.TOKEN_STATE_OVERDUE, 'overdue_time': db.current_time()}
    session.query(model.AccessToken)\
        .filter(and_(model.AccessToken.name == name,
                     model.AccessToken.state == model.TOKEN_STATE_NEW))\
        .update(data)
    session.commit()