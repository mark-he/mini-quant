import time
from tactics import target
from tactics import gun
from back_test import engine
from database import db_template as db

def start():
    db.init(50)
    engine.start('target', start_date='20220101')
    engine.start('target_v2', start_date='20220101')
    engine.start('gun', start_date='20220101')
    engine.start('gun_v2', start_date='20220101')

def stop():
    pass

if __name__ == '__main__':
    start()