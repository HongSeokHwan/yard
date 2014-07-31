from django.core.management.base import BaseCommand

from yard.apps.trading.strategy import StrategyRunner


class Command(BaseCommand):
    help = 'Run strategy'

    def handle(self, *args, **options):
        StrategyRunner().start()
