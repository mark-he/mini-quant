import time
from tactics import target
from tactics import gun
from analysis import engine
from database import db_template as db

def start():
    db.init(20)
    engine.start('target')

def stop():
    pass

if __name__ == '__main__':
    start()