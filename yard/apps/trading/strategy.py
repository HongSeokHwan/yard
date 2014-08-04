import time

from yard.utils.log import LoggableMixin
from yard.utils.meta import SingletonMixin


class Account(LoggableMixin):
    pass


class AccountManager(LoggableMixin):
    pass


class Quote(LoggableMixin):
    def __init__(self):
        super(Quote, self).__init__()


class QuoteBoard(LoggableMixin, SingletonMixin):
    def __init__(self):
        super(QuoteBoard, self).__init__()
        self.quotes = {}

    def append(self, code, quote):
        pass


class Instrument(LoggableMixin):
    def __init__(self):
        pass


class InstrumentManager(LoggableMixin):
    pass


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


class StrategyRunner(LoggableMixin, SingletonMixin):
    def start(self):
        self.info('Start running')
        StrategyManager().register_strategy('btc_arb', BtcArb())
        StrategyManager().run()
