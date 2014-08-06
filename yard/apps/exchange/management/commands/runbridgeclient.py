from django.core.management.base import BaseCommand

from yard.apps.exchange.bridge import subscribe
from yard.utils.log import LoggableMixin


class Command(LoggableMixin, BaseCommand):
    help = 'Run bridge client'

    def handle(self, *args, **options):
        for tick in subscribe():
            self.info(tick)
