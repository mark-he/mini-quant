import pandas as pd
from database import db_template as db
from database import model as model

def add_execution(name, execution_key):
    df = pd.DataFrame({'id': db.auto_id(), 'name': name, 'execution_key': execution_key, 'created_time': db.current_time()}, index=[0])
    df.to_sql('schedule', db.engine(), index=False, if_exists='append', index_label='id')
    return df.iloc[-1]


def get_execution(name, execution_key):
    sql = "SELECT * FROM schedule WHERE name = %(p1)s AND execution_key = %(p2)s"
    params = {
        'p1': name,
        'p2': execution_key,
    }
    df = pd.read_sql(
        sql, db.engine(), params=params)
    return df
