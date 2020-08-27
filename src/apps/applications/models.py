from django.db import models
from django.conf import settings

# own
from utils import visma
from utils import nettime6 as nt6

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

    def __str__(self):
        return self.get_synchronize_display()

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
        app_origin_params = self.syncparameter_set.filter(use_in='origin')
        app_dest_params = self.syncparameter_set.filter(use_in='destiny')

        # parse elements
        parse_origin_params = {p.key: eval(p.value) for p in app_origin_params}
        parse_dest_params = {p.key: eval(p.value) for p in app_dest_params}

        #print(parse_dest_params)

        # executing methods
        origin_response = get_method(**parse_origin_params)
        destiny_response = post_method(origin_response, **parse_dest_params)

        #print(origin_response)

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

        return nt6.Client(url=host, username=username, pwd=pwd)

    def open_visma_connection(self, source: str):
        """
        Create and return a visma client.
        Source specify origin or destiny conn.
        """

        # connection params
        params = getattr(self, source).credentialparameter_set.all()
        host = params.filter(key='host').first()
        username = params.filter(key='user').first()
        pwd = params.filter(key='password').first()

        return visma.Client(url=host, username=username, pwd=pwd)

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

    def get_nt6_employees(self, fields: list, filterExp: str = None):

        # open api connection
        client = self.open_nt6_connection(source="origin")
        
        # prepare nt query with fields
        # add expression for ignore old migrations (this.modified >= lastSync)
        query = nt6.Query(
            fields=fields,
            filterExp='{}(this.modified >= "{}")'.format(
                f'({filterExp}) && ' if filterExp else '',
                '2020-08-26'
            )
        )

        # get employees
        employees = client.get_employees(query=query)

        # close connection
        client.disconnect()

        # return employees results. Empty list by default
        return employees.get('items', [])

    def post_nt6_employees(self, employees: list, refer: dict):
        
        # open api connection
        client = self.open_nt6_connection(source="destiny")

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

                dataObj.update({k: employee.get(v) for k, v in refer.items()})
                data["dataObj"] = dataObj

                # save employee
                client.save_element(**data)

        # close connection
        client.disconnect()

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
    value = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return str(self.sync)


class SyncHistory(models.Model):

    sync = models.ForeignKey("Sync", on_delete=models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)
    ok = models.BooleanField(default=True)

    error = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.sync} | {self.date_time.strftime("%d/%m/%Y %H:%M:%S")}'
    
    






