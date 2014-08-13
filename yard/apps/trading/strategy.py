import time
import threading
import datetime
from enum import Enum

from yard.utils.log import LoggableMixin
from yard.utils.meta import SingletonMixin

from yard.apps.exchange.bridge import subscribe
from yard.settings import (
    BTCUSD_BITSTAMP_CURRENCY,
    BTCKRW_KORBIT_CURRENCY,
    BTCCNY_BTCCHINA_CURRENCY,
    #BTCUSD_1409_ICBIT_FUTURES,
    #BTCUSD_1412_ICBIT_FUTURES,
    USDKRW_WEBSERVICEX_CURRENCY,
    CNYKRW_WEBSERVICEX_CURRENCY)


class QuoteProducer(LoggableMixin, SingletonMixin, threading.Thread):
    def __init__(self):
        super(QuoteProducer, self).__init__()
        self.quote_subscribers = []

    def run(self):
        for quote in subscribe():
            self.publish(quote)

    def publish(self, json_quote):
        for quote_subscriber in self.quote_subscribers:
            quote_subscriber.notice(json_quote)


class Quote(LoggableMixin):
    def __init__(self):
        super(Quote, self).__init__()
        self.ticker = None
        self.bid_data = None
        self.ask_data = None
        self.bid_price1 = 0.0  # cache
        self.ask_price1 = 0.0  # cache
        self.last_updated_time = None

    def __str__(self):
        return '%s %.2f - %.2f (%s)' % (self.ticker,
                                        self.ask_price1,
                                        self.bid_price1,
                                        self.last_updated_time)

    def parse(self, json_quote):
        data = json_quote['data']
        self.ticker = data['tick']['ticker']
        self.bid_data = data['tick']['bids']
        self.ask_data = data['tick']['asks']

        self.bid_price1 = float(data['tick']['bids'][0][0])
        self.ask_price1 = float(data['tick']['asks'][0][0])

        self.last_updated_time = datetime.datetime.now()


class TradeQuote(LoggableMixin):
    def __init__(self):
        super(TradeQuote, self).__init__()
        self.ticker = None
        self.price = 0.0
        self.amount = 0.0
        self.order_id = None
        self.last_updated_time = None

    def __str__(self):
        try:
            return '%s %.2f(%.2f) (%s)' % (self.ticker, self.price,
                                           self.amount, self.last_updated_time)
        except:
            return '__str__ error'

    def parse(self, json_quote):
        data = json_quote['data']
        self.ticker = data['tick']['ticker']
        self.price = float(data['tick']['price'])

        try:
            self.amount = float(data['tick']['amount'])
        except:
            pass

        try:
            self.order_id = float(data['tick']['id'])
        except Exception, e:
            self.warn(str(e))
            self.warn(json_quote)

        self.last_updated_time = datetime.datetime.now()


class QuoteBoard(LoggableMixin, SingletonMixin):
    def __init__(self):
        super(QuoteBoard, self).__init__()
        self.trade_quotes = {}  # { ticker: TradeQuote } }
        self.quotes = {}  # { ticker: Quote } }
        self._lock = threading.Lock()

    def notice(self, json_quote):
        quote_type = json_quote['type']
        if quote_type == 'trade':
            q = TradeQuote()
            q.parse(json_quote)
            self.info(str(q))
            with self._lock:
                self.trade_quotes[q.ticker] = q
        elif quote_type == 'quote':
            q = Quote()
            q.parse(json_quote)
            self.info(str(q))
            with self._lock:
                self.quotes[q.ticker] = q

    def get_trade_quote(self, exchange, ticker):
        with self._lock:
            if ticker in self.trade_quotes:
                return self.trade_quotes[ticker]
        return None

    def get_quote(self, ticker):
        with self.lock:
            if ticker in self.quotes:
                return self.quotes[ticker]
        return None


class OrderSheet(LoggableMixin):
    def __init__(self):
        super(OrderSheet, self).__init__()
        self.order_id = 0  # is it possible??
        self.market = None
        self.code = None
        self.price = 0.0
        self.quantity = 0.0
        self.askbid = None


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
    def __init__(self, name, market, currency):
        super(Account, self).__init__()
        self.name = name
        self.market = market
        self.currency = currency
        self.deposit = 0.0
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


class IStrategy(LoggableMixin):
    def __init__(self):
        super(IStrategy, self).__init__()

    def run(self):
        pass


class CurrencyConverter(LoggableMixin):
    def __init__(self, ticker):
        super(CurrencyConverter, self).__init__()
        self.ticker = ticker

    def is_ready(self):
        currency_quote = QuoteBoard().get_trade_quote(self.ticker)
        if currency_quote:
            return True
        return False

    def convert(self, price):
        currency_quote = QuoteBoard().get_trade_quote(self.ticker)
        if currency_quote:
            return price * currency_quote.price
        return None


class BtcMarketMaker(IStrategy):
    State = Enum(
        'IDLE',
        'AFTER_CANCEL',
        'AFTER_ORDER',
        'MARKET_MAKING',
        'ERROR')

    def __init__(self):
        super(BtcMarketMaker, self).__init__()
        self.cur_state = BtcMarketMaker.State.IDLE
        self.usd_to_krw = CurrencyConverter(USDKRW_WEBSERVICEX_CURRENCY)
        self.cny_to_krw = CurrencyConverter(CNYKRW_WEBSERVICEX_CURRENCY)

    def run(self):
        btcchina_quote = QuoteBoard().get_quote(BTCCNY_BTCCHINA_CURRENCY)
        bitstamp_quote = QuoteBoard().get_quote(BTCUSD_BITSTAMP_CURRENCY)
        korbit_quote = QuoteBoard().get_quote(BTCKRW_KORBIT_CURRENCY)

        # for testing
        if btcchina_quote:
            self.info(btcchina_quote)

        if bitstamp_quote:
            self.info(bitstamp_quote)

        if korbit_quote:
            self.info(korbit_quote)

    def _set_state(self, new_state):
        self.cur_state = new_state


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
            for k, v in self.strategies.iteritems():
                v.run()


class StrategyRunner(LoggableMixin, SingletonMixin):
    def start(self):
        self.info('Start running')
        StrategyManager().register_strategy(
            'btc_market_making', BtcMarketMaker())
        StrategyManager().run()


# TODO implement me.
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
