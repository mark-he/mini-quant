import database.trade as trade
import back_test.engine as back_test_engine
import database.trade_test as trade_test
from concurrent.futures import ThreadPoolExecutor
import utils.date_utils as date_utils


class Callback(object):
    def __init__(self, order_id):
        self.order_id = order_id

    def on_finished(self, tactic, share, account):
        trade.update_order_analysis_flag(self.order_id)


MAX_WORKERS = 10
ANALYSIS_PERIOD = 180
_thread_pool_keep = ThreadPoolExecutor(max_workers=MAX_WORKERS)

def start():
    df = trade.get_orders_pending_analysis()
    for index, order in df.iterrows():
        target_date = order['target_date']
        if target_date:
            end = date_utils.str2date(target_date)
            start = date_utils.next_days(end, -1 * 180)
            _thread_pool_keep.submit(_run(order['id'], order['tactic'], start, end, order['symbol']))


def _run(order_id, tactic, start, end, symbol):
    account = trade_test.create_account('ORDER-TEST', 1000 * 1000, order_id)
    id = account['id']
    back_test_engine.start(tactic, date_utils.date2str(start), date_utils.date2str(end), symbol=symbol, callback=Callback(order_id), account=id)


