from django.core.management.base import BaseCommand

from yard.apps.study.quotelogger import QuoteLogger


class Command(BaseCommand):
    help = 'Run quotelogger'

    def handle(self, *args, **options):
        QuoteLogger().start()
