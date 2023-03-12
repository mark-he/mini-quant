class TraderBase(object):
    def __init__(self):
        pass

    def create_account(self, name, amount):
        pass


    def place_order(self, order, current_time, release=True):
        pass


    def open_position(self, account_id, symbol, volume, price, current_time):
        pass


    def close_position(self, account_id, symbol, price, current_time):
        pass


    def get_position(self, account_id, symbol):
        pass