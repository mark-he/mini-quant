import pandas as pd
import datetime
from collections import OrderedDict


def initialize(context):
    """初始化，启动程序后只调用一次

    :param context: Context对象，存放有当前的账户及持仓信息
    :return: None
    """

    log.info('before_trading_start')

    # 定义一个周期处理函数，每3秒执行一次
    # run_interval(context, interval_handle, seconds=3)
    # 资金少于limit_value则不买入
    g.limit_value = 2000
    # 持仓股票只数限制
    g.limit_stock_num = 10

    g.win_ratio = 1.05
    g.loss_ratio = 0.95

    g.security = []
    g.to_buy = []
    g.to_sell = []


def before_trading_start(context, data):
    """在每天开始交易前被调用，此处添加每天都要初始化的信息
    :param context: Context对象，存放有当前的账户及持仓信息
    :param data: 保留字段暂无数据
    :return: None
    """
    now = datetime.datetime.now()
    target_date = now.strftime('%Y%m%d')

    # 读取数据库文件
    log.info(get_research_path())
    file_path = get_research_path() + 'upload_file/orders.csv'.format(target_date)
    db_df = None
    try:
        db_df = pd.read_csv(file_path, encoding='utf-8', converters={'symbol': str, 'target_date': str})
    except:
        log.info('没有发现 {} 交易文件，跳过交易'.format(target_date))
        return

    db_df = db_df[db_df['target_date'] == target_date]
    log.info(db_df)

    g.security = []
    # 获取待交易数据
    g.to_buy = []
    for index, share in db_df.iterrows():
        symbol = share['symbol']
        if symbol.startswith('6'):
            symbol = symbol + '.SS'
        else:
            symbol = symbol + '.SZ'
        g.to_buy.append({'symbol': symbol, 'price': share['price']})
        g.security.append(symbol)

    # 获取当前持仓
    g.to_sell = []
    positions = get_position()
    position = None
    log.info(positions)
    for symbol in positions:
        position = positions[symbol]
        if position.sid not in g.security:
            g.to_sell.append({'symbol': position.sid, 'cost': position.cost_basis, 'volume': position.enable_amount})
            g.security.append(position.sid)

    # 设置待交易股票
    set_universe(g.security)

    # 盘前信息
    log.info('当前可用资金：{}'.format(context.portfolio.cash))
    log.info('盘前持股{}只：{}'.format(get_position_count(context), get_position_list(context)))
    log.info('单只股票买入金额：{}'.format(value_per_stock(context)))


def enough_cash(context, limit_value):
    """判断资金余额是否充足

    :param context: Context对象，存放有当前的账户及持仓信息
    :param limit_value: 资金限制，当前账户余额需大于等于该值，才判断为余额充足
    :return: 资金充足则返回True，否则返回False
    """

    if context.portfolio.cash < limit_value:
        log.info('余额不足')
        return False
    else:
        return True


def available_position_count(context):
    """计算当前可买的股票只数

    对已提交买入的股票代码的集合、持仓股票代码的集合求并集
    再用持股只数限制减去上面并集中元素的个数，即为当前可买的股票只数

    :param context: Context对象，存放有当前的账户及持仓信息
    :return: 当前可买的股票只数
    """

    return g.limit_stock_num - len(get_position())


def value_per_stock(context):
    """计算单只股票买入金额

    资金余额除以当前可买的股票只数
    当可买的股票只数为0时返回0.0

    :param context: Context对象，存放有当前的账户及持仓信息
    :return: 单只股票买入金额，当可买的股票只数为0时返回0.0
    """

    # 计算当前可买的股票只数
    available_count = available_position_count(context)

    # 当可买的股票只数为0时返回0.0
    if 0 == available_count:
        return 0.0

    return context.portfolio.cash / available_count


def get_position_count(context):
    """获取当前持股只数

    调用get_position_list获取当前持有股票的代码列表
    使用len获取持股只数

    :param context: 存放有当前的账户及持仓信息
    :return: 当前持有股票的只数
    """

    return len(get_position_list(context))


def get_position_list(context):
    """获取当前持股列表

    context.portfolio.positions包含持股信息，但需要通过amount!=0来获取真实持股
    因为当股票卖出成功时，当日清仓的股票信息仍会保存在context.portfolio.positions中，只是amount等于0

    :param context: 存放有当前的账户及持仓信息
    :return: 当前持有股票的代码列表
    """

    return [x for x in context.portfolio.positions if context.portfolio.positions[x].amount != 0]


def handle_sell(context, data):
    """处理卖出逻辑

    :param context: Context对象，存放有当前的账户及持仓信息
    :return: None
    """

    # 遍历待卖出股票
    for stock in g.to_sell.copy():
        # 获取实时行情快照
        snapshot = get_snapshot(stock['symbol'])

        bar = data[stock['symbol']]

        # 判断是否停盘，停盘则跳过
        if not bar:
            continue

        # 获取股票最高价、最低价、当前价
        current_price = bar['close']

        # 限价，创业板和科创板有价格笼子限制，卖出申报价格不得低于卖出基准价格的99%
        # limit_price = round(current_price * 0.99, 2)
        limit_price = round(current_price, 2)

        # 如果达到止盈或者止损条件，则挂限价卖出
        if current_price >= stock['cost'] * g.win_ratio or current_price <= stock['cost'] * g.loss_ratio:
            log.info('{}到达卖点'.format(stock))
            # 下指定市值卖单
            order_target(stock['symbol'], 0, limit_price=limit_price)
            # 在待卖出股票列表中删除该股票
            g.to_sell.remove(stock)
            log.info('{}卖单提交'.format(stock['symbol']))


def handle_buy(context, data):
    """处理买入逻辑

    :param context: Context对象，存放有当前的账户及持仓信息
    :return: None
    """

    # 判断剩余资金是否大于最小买入金额限制，单只股票买入金额太小，没有意义
    if context.portfolio.cash < g.limit_value:
        return

    # 判断如果已达最大持股只数，则不买入
    if available_position_count(context) <= 0:
        return

    # 遍历每只候选买入股票
    for stock in g.to_buy.copy():

        # 判断如果已达最大持股只数，则不买入
        if available_position_count(context) <= 0:
            return

        # 获取实时行情快照
        bar = data[stock['symbol']]

        # 判断是否停盘，停盘则跳过
        if not bar:
            continue

        # 获取股票最低价和当前价
        low_price = bar['low']
        current_price = bar['close']

        # 获取计算单只股票买入金额
        target_value = value_per_stock(context)

        # 如果余额不足买1手，则跳过该股票
        if target_value < current_price * 100 * 1.0003:
            continue

        # 限价，创业板和科创板有价格笼子限制，买入申报价格不得高于买入基准价格的101%
        # limit_price = round(current_price * 1.01, 2)
        limit_price = round(current_price, 2)

        # 最低价低于买点，且limit_price不超过买点的1%，再下买单。避免有股票卖出后，余额充足后买入新股票的价格过高
        if (low_price <= stock['price']) and (limit_price / stock['price'] <= 1.01):
            # 下指定市值买单，用限价提交
            log.info('targe_value={}, limit_price={}'.format(target_value, limit_price))
            order_target_value(stock['symbol'], target_value, limit_price=limit_price)

            # 在待买入股票列表中删除该股票
            g.to_buy.remove(stock)
            log.info('{}买单提交'.format(stock['symbol']))
            return


def handle_data(context, data):
    interval_handle(context, data)


def interval_handle(context, data):
    """周期处理函数

    :param context: 存放有当前的账户及持仓信息
    :return: None
    """

    # 卖出
    handle_sell(context, data)

    # 买入
    handle_buy(context, data)


def on_order_response(context, order):
    """在委托回报返回时响应

    :param context: 存放有当前的账户及持仓信息
    :param order_list: 一个列表，当前委托单发生变化时，发生变化的委托单列表。委托单以字典形式展现，内容包括：'entrust_no'(委托单号),
                       'order_time'(委托时间), 'stock_code'(股票代码), 'amount'(委托数量), 'price'(委托价格), 'business_amount'(成交数量),
                       'status'(委托状态), 'order_id'(委托订单号), 'entrust_type'(委托类别), 'entrust_prop'(委托属性)
    :return: None
    """

    # 打印委托数据
    log.info(order)


def on_trade_response(context, trade):
    """在成交回报返回时响应

    :param context: 存放有当前的账户及持仓信息
    :param trade_list： 一个列表，当前成交单发生变化时，发生变化的成交单列表。成交单以字典形式展现，内容包括：'entrust_no'(委托单号),
                        'business_time'(成交时间), 'stock_code'(股票代码), 'entrust_bs'(成交方向), 'business_amount'(成交数量),
                        'business_price'(成交价格), 'business_balance'(成交额), 'business_id'(成交编号), 'status'(委托状态)
    :return: None
    """

    # 打印成交数据
    log.info(trade)


def after_trading_end(context, data):
    """在每天交易结束之后调用，用来处理每天收盘后的操作

    :param context: 存放有当前的账户及持仓信息
    :param data： 保留字段暂无数据
    :return: None
    """

    # 打印盘后持股数据
    log.info('盘后持股{}只：{}'.format(get_position_count(context), get_position_list(context)))