from yard.utils.log import LoggableMixin
from yard.utils.meta import SingletonMixin


class StrategyRunner(LoggableMixin, SingletonMixin):
    def start(self):
        self.info('Start running')

        while True:
            pass
