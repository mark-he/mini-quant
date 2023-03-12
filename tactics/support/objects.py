class Context(object):
    def __init__(self):
        self.share = None
        self.symbol = None
        self.now = None
        self.target_date = None
        self.count = 0
        self.trigger = None
        self.subscribe = []
        self.subscribe_index = []
        self.data = {}
        self.data_index = {}
        self.tactic_instance = None
        self.tactic_code = None
        self.trader_instance = None
        self.account_id = None
        self.on_buy_callback = None

    def on_buy(self, symbol, target_date, price):
        if self.on_buy_callback:
            self.on_buy_callback(symbol, target_date, price)


class Config(object):
    def __init__(self, name, release=False):
        self.name = name
        self.release = release
        self.list_date = None
        self.market = ['创业板', '主板', '中小板']
        self.exchange = ['SZSE', 'SSE']