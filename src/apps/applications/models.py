# -*- coding: utf-8 -*-

### built-in ###
import datetime
import json

### django ###
from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

### own ###
from utils.methods import SyncMethods

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
        return self.get_synchronize_display()

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
        return history.start_time
    get_last_run.short_description = "Last Run"

    def get_next_run(self):
        """ Return datetime with scheduled next time. """
        try:
            lr = self.get_last_run()
            cron = croniter.croniter(self.cron_expression, lr or now())
            return cron.get_next(datetime.datetime)
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
