from django.core.management.base import BaseCommand

from yard.apps.exchange.bridge import BridgeServer


class Command(BaseCommand):
    help = 'Run bridge server'

    def handle(self, *args, **options):
        BridgeServer().start()
