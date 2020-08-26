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
        return self.get_application_display()

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

    def open_nt6_connection(self, source: str):
        """
        Create and return a nettime client.
        Source specify origin or destiny conn.
        """

        # connection params
        params = getattr(self, source).credentialparameter_set.all()
        host = params.filter(key='host').first()
        username = params.filter(key='user').first()
        pwd = params.filter(key='password').first()

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

    def get_nt_employees(self, fields: list = None):

        # open api connection
        client = self.open_nt6_connection(source="origin")
        
        # fields to synchronize
        fields = ["nif", "name", "nameEmployee", "LastName"]
        
        # prepare nt query with fields
        query = nt6.Query(
            fields=fields,
            filterExp='(true = true) && (1 = 1)'
        )

        # get employees
        employees = client.get_employees(query=query)

        # close connection
        client.disconnect()

        # return employees results. Empty list by default
        return employees.get('items', [])

    def post_nt_employees(self, employees: list, refer: dict):
        
        # open api connection
        client = self.open_nt6_connection(source="destiny")

        # match fields between apps
        refer = {
            # destiny : origin
            'nif': 'nif',
            'name': 'name',
            'nameEmployee': 'nameEmployee',
            'LastName': 'LastName'
        }

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
                    dataObj = client.get_create_form(container="Persona")
                    
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
    value = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return str(self.sync)
    






