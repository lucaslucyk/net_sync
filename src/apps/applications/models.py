# -*- coding: utf-8 -*-

### built-in ###
import datetime as dt
import json
import importlib

### django ###
from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.contrib.auth.models import User

### own ###
from utils.api import SyncMethods

### third ###
import croniter

class Company(models.Model):
    name = models.CharField(
        max_length=200,
        blank=False,
        null=False,
        unique=True
    )
    country = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )
    city = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )
    address = models.CharField(
        max_length=200,
        blank=True,
        null=True,
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )
    phone = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )
    users = models.ManyToManyField(User, blank=True)

    def is_authorized(self, user):
        return self in user.company_set.all()

    def __str__(self):
        return self.name
    
class Credential(models.Model):

    company = models.ForeignKey(
        "Company",
        blank=True,
        null=True,
        default=None,
        on_delete=models.CASCADE
    )

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

    @property
    def parameters(self):
        return self.credentialparameter_set.all()

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


class Sync(models.Model, SyncMethods):

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
        related_name='origin'
    )
    destiny = models.ForeignKey(
        "Credential", 
        on_delete=models.CASCADE,
        related_name='destiny'
    )
    cron_expression = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        help_text=mark_safe("{} {}{}{}".format(
            "Can find your expression in",
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
        return '{} from {} to {}'.format(
            self.get_synchronize_display(),
            self.origin,
            self.destiny
        )

    @classmethod
    def get_needs_run(cls):
        """ Returns all elements that need to run """

        # get all active syncs
        syncs = cls.objects.filter(active=True, status='0')

        # get needs_run only
        out_elements = []
        for sync in syncs:
            if sync.needs_run():
                out_elements.append(sync)

        # return elements
        return out_elements

    @classmethod
    def run_needs(cls):
        """ Run syncs that needs to run. """

        # get needs_run only
        syncs = cls.get_needs_run()
        
        _isok = True
        for sync in syncs:
            if not sync.run():
                _isok = False

        return _isok

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
        froms = settings.CONFIG_FUNCS.get(self.synchronize).get('from').keys()

        # available destinies of sync type
        towards = settings.CONFIG_FUNCS.get(self.synchronize).get('to').keys()
            
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
        # update status
        self.status = '1'
        self.save()

        # history create
        logg = SyncHistory.objects.create(
            sync=self,
            ok=True
        )

        try:
            # get configs
            origin_app = self.origin.application
            destiny_app = self.destiny.application

            # config from setting
            sync_cfg = settings.CONFIG_FUNCS.get(self.synchronize)

            # get methods
            origin_method = sync_cfg.get('from').get(origin_app).get('method')
            destiny_method = sync_cfg.get('to').get(destiny_app).get('method')

            # str to method
            get_method = getattr(self, origin_method)
            post_method = getattr(self, destiny_method)

            # mapping req parameters with application values
            app_orig_prms = self.syncparameter_set.filter(use_in='origin')
            app_dest_params = self.syncparameter_set.filter(use_in='destiny')

            # parse elements
            parse_origin_params = {}
            parse_dest_params = {}

            # process origin params
            for p in app_orig_prms:
                if p._type == 'json':
                    parse_origin_params[p.key] = json.loads(p.value)
                else:
                    parse_origin_params[p.key] = eval(p.value)

            # process destiny params
            for p in app_dest_params:
                if p._type == 'json':
                    parse_dest_params[p.key] = json.loads(p.value)
                else:
                    parse_dest_params[p.key] = eval(p.value)

            # executing methods
            origin_response = get_method(**parse_origin_params)
            
            # custom processes
            for process in self.syncprocess_set.all():
                # recursive call
                origin_response = process.execute(self, origin_response)
                #exec(process.expression)

            # send to destiny method
            destiny_response = post_method(origin_response, **parse_dest_params)

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
            logg.message = str(error)
            logg.save()

            # update status
            self.status = '0'
            self.save()

            return False


class SyncParameter(models.Model):

    sync = models.ForeignKey("Sync", on_delete=models.CASCADE)

    use_in = models.CharField(
        max_length=20,
        choices=(('origin', 'Origin'), ('destiny', 'Destiny')),
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
    get_origin.short_description = "Origin"
    get_origin.admin_order_field = "sync__origin"

    def get_destiny(self):
        return self.sync.destiny
    get_destiny.short_description = "Destiny"
    get_destiny.admin_order_field = "sync__destiny"


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
