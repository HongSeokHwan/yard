from django.conf import settings
import tornado.ioloop
import tornado.web

from yard.utils.log import LoggableMixin
from yard.utils.meta import SingletonMixin


_loop = tornado.ioloop.IOLoop.instance()


class BridgeServer(LoggableMixin, SingletonMixin):
    def start(self):
        application = tornado.web.Application([
        ])
        application.listen(settings.BRIDGE_SERVER_PORT)

        self.info('Start serving')

        _loop.start()
