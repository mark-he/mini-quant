from database import db_template as db

import analysis.fast_analysis as fast_analysis


def start():
    db.init()
    fast_analysis.start()


if __name__ == '__main__':
    start()