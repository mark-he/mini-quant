from database import db_template as db
from data_feed import share_feed as feed


def start():
    db.init()
    feed.update_share_list_into_db()
    feed.update_index_list_into_db()
    feed.update_history_into_db()
    feed.update_index_history_into_db()
    feed.update_share_basic_into_db()


if __name__ == '__main__':
    start()