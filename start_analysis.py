from database import db_template as db

import event.scheduler as es


def start():
    db.init()
    es.auto_analyse()


if __name__ == '__main__':
    start()