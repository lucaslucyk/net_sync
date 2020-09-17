# -*- coding: utf-8 -*-

### built-in ###
from datetime import datetime

### django ###
from django.core.management.base import BaseCommand, CommandError

### own ###
from apps.applications import models 


class Command(BaseCommand):
    help = 'Run syncs that are necessary according to the needs_run* parameter.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--force',
            action='store_true',
            help='Run syncs without asking if it is necessary to run them.'
        )
        parser.add_argument(
            '-m',
            '--messages',
            action='store_true',
            help='Get info and warning messages (with errors).'
        )

    def handle(self, *args, **kwargs):
        
        # if force ignore last error
        force = kwargs.get('force')
        messages = kwargs.get('messages')
        
        # inform start runs
        if messages:
            self.stdout.write('{} - INFO - Starting run of syncs...'.format(
                datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            )

        try:
            # execute and evaluate result
            if force:
                # all active and not pending elements
                syncs = models.Sync.objects.filter(active=True, status='0')
                result = True
                for sync in syncs:
                    if not sync.run():
                        result = False
            else:
                # needs_run only
                result = models.Sync.run_needs()

            #if everything was correctly ended
            if not result:
                self.stdout.write(
                    self.style.ERROR('{} - ERROR - {}'.format(
                        datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        'See sync_history for more information.'
                        )
                    )
                )
                return

            if messages:
                self.stdout.write(
                    self.style.SUCCESS('{} - {}'.format(
                        datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        'OK - The syncs have finished!'
                        )
                    )
                )
                return

        except Exception as error:
            self.stdout.write(
                self.style.ERROR('{} - ERROR - {}'.format(
                    datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    str(error)
                    )
                )
            )
