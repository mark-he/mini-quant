from sqlalchemy import Column, Numeric, BigInteger, Integer, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def create_if_not_exists(engine):
    Base.metadata.create_all(engine)

class Schedule(Base):
    __tablename__ = "schedule"
    id = Column(String(32), primary_key=True)
    execution_key = Column(String(20), index=True)
    name = Column(String(20), index=True)
    created_time = Column(String(20))


class ShareIndex(Base):
    __tablename__ = "share_index"
    ts_code = Column(String(20), unique=True, index=True, primary_key=True)
    symbol = Column(String(20), unique=True, index=True)
    name = Column(String(20), unique=True, index=True)

    def __init__(self, ts_code, symbol, name):
        self.ts_code = ts_code
        self.symbol = symbol
        self.name = name


#https://www.tushare.pro/document/2?doc_id=25
class Share(Base):
    __tablename__ = "share"
    ts_code = Column(String(20), unique=True, index=True, primary_key=True)
    symbol = Column(String(20), unique=True, index=True)
    name = Column(String(20), unique=True, index=True)
    exchange = Column(String(20))
    market = Column(String(20))
    area = Column(String(20))
    list_status = Column(String(20))
    industry = Column(String(20))
    list_date = Column(String(20))

    def __init__(self, ts_code, symbol, name, exchange, market, area, list_status, industry, list_date):
        self.ts_code = ts_code
        self.symbol = symbol
        self.name = name
        self.exchange = exchange
        self.market = market
        self.area = area
        self.list_status = list_status
        self.industry = industry
        self.list_date = list_date


#https://www.tushare.pro/document/2?doc_id=32
class ShareBasic(Base):
    __tablename__ = "share_basic"
    ts_code = Column(String(20), index=True, primary_key=True)
    symbol = Column(String(20), index=True)
    trade_date = Column(String(20), index=True, primary_key=True)
    close = Column(Numeric(20, 6), server_default='0')
    turnover_rate = Column(Numeric(20, 6), server_default='0')
    turnover_rate_f = Column(Numeric(20, 6), server_default='0')
    volume_ratio = Column(Numeric(20, 6), server_default='0')
    pe = Column(Numeric(20, 6), server_default='0')
    pe_ttm = Column(Numeric(20, 6), server_default='0')
    pb = Column(Numeric(20, 6), server_default='0')
    ps = Column(Numeric(20, 6), server_default='0')
    ps_ttm = Column(Numeric(20, 6), server_default='0')
    dv_ratio = Column(Numeric(20, 6), server_default='0')
    dv_ttm = Column(Numeric(20, 6), server_default='0')
    total_share = Column(Numeric(20, 6), server_default='0')
    float_share = Column(Numeric(20, 6), server_default='0')
    free_share = Column(Numeric(20, 6), server_default='0')
    total_mv = Column(Numeric(20, 6), server_default='0')
    circ_mv = Column(Numeric(20, 6), server_default='0')
    limit_status = Column(Integer, server_default='0')
    def __init__(self, ts_code, symbol, trade_date, close, turnover_rate, turnover_rate_f, volume_ratio, pe, pe_ttm, pb,
                 ps, ps_ttm, dv_ratio, dv_ttm, total_share, float_share, free_share, total_mv, circ_mv, limit_status):
        self.ts_code = Column(String(20), index=True, primary_key=True)
        self.symbol = Column(String(20), index=True)
        self.trade_date = Column(String(20), index=True, primary_key=True)
        self.close = Column(Numeric(20, 6), server_default='0')
        self.turnover_rate = Column(Numeric(20, 6), server_default='0')
        self.turnover_rate_f = Column(Numeric(20, 6), server_default='0')
        self.volume_ratio = Column(Numeric(20, 6), server_default='0')
        self.pe = Column(Numeric(20, 6), server_default='0')
        self.pe_ttm = Column(Numeric(20, 6), server_default='0')
        self.pb = Column(Numeric(20, 6), server_default='0')
        self.ps = Column(Numeric(20, 6), server_default='0')
        self.ps_ttm = Column(Numeric(20, 6), server_default='0')
        self.dv_ratio = Column(Numeric(20, 6), server_default='0')
        self.dv_ttm = Column(Numeric(20, 6), server_default='0')
        self.total_share = Column(Numeric(20, 6), server_default='0')
        self.float_share = Column(Numeric(20, 6), server_default='0')
        self.free_share = Column(Numeric(20, 6), server_default='0')
        self.total_mv = Column(Numeric(20, 6), server_default='0')
        self.circ_mv = Column(Numeric(20, 6), server_default='0')
        self.limit_status = Column(Integer, server_default='0')

#https://www.tushare.pro/document/2?doc_id=95
class IndexHistory(Base):
    __tablename__ = "index_history"
    '''
    __table_args__ = (
        UniqueConstraint('ts_code', 'trade_date'),
    )
    id = Column(Integer, primary_key=True)
    '''
    ts_code = Column(String(20), index=True, primary_key=True)
    symbol = Column(String(20), index=True)
    trade_date = Column(String(20), index=True, primary_key=True)
    open = Column(Numeric(20, 6), server_default='0')
    high = Column(Numeric(20, 6), server_default='0')
    low = Column(Numeric(20, 6), server_default='0')
    close = Column(Numeric(20, 6), server_default='0')
    pre_close = Column(Numeric(20, 6), server_default='0')
    change = Column(Numeric(20, 6), server_default='0')
    pct_chg = Column(Numeric(20, 6), server_default='0')
    vol = Column(Numeric(20, 6), server_default='0')
    amount = Column(Numeric(20, 6), server_default='0')
    adj_factor = Column(Numeric(20, 6), server_default='1')

    def __init__(self, ts_code, trade_date, open, high, low, close, pre_close, change, pct_chg, vol, amount, adj_factor):
        self.ts_code = ts_code
        self.trade_date = trade_date
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.pre_close = pre_close
        self.change = change
        self.pct_chg = pct_chg
        self.vol = vol
        self.amount = amount
        self.adj_factor = adj_factor


#https://www.tushare.pro/document/2?doc_id=27
class History(Base):
    __tablename__ = "history"
    '''
    __table_args__ = (
        UniqueConstraint('ts_code', 'trade_date'),
    )
    id = Column(Integer, primary_key=True)
    '''
    ts_code = Column(String(20), index=True, primary_key=True)
    symbol = Column(String(20), index=True)
    trade_date = Column(String(20), index=True, primary_key=True)
    open = Column(Numeric(20, 6), server_default='0')
    high = Column(Numeric(20, 6), server_default='0')
    low = Column(Numeric(20, 6), server_default='0')
    close = Column(Numeric(20, 6), server_default='0')
    pre_close = Column(Numeric(20, 6), server_default='0')
    change = Column(Numeric(20, 6), server_default='0')
    pct_chg = Column(Numeric(20, 6), server_default='0')
    vol = Column(Numeric(20, 6), server_default='0')
    amount = Column(Numeric(20, 6), server_default='0')
    adj_factor = Column(Numeric(20, 6), server_default='1')

    def __init__(self, ts_code, trade_date, open, high, low, close, pre_close, change, pct_chg, vol, amount, adj_factor):
        self.ts_code = ts_code
        self.trade_date = trade_date
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.pre_close = pre_close
        self.change = change
        self.pct_chg = pct_chg
        self.vol = vol
        self.amount = amount
        self.adj_factor = adj_factor


ORDER_TYPE_MARKET = 'MARKET'
ORDER_TYPE_RANGE = 'SPEC'
SIDE_BUY='BUY'
SIDE_SELL='SELL'
ORDER_STATE_PASS = 'PASS'
ORDER_STATE_FAIL = 'FAIL'
ORDER_STATE_NEW = 'NEW'
ORDER_STATE_SENT = 'SENT'
ORDER_STATE_DONE = 'DONE'
ANALYSIS_FLAG_DONE = 'DONE'


class TestOrder(Base):
    __tablename__ = "test_order"
    id = Column(String(32), primary_key=True)
    account_id = Column(String(32))
    symbol = Column(String(20))
    name = Column(String(20))
    price = Column(Numeric(20, 6), server_default='0')
    side = Column(String(20))
    order_type = Column(String(20))
    price_start = Column(Numeric(20, 6), server_default='0')
    price_end = Column(Numeric(20, 6), server_default='0')
    price_win = Column(Numeric(20, 6), server_default='0')
    price_loss = Column(Numeric(20, 6), server_default='0')
    percent_win = Column(Numeric(20, 6), server_default='0')
    percent_loss = Column(Numeric(20, 6), server_default='0')
    position_percent = Column(Numeric(20, 6), server_default='0')
    created_time = Column(String(20), index=True)
    target_date = Column(String(20), index=True)
    state =  Column(String(20))
    tactic = Column(String(20))
    weight = Column(Numeric(20, 6), server_default='0')
    remark = Column(String(1000))

    def __init__(self, id, symbol, name, price, side, order_type, price_start, price_end, price_win, price_loss, percent_win,
                 percent_loss, position_percent, target_date, created_time, state, tactic, weight, remark):
        self.id = id
        self.symbol = symbol
        self.name = name
        self.price = price
        self.side = side
        self.order_type = order_type
        self.price_start = price_start
        self.price_end = price_end
        self.price_win = price_win
        self.price_loss = price_loss
        self.percent_win = percent_win
        self.percent_loss = percent_loss
        self.position_percent = position_percent
        self.created_time = created_time
        self.target_date = target_date
        self.state = state
        self.tactic = tactic
        self.weight = weight
        self.remark = remark


class TradeOrder(Base):
    __tablename__ = "trade_order"
    id = Column(String(32), primary_key=True)
    account_id = Column(String(32))
    symbol = Column(String(20))
    name = Column(String(20))
    price = Column(Numeric(20, 6), server_default='0')
    side = Column(String(20))
    order_type = Column(String(20))
    price_start = Column(Numeric(20, 6), server_default='0')
    price_end = Column(Numeric(20, 6), server_default='0')
    price_win = Column(Numeric(20, 6), server_default='0')
    price_loss = Column(Numeric(20, 6), server_default='0')
    percent_win = Column(Numeric(20, 6), server_default='0')
    percent_loss = Column(Numeric(20, 6), server_default='0')
    position_percent = Column(Numeric(20, 6), server_default='0')
    created_time = Column(String(20), index=True)
    target_date = Column(String(20), index=True)
    state =  Column(String(20))
    tactic = Column(String(20))
    weight = Column(Numeric(20, 6), server_default='0')
    remark = Column(String(1000))
    analysis_flag = Column(String(20), index=True)

    def __init__(self, id, symbol, name, price, side, order_type, price_start, price_end, price_win, price_loss, percent_win,
                 percent_loss, position_percent, target_date, created_time, state, tactic, weight, remark):
        self.id = id
        self.symbol = symbol
        self.name = name
        self.price = price
        self.side = side
        self.order_type = order_type
        self.price_start = price_start
        self.price_end = price_end
        self.price_win = price_win
        self.price_loss = price_loss
        self.percent_win = percent_win
        self.percent_loss = percent_loss
        self.position_percent = position_percent
        self.created_time = created_time
        self.target_date = target_date
        self.state = state
        self.tactic = tactic
        self.weight = weight
        self.remark = remark


ACCOUNT_TYPE_TEST='TEST'
ACCOUNT_TYPE_MOCK='MOCK'
ACCOUNT_TYPE_REAL='REAL'

class TestAccount(Base):
    __tablename__ = "test_account"
    id = Column(String(32), primary_key=True)
    name = Column(String(20))
    type = Column(String(20))
    ref_no = Column(String(20), index=True)
    amount = Column(Numeric(20, 6), server_default='0') #总资金
    float_pnl = Column(Numeric(20, 6), server_default='0') #浮动盈亏
    available = Column(Numeric(20, 6), server_default='0') #可用资金
    market_value = Column(Numeric(20, 6), server_default='0') #市值
    balance = Column(Numeric(20, 6), server_default='0') #资金余额
    created_time = Column(String(20))
    def __init__(self, id, name, type, amount, float_pnl, available, market_value, balance, created_time):
        self.id = id
        self.name = name
        self.type = type
        self.amount = amount
        self.float_pnl = float_pnl
        self.available = available
        self.market_value = market_value
        self.balance = balance
        self.created_time = created_time


class Account(Base):
    __tablename__ = "account"
    id = Column(String(32), primary_key=True)
    name = Column(String(20))
    type = Column(String(20))
    amount = Column(Numeric(20, 6), server_default='0') #总资金
    float_pnl = Column(Numeric(20, 6), server_default='0') #浮动盈亏
    available = Column(Numeric(20, 6), server_default='0') #可用资金
    market_value = Column(Numeric(20, 6), server_default='0') #市值
    balance = Column(Numeric(20, 6), server_default='0') #资金余额
    created_time = Column(String(20))
    def __init__(self, id, name, type, amount, float_pnl, available, market_value, balance, created_time):
        self.id = id
        self.name = name
        self.type = type
        self.amount = amount
        self.float_pnl = float_pnl
        self.available = available
        self.market_value = market_value
        self.balance = balance
        self.created_time = created_time


class AccountReport(Base):
    __tablename__ = "account_report"
    id = Column(String(32), primary_key=True)
    account_id = Column(String(32), index=True)
    float_pnl = Column(Numeric(20, 6), server_default='0')
    drawdown = Column(Numeric(20, 6), server_default='0')
    balance = Column(Numeric(20, 6), server_default='0')  # 资金余额
    trade_date = Column(String(20))
    count_win = Column(Integer, server_default='0')
    count_loss = Column(Integer, server_default='0')
    def __init__(self):
        pass


POSITION_STATE_OPEN = 'OPEN'
POSITION_STATE_CLOSE = 'CLOSE'


class TestPosition(Base):
    __tablename__ = "test_position"
    id = Column(String(32), primary_key=True)
    account_id = Column(String(32))
    symbol = Column(String(20))
    volume = Column(Integer, server_default='0') #浮动盈亏
    amount = Column(Numeric(20, 6), server_default='0')
    open = Column(Numeric(20, 6), server_default='0') #持仓均价
    price = Column(Numeric(20, 6), server_default='0') #当前行情价
    close = Column(Numeric(20, 6), server_default='0') #当前行情价
    float_pnl = Column(Numeric(20, 6), server_default='0') #浮动盈亏
    state = Column(String(20))
    created_time = Column(String(20))
    closed_time = Column(String(20))

    def __init__(self, id, account_id, symbol, volume, amount, open, price, close, float_pnl, state, created_time, closed_time):
        self.id = id
        self.account_id = account_id
        self.symbol = symbol
        self.volume = volume
        self.amount = amount
        self.open = open
        self.price = price
        self.close = close
        self.float_pnl = float_pnl
        self.state = state
        self.created_time = created_time
        self.closed_time = closed_time


class Position(Base):
    __tablename__ = "position"
    id = Column(String(32), primary_key=True)
    account_id = Column(String(32))
    symbol = Column(String(20))
    volume = Column(Integer, server_default='0') #浮动盈亏
    amount = Column(Numeric(20, 6), server_default='0')
    open = Column(Numeric(20, 6), server_default='0') #持仓均价
    price = Column(Numeric(20, 6), server_default='0') #当前行情价
    close = Column(Numeric(20, 6), server_default='0') #当前行情价
    float_pnl = Column(Numeric(20, 6), server_default='0') #浮动盈亏
    state = Column(String(20))
    created_time = Column(String(20))
    closed_time = Column(String(20))

    def __init__(self, id, account_id, symbol, volume, amount, open, price, close, float_pnl, state, created_time, closed_time):
        self.id = id
        self.account_id = account_id
        self.symbol = symbol
        self.volume = volume
        self.amount = amount
        self.open = open
        self.price = price
        self.close = close
        self.float_pnl = float_pnl
        self.state = state
        self.created_time = created_time
        self.closed_time = closed_time


class Calendar(Base):
    __tablename__ = "calendar"
    holiday = Column(String(20), index=True, primary_key=True)

    def __init__(self, holiday):
        self.holiday = holiday


USER_STATE_ENABLED = 'ENABLED'
USER_STATE_DISABLED = 'DISABLED'
class User(Base):
    __tablename__ = "user"
    id = Column(String(32), primary_key=True)
    name = Column(String(20), index=True, unique=True)
    password = Column(String(50))
    role = Column(String(20))
    state = Column(String(20))

    def __init__(self):
        pass


TOKEN_STATE_NEW = 'NEW'
TOKEN_STATE_OVERDUE = 'OVERDUE'

class AccessToken(Base):
    __tablename__ = "access_token"
    id = Column(String(32), primary_key=True)
    token = Column(String(32), index=True, unique=True)
    name = Column(String(20))
    created_time = Column(String(20))
    overdue_time = Column(String(20))
    state = Column(String(20))

    def __init__(self):
        pass