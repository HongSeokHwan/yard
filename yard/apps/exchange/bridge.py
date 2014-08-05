from collections import defaultdict
from functools import partial

from django.conf import settings
import simplejson as json
import tornado.ioloop
import tornado.web
import tornado.websocket

from yard.utils.log import LoggableMixin
from yard.utils.meta import SingletonMixin


_loop = tornado.ioloop.IOLoop.instance()

def delay(seconds, callback):
    """Friendly shortcut for IOLoop's add_timeout method."""
    _loop.add_timeout(datetime.timedelta(seconds=seconds), callback)



class AbstractExchange(object):
    exchange_code = None
    url = None

    def __init__(self):
        pass

    def connect(self):
        pass

    def on_quote(self, callback):
        pass

    def on_trade(self, callback):
        pass

    def notify_quote(self, quote):
        pass

    def notify_trade(self, trade):
        pass

    def order(self, quantity):
        raise NotImplementedError


class WebSocketMixin(object):
    def on_message(self, message):
        raise NotImplementedError


class PollingMixin(object):
    pass


class KorbitExchange(PollingMixin, AbstractExchange):
    exchange_code = 'korbit'


class BitstampExchange(WebsocketMixin, AbstractExchange):
    exchange_code = 'korbit'


exchange = KorbitExchange()
exchange.on_quote()
exchange.on_trade()


class ExchangeManager(LoggableMixin, SingletonMixin):
    exchange_classes = (
        KorbitExchange,
    )

    def __init__(self):
        super(ExchangeManager, self).__init__()
        self._subscribers = defaultdict(set)

    def get(self, exchange_code):
        pass

    def subscribe(self, session, exchange=None):
        pass

    def unsubscribe(self, session):
        for _, subscribers in self._subscribers.iteritems():
            if session in subscribers:
                subscribers.remove(session)

    def _create_exchange(self, exchange):
        exchange = KorbitExchange()
        exchange.on_quote(partial(self._on_quote, exchange))
        exchange.on_trade(partial(self._on_trade, exchange))

    def _on_quote(self, exchange, quote):
        for subscriber in self._subscribers[exchange]:
            subscriber.notify_quote(exchange, quote)

    def _on_trade(self, exchange, trade):
        for subscriber in self._subscribers[exchange]:
            subscriber.notify_trade(exchange, trade)


class Session(LoggableMixin, tornado.websocket.WebSocketHandler):
    """Represents a (web)socket session of subscriber."""

    def open(self):
        self.debug('Opened')

    def on_close(self):
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
        pass

    # Notifiers
    # ---------

    def notify_quote(self, exchange, quote):
        self.send('quote', quote)

    def notify_trade(self, exchange, trade):
        self.send('trade', quote)


class BridgeServer(LoggableMixin, SingletonMixin):
    def start(self):
        application = tornado.web.Application([
            (r'/bridge', Session),
        ])
        application.listen(settings.BRIDGE_SERVER_PORT)

        self.info('Start serving')

        _loop.start()
