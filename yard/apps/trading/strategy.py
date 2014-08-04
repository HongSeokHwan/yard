import time

from yard.utils.log import LoggableMixin
from yard.utils.meta import SingletonMixin


class OrderSheet(LoggableMixin):
    def __init__(self):
        super(OrderSheet, self).__init__()
        self.order_id = 0  # is it possible??


class Order(LoggableMixin):
    def __init__(self):
        super(Order, self).__init__()


class ApplyOrder(LoggableMixin):
    def __init__(self):
        super(ApplyOrder, self).__init__()


class OrderBoard(LoggableMixin):
    def __init__(self):
        super(OrderBoard, self).__init__()
        self.apply_orders = {}
        self.live_orders = {}
        self.done_orders = {}


class OrderManager(LoggableMixin, SingletonMixin):
    def __init__(self):
        super(OrderManager, self).__init__()


class Account(LoggableMixin):
    def __init__(self, name, market):
        super(Account, self).__init__()
        self.name = name
        self.market = market
        self.deposit_krxbase = 0.0
        self.sellable_btc_quantity = 0.0
        self.order_board = {}

    def send_new_order(self, order_sheet):
        #TODO
        pass

    def send_cancel_order(self, order_sheet):
        #TODO
        pass

    def get_total_pnl(self):
        #TODO
        pass

    def get_unrealized_pnl(self):
        #TODO
        pass


class AccountManager(LoggableMixin):
    pass


class Book(LoggableMixin):
    def __init__(self):
        super(Book, self).__init__()
        self.accounts = {}

    def append_account(self, account_name, account):
        self.accounts[account_name] = account

    def get_total_pnl(self):  # krx base
        #TODO
        pass

    def get_unrealized_pnl(self):  # krx base
        #TODO
        pass


class Quote(LoggableMixin):
    def __init__(self, code):
        super(Quote, self).__init__()
        self.code = code
        self.bid_prices = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.ask_prices = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.bid_quantities = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.ask_quantities = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.update_time = None


class QuoteBoard(LoggableMixin, SingletonMixin):
    def __init__(self):
        super(QuoteBoard, self).__init__()
        self.quotes = {}

    def append(self, quote):
        #TODO
        pass


class Instrument(LoggableMixin):
    def __init__(self, code, underlying, market, description):
        self.code = code
        self.underlying = underlying
        self.market = market
        self.description = description


class InstrumentManager(LoggableMixin, SingletonMixin):
    def __init__(self):
        super(InstrumentManager, self).__init__()


class IStrategy(LoggableMixin):
    def __init__(self):
        super(IStrategy, self).__init__()

    def run(self):
        pass


class BtcArb(IStrategy):
    def __init__(self):
        super(BtcArb, self).__init__()

    def run(self):
        pass


class QuoteLogger(IStrategy):
    def __init__(self):
        pass


class StrategyManager(LoggableMixin, SingletonMixin):
    def __init__(self):
        super(StrategyManager, self).__init__()
        self.strategies = {}

    def register_strategy(self, name, strategy):
        self.strategies[name] = strategy

    def run(self):
        while True:
            time.sleep(0.1)
            # calculate normal spread
            # check current spread
            # enter if chance


class StrategyRunner(LoggableMixin, SingletonMixin):
    def start(self):
        self.info('Start running')
        StrategyManager().register_strategy('btc_arb', BtcArb())
        StrategyManager().run()
