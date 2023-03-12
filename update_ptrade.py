from database import db_template as db

import trade.ptrade as ptrade


def start():
    db.init()
    df = ptrade.generate()


if __name__ == '__main__':
    start()