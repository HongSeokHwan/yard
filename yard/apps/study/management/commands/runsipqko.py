from django.core.management.base import BaseCommand

from yard.apps.study.sipqko import Sipqko


class Command(BaseCommand):
    help = 'Run sipqko'

    def handle(self, *args, **options):
        Sipqko().start()
