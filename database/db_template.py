# coding=utf-8
import datetime

from sqlalchemy import create_engine
import database.config as config
import database.model as model
import sqlalchemy.orm as orm
import database.snowflake as snowflake
import uuid

def init(size=50):
    global _engine
    _engine = create_engine(
        'mysql+pymysql://%(user)s:%(password)s@%(host)s:%(port)d/%(database)s?charset=utf8' % config.DB_CONFIG,
            encoding='utf-8',
            echo=False,
            pool_size=size,
            pool_pre_ping=True,
            pool_recycle=60 * 30
    )
    model.create_if_not_exists(_engine)


def engine():
    return _engine


def session():
    Session = orm.sessionmaker(bind=_engine)
    return Session()


def auto_id():
    return str(snowflake.generate_id())


def auto_uuid():
    uid = str(uuid.uuid4())
    return ''.join(uid.split('-'))


def current_time():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def current_date():
    return datetime.datetime.now().strftime('%Y%m%d')
