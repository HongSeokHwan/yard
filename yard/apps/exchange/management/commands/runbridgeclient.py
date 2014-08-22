from django.core.management.base import BaseCommand

from yard.apps.exchange.bridge import subscribe
from yard.utils.log import LoggableMixin


class Command(LoggableMixin, BaseCommand):
    help = 'Run bridge client'

    def handle(self, *args, **options):
        for tick in subscribe():
            data = tick['data']
            self.info('{exchange:<10} {type:<6} {ticker:<10}'.format(
                type=tick['type'], exchange=data['exchange'],
                ticker=data['tick']['ticker']))
            self.debug(tick)
