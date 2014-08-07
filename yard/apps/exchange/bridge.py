from collections import defaultdict
from functools import partial

from django.conf import settings
from tornado import gen
from tornado.simple_httpclient import SimpleAsyncHTTPClient
import simplejson as json
import tornado.ioloop
import tornado.web
import tornado.websocket
import websocket
import xmltodict

from yard.utils.ds import is_equal, pick
from yard.utils.log import LoggableMixin
from yard.utils.meta import SingletonMixin


_loop = tornado.ioloop.IOLoop.instance()


# Exchange (Abstract)
# -------------------

class AbstractExchange(LoggableMixin):
    exchange_code = None
    currency = None

    def __init__(self):
        super(AbstractExchange, self).__init__()
        self._subscribers = set()
        self._started = False

    def subscribe(self, callback):
        self._subscribers.add(callback)
        if not self._started:
            self.start()
            self._started = True

    def publish(self, type, tick):
        for subscriber in self._subscribers:
            subscriber(type, tick)

    # Overridable
    # -----------

    def start(self):
        pass

    def normalize_quote(self, tick):
        return tick

    def normalize_trade(self, tick):
        return tick

    def load_message(self, text):
        return json.loads(text)

    def dump_message(self, message):
        return json.dumps(message)


class WebsocketMixin(object):
    websocket_url = None

    def __init__(self, *args, **kwargs):
        super(WebsocketMixin, self).__init__(*args, **kwargs)
        self.connection = None

    @gen.engine
    def start(self):
        super(WebsocketMixin, self).start()

        self.connection = yield tornado.websocket.websocket_connect(
            self.websocket_url)

        self.on_connect()

        while True:
            raw = yield self.connection.read_message()
            message = self.load_message(raw)

            self.on_message(message)

    def on_connect(self):
        pass

    def on_message(self, message):
        raise NotImplementedError


class PollingMixin(object):
    quote_poll_concurrency = 1
    trade_poll_concurrency = 1
    quote_poll_url = None
    trade_poll_url = None

    def __init__(self, *args, **kwargs):
        super(PollingMixin, self).__init__(*args, **kwargs)
        self._last_quote = None
        self._last_trade = None

    def start(self):
        super(PollingMixin, self).start()

        if self.get_quote_poll_url():
            for _ in range(self.quote_poll_concurrency):
                self.poll_quote()
        if self.get_trade_poll_url():
            for _ in range(self.trade_poll_concurrency):
                self.poll_trade()

    @gen.engine
    def poll_quote(self):
        client = SimpleAsyncHTTPClient()
        while True:
            self.debug('Polling quote')
            response = yield client.fetch(self.get_quote_poll_url())
            tick = self.load_message(response.body)
            quote = self.normalize_quote(tick)
            if not quote:
                continue
            if not is_equal(self._last_quote, quote):
                first = self._last_quote is None
                self._last_quote = quote
                if not first:
                    self.publish('quote', quote)

    @gen.engine
    def poll_trade(self):
        client = SimpleAsyncHTTPClient()
        while True:
            self.debug('Polling trade')
            response = yield client.fetch(self.get_trade_poll_url())
            tick = self.load_message(response.body)
            trade = self.normalize_trade(tick)
            if not trade:
                continue
            if not is_equal(self._last_trade, trade):
                first = self._last_trade is None
                self._last_trade = trade
                if not first:
                    self.publish('trade', trade)

    def get_quote_poll_url(self):
        return self.quote_poll_url

    def get_trade_poll_url(self):
        return self.trade_poll_url


class XMLMixin(object):
    def load_message(self, text):
        return xmltodict.parse(text)


class AbstractFxExchange(XMLMixin, PollingMixin, AbstractExchange):
    exchange_code = 'usdkrw'
    currency = 'krw'
    trade_poll_concurrency = 1
    trade_poll_url_tmpl = ('http://www.webservicex.net/CurrencyConvertor.asmx/'
                           'ConversionRate?FromCurrency={from_}'
                           '&ToCurrency={to}')
    from_currency = None
    to_currency = None

    def get_trade_poll_url(self):
        return self.trade_poll_url_tmpl.format(
            from_=self.from_currency, to=self.to_currency)

    def normalize_trade(self, tick):
        if not tick:
            return None
        return {
            'price': tick['double']['#text'],
        }


# Exchange (Concrete)
# -------------------

class KorbitExchange(PollingMixin, AbstractExchange):
    exchange_code = 'korbit'
    currency = 'krw'
    quote_poll_concurrency = 2
    trade_poll_concurrency = 2
    quote_poll_url = 'https://api.korbit.co.kr/v1/orderbook'
    trade_poll_url = 'https://api.korbit.co.kr/v1/transactions'

    def normalize_quote(self, tick):
        if 'bids' not in tick or 'asks' not in tick:
            return None
        return pick(tick, 'bids', 'asks')

    def normalize_trade(self, tick):
        if not tick:
            return None
        trade = tick[0]
        return {
            'id': trade['tid'],
            'price': trade['price'],
            'quantity': trade['amount'],
        }


class BitstampExchange(WebsocketMixin, AbstractExchange):
    exchange_code = 'bitstamp'
    currency = 'usd'
    websocket_url = ('wss://ws.pusherapp.com/app/de504dc5763aeef9ff52?'
                     'protocol=7&client=js&version=2.1.6&flash=false')
    channels = ('order_book', 'live_trades')

    def on_connect(self):
        for channel in self.channels:
            self.connection.write_message(self.dump_message({
                'event': 'pusher:subscribe',
                'data': {'channel': channel},
            }))

    def on_message(self, message):
        if message.get('channel') not in self.channels:
            return

        data = json.loads(message['data'])

        if message['event'] == 'trade':
            self.publish('trade', data)

        elif message['event'] == 'data':
            self.publish('quote', data)

    def normalize_quote(self, tick):
        if 'bids' not in tick or 'asks' not in tick:
            return None
        return pick(tick, 'bids', 'asks')

    def normalize_trade(self, tick):
        if not tick:
            return None
        trade = tick[0]
        return {
            'id': trade['id'],
            'price': trade['price'],
            'quantity': trade['amount'],
        }


class UsdToKrwExchange(AbstractFxExchange):
    exchange_code = 'usdkrw'
    currency = 'krw'
    from_currency = 'USD'
    to_currency = 'KRW'


class CnyToKrwExchange(AbstractFxExchange):
    exchange_code = 'cnykrw'
    currency = 'krw'
    from_currency = 'CNY'
    to_currency = 'KRW'


class UsdToCnyExchange(AbstractFxExchange):
    exchange_code = 'usdcny'
    currency = 'cny'
    from_currency = 'USD'
    to_currency = 'CNY'


# Manager
# -------

class ExchangeManager(LoggableMixin, SingletonMixin):
    exchange_classes = dict([(class_.exchange_code, class_) for class_ in (
        KorbitExchange,
        BitstampExchange,
        UsdToKrwExchange,
        CnyToKrwExchange,
        UsdToCnyExchange,
    )])

    def __init__(self):
        super(ExchangeManager, self).__init__()
        self._subscribers = defaultdict(set)
        self._exchanges = {}

    @property
    def exchange_codes(self):
        return self.exchange_classes.keys()

    def get(self, exchange):
        return self._exchanges.get(exchange)

    def subscribe(self, session, exchange=None):
        exchanges = (self.exchange_codes if exchange is None else
                     exchange if isinstance(exchange, (list, tuple)) else
                     [exchange])
        for exchange in exchanges:
            self.info('Subscribing {0}'.format(exchange))
            self._ensure_exchange(exchange)
            self._subscribers[exchange].add(session)

    def unsubscribe(self, session):
        for exchange, subscribers in self._subscribers.iteritems():
            if session in subscribers:
                self.info('Unsubscribing {0}'.format(exchange))
                subscribers.remove(session)

    def _ensure_exchange(self, exchange):
        if exchange not in self._exchanges:
            self._exchanges[exchange] = self._create_exchange(exchange)

    def _create_exchange(self, exchange):
        instance = self.exchange_classes[exchange]()
        instance.subscribe(partial(self._on_tick, exchange))
        return instance

    def _on_tick(self, exchange, type, tick):
        self.info('Received {type} tick from {exchange}'.format(
            type=type, exchange=exchange))
        for subscriber in self._subscribers[exchange]:
            subscriber.notify_tick(exchange, type, tick)


# Handler
# -------

class Session(LoggableMixin, tornado.websocket.WebSocketHandler):
    """Represents a (web)socket session of subscriber."""

    def open(self):
        self.debug('Opened')

    def on_close(self):
        ExchangeManager().unsubscribe(self)
        self.debug('Closed')

    def on_message(self, message):
        as_json = json.loads(message)
        self.debug('Received: {0}'.format(as_json))

        method = as_json['type']
        data = as_json.get('data', {})

        getattr(self, 'handle_{method}'.format(method=method))(**data)

    # Utils
    # -----

    def send(self, type, data=None):
        self.write_message(json.dumps({'type': type, 'data': data or {}}))

    def send_error(self, error_msg=None):
        self.send('error', {'msg': error_msg or ''})

    # Handlers
    # --------

    def handle_subscribe(self, exchange=None):
        ExchangeManager().subscribe(self, exchange)

    # Notifiers
    # ---------

    def notify_tick(self, exchange, type, tick):
        self.send(type, {
            'exchange': exchange,
            'currency': ExchangeManager().get(exchange).currency,
            'tick': tick,
        })


# Server
# ------

class BridgeServer(LoggableMixin, SingletonMixin):
    def start(self):
        application = tornado.web.Application([
            (r'/bridge', Session),
        ])
        application.listen(settings.BRIDGE_SERVER_PORT)

        self.info('Start serving')

        _loop.start()


# Utils
# -----

def subscribe(exchange=None):
    url = 'ws://{host}:{port}/bridge'.format(
        host=settings.BRIDGE_SERVER_HOST, port=settings.BRIDGE_SERVER_PORT)

    ws = websocket.create_connection(url)

    ws.send(json.dumps({
        'type': 'subscribe',
        'data': {
            'exchange': exchange
        },
    }))

    while True:
        raw = ws.recv()
        yield json.loads(raw)
