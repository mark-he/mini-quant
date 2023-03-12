import time
from database import db_template as db
import event.scheduler as es
import webclient


def start():
    print('initializing DB connections')
    db.init()
    print('starting scheduler')
    es.start()

def stop():
    es.stop()


if __name__ == '__main__':
    start()