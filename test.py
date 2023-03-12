import time
from database import db_template as db
import event.scheduler as es
import webclient


def start():
    db.init()
    # 定时器
    es.send_ptrade()

def stop():
    pass


if __name__ == '__main__':
    start()
    while(True):
        try:
            time.sleep(1)
        except:
            stop()