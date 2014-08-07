import time
import threading
import datetime

from yard.utils.log import LoggableMixin
from yard.utils.meta import SingletonMixin

from yard.apps.exchange.bridge import subscribe


BITCOIN_CODE = 'bitcoin'


class QuoteProducer(LoggableMixin, SingletonMixin, threading.Thread):
    def __init__(self):
        super(QuoteProducer, self).__init__()
        self.quote_subscribers = []

    def run(self):
        for quote in subscribe():
            self.publish(quote)

    def publish(self, json_quote):
        for quote_subscriber in self.quote_subscribers:
            quote_subscriber.message(json_quote)


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
    BITCOIN_EXCHANGES = ['bitstamp', 'korbit', ]

    def __init__(self):
        super(Quote, self).__init__()
        self.code = None
        self.exchange = None
        self.currency = None
        self.bid_data = None
        self.ask_data = None
        self.last_updated_time = None
        self.bid_price1 = 0.0
        self.ask_price1 = 0.0

    def __str__(self):
        return '%s (%s) %.2f - %.2f (%s)' % (
            self.exchange, self.code, self.ask_price1, self.bid_price1,
            self.last_updated_time)

    def parse(self, json_quote):
        data = json_quote['data']
        self.exchange = data['exchange']
        if self.exchange in Quote.BITCOIN_EXCHANGES:
            self.code = BITCOIN_CODE
        else:
            self.code = data['code']

        self.currency = data['currency']
        self.bid_data = data['tick']['bids']
        self.ask_data = data['tick']['asks']

        self.bid_price1 = float(data['tick']['bids'][0][0])
        self.ask_price1 = float(data['tick']['asks'][0][0])

        self.last_updated_time = datetime.datetime.now()


class QuoteBoard(LoggableMixin, SingletonMixin):
    def __init__(self):
        super(QuoteBoard, self).__init__()
        self.quotes = {}  # { exchange: { code: Quote } }
        self.lock = threading.Lock()

    def message(self, json_quote):
        quote_type = json_quote['type']
        if quote_type == 'quote':
            q = Quote()
            q.parse(json_quote)

            self.info(str(q))

            with self.lock:
                if q.exchange not in self.quotes:
                    self.quotes[q.exchange] = {}
                exchange_dict = self.quotes[q.exchange]
                exchange_dict[q.code] = q
        else:
            print json_quote

            # TODO handle trade quote
            pass

    def get_quote(self, exchange, code):
        #TODO
        pass

    def get_bitcoin_quote(self, exchange):
        code = BITCOIN_CODE

        with self.lock:
            if exchange not in self.quotes:
                return None
            exchange_dict = self.quotes[exchange]

            if code not in exchange_dict:
                return None

            return exchange_dict[code]


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


class SpreadCalculator(LoggableMixin):
    def __init__(self, monitor_code, target_code, currency_code):
        super(SpreadCalculator, self).__init__()
        self.monitor_code = monitor_code
        self.target_code = target_code
        self.currency_code = currency_code
        self.cur_spread = 0.0

    def update(self):
        qb = QuoteBoard()
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
        qp = QuoteProducer()
        qp.quote_subscribers.append(QuoteBoard())
        qp.run()

        while True:
            time.sleep(1)
            print 'main thread'
            # calculate normal spread
            # check current spread
            # enter if chance


class StrategyRunner(LoggableMixin, SingletonMixin):
    def start(self):
        self.info('Start running')
        StrategyManager().register_strategy('btc_arb', BtcArb())
        StrategyManager().run()
