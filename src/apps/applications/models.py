# -*- coding: utf-8 -*-

### built-in ###
import datetime as dt
import json
import importlib
import traceback

### django ###
from django.db import models
# from django.db.models import Q
from django.conf import settings
from django.utils.timezone import now
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.utils import timezone

### own ###
from utils import connectors
from utils.processors import rgetattr

### third ###
import croniter


class Credential(models.Model):

    application = models.CharField(
        max_length=20,
        choices=settings.REGISTERED_APPS,
        blank=False,
        null=False,
        default=settings.REGISTERED_APPS[0],
    )

    comment = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'{self.get_application_display()} | {self.comment}'

class CredentialParameter(models.Model):

    credential = models.ForeignKey("Credential", on_delete=models.CASCADE)
    key = models.CharField(
        max_length=20,
        choices=settings.REGISTERED_PARAMS,
        blank=False,
        null=False,
        default=settings.REGISTERED_PARAMS[0],
    )
    value = models.CharField(max_length=200, null=False, blank=False)

    def __str__(self):
        return str(self.credential)


class Sync(models.Model):

    synchronize = models.CharField(
        max_length=20,
        choices=settings.AVAILABLE_FUNCS,
        blank=False,
        null=False,
        default=settings.AVAILABLE_FUNCS[0],
    )

    origin = models.ForeignKey(
        "Credential",
        on_delete=models.CASCADE,
        related_name='origin',
        verbose_name='Source'
    )
    destiny = models.ForeignKey(
        "Credential", 
        on_delete=models.CASCADE,
        related_name='destiny',
        verbose_name='Target'
    )
    cron_expression = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        help_text=mark_safe("{} {}{}{}".format(
            "Find your expression in",
            "<a href='https://crontab.guru/examples.html' target='_blank'>",
            "Crontab Guru",
            "</a>."
        ))
    )
    active = models.BooleanField(default=True)
    status = models.CharField(
        max_length=1,
        null=True,
        blank=True,
        choices=settings.TASK_STATUS,
        default=settings.TASK_STATUS[0][0]
    )

    def __str__(self):
        return self.get_synchronize_display()

    @classmethod
    def get_needs_run(cls, **kwargs) -> list:
        """ Returns all elements that need to run """

        def filter_(obj):
            return obj.needs_run()

        # get all active and needs run syncs
        return list(filter(
            filter_,
            cls.objects.filter(active=True, status__in=('0', '2'))
        ))

    @classmethod
    def run_needs(cls, **kwargs) -> bool:
        """ Run syncs that needs to run. """

        # default
        result = True

        # get needs_run only
        for sync in cls.get_needs_run():
            result = result if sync.run() else False

        return result

    def get_last_run(self):
        """ Get last sync history of sync and return end_time property. """
        
        # get last history
        history = self.synchistory_set.last()

        # if never run
        if not history:
            return None
        # return end_time
        return history.end_time
    get_last_run.short_description = "Last Run"

    def get_previous_run(self):
        """
        Get previous sync history of sync and return end_time property.
        Ignores if end_time is null (is running)
        """

        # get last history
        history = self.synchistory_set.exclude(end_time__isnull=True).last()

        # if never run
        if not history:
            return None

        # return start_time
        return history.start_time
    get_previous_run.short_description = "Previous Run"

    def get_next_run(self):
        """ Return datetime with scheduled next time. """
        try:
            lr = self.get_last_run()
            cron = croniter.croniter(self.cron_expression, lr or now())
            return cron.get_next(dt.datetime)
        except Exception as error:
            return None
    get_next_run.short_description = "Next Run"
    
    def needs_run(self):
        """ Determines if it needs to run depending on the cron expression. """
        
        # check if is queued
        if self.status == '2':
            return True

        next_run = self.get_next_run()
        if not next_run:
            return False

        # if is time to run and not running actually
        if now() >= next_run and self.status == '0':
            return True

        return False
    needs_run.short_description = "Needs Run"
    needs_run.boolean = True

    def is_valid(self):
        """
        Determines if source and destiny have the chosen sync type available.
        """

        # available origins of sync type
        froms = settings.CONNECTORS.get(self.synchronize).get('from', {}).keys()

        # available destinies of sync type
        towards = settings.CONNECTORS.get(self.synchronize).get('to', {}).keys()
            
        if self.origin.application not in froms:
            return False

        if self.destiny.application not in towards:
            return False

        return True

    is_valid.short_description = "Is valid"
    is_valid.boolean = True

    def run(self):
        """
        Execute the synchronization obtaining the source and destination 
        methods and parameters.
        """

        self.status = '1'
        self.save()

        # history create
        logg = SyncHistory.objects.create(
            sync=self,
            ok=True
        )
        try:
            # get configs
            from_app = self.origin.application
            to_app = self.destiny.application

            # config from setting
            sync_cfg = settings.CONNECTORS.get(self.synchronize)
            
            # get data
            from_ = sync_cfg.get('from').get(from_app)
            from_class_name = from_.get('class_')
            from_method_name = from_.get('method')
            
            # send data
            to_ = sync_cfg.get('to').get(to_app)
            to_class_name = to_.get('class_')
            to_method_name = to_.get('method')

            # classes
            from_class = rgetattr(connectors, from_class_name)
            to_class = rgetattr(connectors, to_class_name)
            
            # get last run in datetime object
            last_run = dt.datetime.strptime(
                '2000-01-01 00:00:00',
                "%Y-%m-%d %H:%M:%S"
            )
            if self.get_previous_run():
                # offset calculate
                tz = timezone.get_current_timezone()
                pr = self.get_previous_run()

                last_run = pr + tz.utcoffset(dt.datetime.now())

            # create clients
            from_client = from_class(
                source=self.origin,
                last_run=last_run
            )
            to_client = to_class(
                source=self.destiny,
                last_run=last_run
            )

            # get methods
            from_method = rgetattr(from_client, from_method_name)
            to_method = rgetattr(to_client, to_method_name)

            # mapping req parameters with application values
            from_params = self.syncparameter_set.filter(use_in='origin')
            to_params = self.syncparameter_set.filter(use_in='destiny')

            # parse elements
            parsed_from_params = {}
            parsed_to_params = {}

            # process origin params
            for p in from_params:
                if p._type == 'json':
                    parsed_from_params[p.key] = json.loads(p.value)
                else:
                    parsed_from_params[p.key] = eval(p.value)

            # process destiny params
            for p in to_params:
                if p._type == 'json':
                    parsed_to_params[p.key] = json.loads(p.value)
                else:
                    parsed_to_params[p.key] = eval(p.value)

            # execute from method
            from_response = from_method(**parsed_from_params)
            # print(from_response)

            # execute custom processes
            for process in self.syncprocess_set.all():
                # recursive call
                from_response = process.execute(self, from_response)

            # execute to method passing connector response
            to_response = to_method(from_response, **parsed_to_params)

            # log update
            logg.end_time = now()
            logg.save()

            # update status
            self.status = '0'
            self.save()

            return True

        except Exception as error:
            
            # log change
            logg.end_time = now()
            logg.ok = False
            logg.message = ''.join(traceback.format_exception(
                etype=type(error),
                value=error,
                tb=error.__traceback__
            )) if settings.DEBUG and settings.LOG_TRACEBACK else str(error)
            logg.save()

            # update status
            self.status = '0'
            self.save()

            return False


class SyncParameter(models.Model):

    sync = models.ForeignKey("Sync", on_delete=models.CASCADE)

    use_in = models.CharField(
        max_length=20,
        choices=(('origin', 'Source'), ('destiny', 'Target')),
        blank=False,
        null=False,
        default='origin'
    )

    key = models.CharField(max_length=50, null=True, blank=True)
    value = models.TextField(null=True, blank=True)
    _type = models.CharField(
        "Type",
        max_length=20,
        choices=settings.PARAM_TYPES,
        blank=False,
        null=False,
        default=settings.PARAM_TYPES[0][0]
    )

    def __str__(self):
        return str(self.sync)


class SyncHistory(models.Model):

    sync = models.ForeignKey("Sync", on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(default=None, null=True, blank=True)
    ok = models.BooleanField(default=True)

    message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.sync} | {self.start_time.strftime("%d/%m/%Y %H:%M:%S")}'

    def get_origin(self):
        return self.sync.origin
    get_origin.short_description = "Source"
    get_origin.admin_order_field = "sync__origin"

    def get_destiny(self):
        return self.sync.destiny
    get_destiny.short_description = "Target"
    get_destiny.admin_order_field = "sync__destiny"

    @classmethod
    def delete_olds(cls, force: bool = False):
        """
        Delete old objects using settings.LOG_AUTOCLEAN_DAYS offset.
        """

        # explicit declare to work it
        if settings.LOG_AUTOCLEAN or force:

            # last date to delete
            datetime_to = now() - dt.timedelta(
                days=settings.LOG_AUTOCLEAN_DAYS
            )
            
            # get, delete and return result
            return cls.objects.filter(end_time__lt=datetime_to).delete()

class SyncProcess(models.Model):
    sync = models.ForeignKey("Sync", on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(default=0)
    #reduce = models.BooleanField(default=False)
    requirements = models.CharField(max_length=200, blank=True, null=True)
    name = models.CharField(max_length=100, blank=False, null=False)
    _help = models.CharField(
        verbose_name=_("Help"),
        max_length=200,
        blank=True,
        null=True,
        help_text=_('About the procedure.')
    )
    expression = models.TextField(
        null=True,
        blank=True,
        help_text='Procedure that can process the "origin_response".'
    )

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

    def set_method(self):
        
        # requirements to locals
        if self.requirements: 
            if not isinstance(self.requirements, list):
                requirements = self.requirements.replace(' ', '').split(',')
            else:
                requirements = self.requirements

            for req in requirements:
                # parse if is submodule
                req_name = req.split('.')
                import_express = '{} = importlib.import_module("{}")'.format(
                    req_name[-1],
                    req
                )
                exec(import_express)

        # method expression
        method_expression = self.expression + '\n'
        method_expression += f'self.method = {self.name}'
        exec(method_expression)
        return self.method

    def execute(self, *args, **kwargs):
        method = getattr(self, 'method', self.set_method())
        return method(*args, **kwargs)
