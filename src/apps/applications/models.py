# built-in
import datetime
import json

# django
from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

# own
from utils import processors as procs
from utils.api import FieldDefinition

# third
from spec_utils import visma
from spec_utils import nettime6 as nt6
from spec_utils import specmanagerdb as smdb
import croniter
import pandas as pd

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
        next_run = self.get_next_run()
        if not next_run:
            return False

        if now() >= next_run and self.status != '0':
            return True

        return False
    needs_run.short_description = "Needs Run"
    needs_run.boolean = True

    def is_valid(self):
        
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
            #parse_origin_params = {p.key: eval(p.value) for p in app_orig_prms}
            #parse_dest_params = {p.key: eval(p.value) for p in app_dest_params}
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

            #print(parse_dest_params)

            # executing methods
            origin_response = get_method(**parse_origin_params)
            #print(origin_response)

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

    def open_nt6_connection(self, source: str):
        """
        Create and return a nettime client.
        Source specify origin or destiny conn.
        """

        # connection params
        params = getattr(self, source).credentialparameter_set.all()
        host = params.filter(key='host').first().value
        username = params.filter(key='user').first().value
        pwd = params.filter(key='password').first().value

        # create and return client
        return nt6.Client(url=host, username=username, pwd=pwd)

    def open_visma_connection(self, source: str):
        """
        Create and return a visma client.
        Source specify origin or destiny conn.
        """

        # connection params
        params = getattr(self, source).credentialparameter_set.all()
        host = params.filter(key='host').first().value
        username = params.filter(key='user').first().value
        pwd = params.filter(key='password').first().value

        # create and return client
        return visma.Client(url=host, username=username, pwd=pwd)

    def open_smdb_connection(self, source: str):
        """
        Create and return a specmanagerdb client.
        Source specify origin or destiny conn.
        """

        # connection params
        params = getattr(self, source).credentialparameter_set.all()
        server = params.filter(key='server').first().value
        username = params.filter(key='user').first().value
        pwd = params.filter(key='password').first().value
        database = params.filter(key='database').first().value
        controller = params.filter(key='controller').first().value

        # create and return client
        return smdb.Client(
            username=username,
            pwd=pwd,
            server=server,
            database=database,
            controller=controller
        )

    def get_nt6_timetypes(self, client: nt6.Client):
        
        nt_incidencias = client.get_elements("Incidencia").get('items')

        incidencias = []
        for incidencia in nt_incidencias:
            incidencias.append({"id": incidencia.get("id")})

        return incidencias

    def get_nt6_readers(self, client: nt6.Client):

        nt_readers = client.get_elements("Lector").get('items')

        readers = []
        for reader in nt_readers:
            readers.append({"id": reader.get("id")})

        return readers

    def apply_fields_def(self, structure: list, fields_def: list):
        """ Processes a data structure with the fields definition. """

        # empty data by default
        out_data = []

        # for all elements in structure
        for elem in structure:
            structure = {}
            for fd in fields_def:
                # get first value
                value = elem.get(fd.in_name, None)

                # execute all steps of definition -if exist-
                for step in fd.steps:
                    # for null values
                    if not value:
                        break
                    # get step method name
                    method = getattr(procs, step.method)
                    # execute and get value
                    value = method(value, *step._args, **step._kwargs)

                # insert in structure if has value only
                if value:
                    structure.update({fd.out_name: value})

            # append complete structure
            out_data.append(structure)

        return out_data


    def get_nt6_employees(self, fields: list, filterExp: str = None) -> list:
        """ Get employees from nettime with spec_utils.nettime6 module. """

        # open api connection with auto-disconnect
        with self.open_nt6_connection(source="origin") as client:

            # add expression for ignore old syncs (this.modified >= lastSync)
            query = nt6.Query(
                fields=[f.get('origin') for f in fields],
                filterExp='{}(this.modified >= "{}")'.format(
                    f'({filterExp}) && ' if filterExp else '',
                    '2020-08-26'
                )
            )

            # get employees
            nt_response = client.get_employees(query=query)

        return self.apply_fields_def(
            structure=nt_response.get('items', []),
            fields_def=[FieldDefinition.from_json(f) for f in fields]
        )

    def get_visma_employees(self, fields: list, active: bool = None) -> list:
        """ Get employees from visma with spec_utils.visma module. """
        
        # open api connection with auto-disconnect
        with self.open_visma_connection(source="origin") as client:

            # out employees
            employees_detail = []
            
            # no detail
            response = client.get_employees(
                active=False,
                #updatedFrom="2020-08-01"
            )

            for result in response.get('values'):
                # append response to list of employees
                employees_detail.append(
                    client.get_employees(employee=f'rh-{result.get("id")}')
                )

        return self.apply_fields_def(
            structure=employees_detail,
            fields_def=[FieldDefinition.from_json(f) for f in fields]
        )

    def get_smdb_employees(self, fields: list = [], **kwargs):
        """ Get employees from SM with spec_utils.specmanagerdb module. """
        
        # get manager fields
        sm_fields = [f.get('origin') for f in fields]

        # open api connection with auto-disconnect
        with self.open_smdb_connection(source="origin") as client:
            sm_employees = client.get_employees(
                to_records=kwargs.get('to_records', True),
                fields=sm_fields or ['*'],
                top=kwargs.get('top', 5),
                where=kwargs.get('where', None),
                group_by=kwargs.get('group_by', []),
                #table=kwargs.get('table', "PERSONAS"),
            )

        # return structure
        return self.apply_fields_def(
            structure=sm_employees,
            fields_def=[FieldDefinition.from_json(f) for f in fields]
        )

    def post_smdb_employees(self, employees: list, refer: dict, **kwargs):
        """ Send employees to nettime with spec_utils.smdb module. """

        # open api connection with auto-disconnect
        with self.open_smdb_connection(source="destiny") as client:
            
            # convert if is not dataframe
            if not isinstance(employees, pd.DataFrame):
                employees = pd.DataFrame.from_records(employees)

            # update headers
            employees = employees.rename(columns=refer)

            # send data to module
            result = client.import_employees(
                employees=employees,
                source=str(self.origin)
            )

        # return true for general propose
        return result

    def post_nt6_employees(self, employees: list, refer: dict):
        """ Send employees to nettime with spec_utils.nettime6 module. """
        
        # open api connection with auto-disconnect
        with self.open_nt6_connection(source="destiny") as client:

            # employee structure
            data = {"container": "Persona"}

            for employee in employees:
                # search employee by nif
                query = nt6.Query(
                    fields=["id", "nif"],
                    filterExp=f'this.nif = "{employee.get(refer.get("nif"))}"',
                )
                results = client.get_employees(query=query)

                # safety only
                if results.get('total') <= 1:

                    # update employee
                    if results.get('total') == 1:
                        # set element
                        data["elements"] = [results.get('items')[0].get('id')]
                        # empty data
                        dataObj = {}
                    
                    # create element
                    else:
                        # create form and assign all timetypes and readers
                        dataObj = client.get_create_form(container="Persona")
                        dataObj.update({
                            "TimeTypesEmployee": self.get_nt6_timetypes(client),
                            "Readers": self.get_nt6_readers(client)
                        })
                        
                        # delete elements kw
                        if data.get("elements", None):
                            del data["elements"]

                    dataObj.update(
                        {k: employee.get(v) for k, v in refer.items()}
                    )
                    data["dataObj"] = dataObj

                    # save employee
                    last_responsse = client.save_element(**data)
                    #print(last_responsse)

        # return true for general propose
        return True

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
        
    
    






