# -*- coding: utf-8 -*-

### built-in ###
from datetime import datetime

### django ###
from django.core.management.base import BaseCommand #, CommandError

### own ###
from apps.applications import models 


class Command(BaseCommand):
    help = 'Run syncs that are necessary according to the needs_run* parameter.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--force',
            action='store_true',
            help='Force delete ignoring settings.LOG_AUTOCLEAN'
        )
        parser.add_argument(
            '-m',
            '--messages',
            action='store_true',
            help='Get info and warning messages (with result).'
        )

    def handle(self, *args, **kwargs):
        
        # if force ignore last error
        force = kwargs.get('force')
        messages = kwargs.get('messages')
        
        # inform start runs
        if messages:
            self.stdout.write('{} - INFO - Starting logs cleaning...'.format(
                datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            )

        try:
            # execute and evaluate result
            result = models.SyncHistory.delete_olds(force=force)

            #if everything was correctly ended
            if messages and result[0]:
                self.stdout.write(self.style.SUCCESS(str(result)))

            if messages:
                self.stdout.write(
                self.style.SUCCESS('{} - INFO - Cleaning ended.'.format(
                    datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
                )

        except Exception as error:
            self.stdout.write(
                self.style.ERROR('{} - ERROR - {}'.format(
                    datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    str(error)
                    )
                )
            )
