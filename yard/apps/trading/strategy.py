import time
import threading
import datetime
from enum import Enum

from yard.utils.log import LoggableMixin
from yard.utils.meta import SingletonMixin

from yard.apps.exchange.bridge import subscribe


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
        if self.exchange in BITCOIN_EXCHANGES:
            self.code = BITCOIN_CODE
        else:
            self.code = data['code']

        self.currency = data['currency']
        self.bid_data = data['tick']['bids']
        self.ask_data = data['tick']['asks']

        self.bid_price1 = float(data['tick']['bids'][0][0])
        self.ask_price1 = float(data['tick']['asks'][0][0])

        self.last_updated_time = datetime.datetime.now()


class TradeQuote(LoggableMixin):
    def __init__(self):
        super(TradeQuote, self).__init__()
        self.code = None
        self.exchange = None
        self.currency = None
        self.price = None
        self.amount = None
        self.order_id = None

    def __str__(self):
        return '%s (%s) %.2f (%s)' % (
            self.exchange, self.code, self.price, self.last_updated_time)

    def parse(self, json_quote):
        data = json_quote['data']
        self.exchange = data['exchange']
        if self.exchange in BITCOIN_EXCHANGES:
            self.code = BITCOIN_CODE
        else:
            # TODO: uncomment here if code is implemented.
            #self.code = data['code']
            pass

        self.currency = data['currency']
        self.price = float(data['tick']['price'])
        try:
            self.amount = float(data['tick']['amount'])
            self.order_id = float(data['tick']['id'])
        except Exception, e:
            self.warning(str(e))
            self.warning(json_quote)
        self.last_updated_time = datetime.datetime.now()


class QuoteBoard(LoggableMixin, SingletonMixin):
    def __init__(self):
        super(QuoteBoard, self).__init__()
        self.trade_quotes = {}  # { exchange: { code: Quote } }
        self.quotes = {}  # { exchange: { code: Quote } }
        self._lock = threading.Lock()

    def notice(self, json_quote):
        quote_type = json_quote['type']
        if quote_type == 'trade':
            q = TradeQuote()
            q.parse(json_quote)
            #self.info(str(q))
            with self._lock:
                if q.exchange not in self.trade_quotes:
                    self.trade_quotes[q.exchange] = {}
                exchange_dict = self.trade_quotes[q.exchange]
                exchange_dict[q.code] = q
        elif quote_type == 'quote':
            q = Quote()
            q.parse(json_quote)
            #self.info(str(q))
            with self._lock:
                if q.exchange not in self.quotes:
                    self.quotes[q.exchange] = {}
                exchange_dict = self.quotes[q.exchange]
                exchange_dict[q.code] = q

    def get_trade_quote(self, exchange, code):
        with self._lock:
            if exchange not in self.trade_quotes:
                return None
            exchange_dict = self.trade_quotes[exchange]
            if code not in exchange_dict:
                return None
            return exchange_dict[code]

    def get_quote(self, exchange, code):
        with self.lock:
            if exchange not in self.quotes:
                return None
            exchange_dict = self.quotes[exchange]
            if code not in exchange_dict:
                return None
            return exchange_dict[code]

    def get_btc_quote(self, exchange):
        code = BITCOIN_CODE
        return self.get_quote(exchange, code)


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
    def __init__(self, from_currency, to_currency, exchange):
        super(CurrencyConverter, self).__init__()
        self.from_currency = from_currency
        self.to_currency = to_currency
        self.currency_code = from_currency + to_currency
        self.exchange = exchange
        self.reverse_currency_code = to_currency + from_currency

    def is_ready(self):
        currency_quote = QuoteBoard().get_trade_quote(
            self.exchange, self.currency_code)
        if currency_quote:
            return True

        reverse_currency_quote = QuoteBoard().get_trade_quote(
            self.exchange, self.reverse_currency_code)
        if reverse_currency_quote:
            return True
        return False

    def convert(self, price):
        currency_quote = QuoteBoard().get_trade_quote(
            self.exchange, self.currency_code)
        if currency_quote:
            return price * currency_quote.get_mid()

        reverse_currency_quote = QuoteBoard().get_trade_quote(
            self.exchange, self.reverse_currency_code)
        if reverse_currency_quote:
            return price / currency_quote.get_mid()
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
        self.usd_to_krw = CurrencyConverter(USD, KRW, CURRENCY_EXCHANGE)
        self.cny_to_krw = CurrencyConverter(CNY, KRW, CURRENCY_EXCHANGE)

    def run(self):
        btc_china_quote = QuoteBoard().get_quote(BTC_CHINA)
        bit_stamp_quote = QuoteBoard().get_quote(BIT_STAMP)
        korbit_quote = QuoteBoard().get_quote(KORBIT)

        if btc_china_quote:
            self.info(btc_china_quote)

        if bit_stamp_quote:
            self.info(bit_stamp_quote)

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
