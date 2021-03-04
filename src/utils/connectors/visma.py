# -*- coding: utf-8 -*-

### built-in ###
import datetime as dt

### django ###
# ...

### own ###
# ...

### third ###
from spec_utils import visma


class Client:

    def __init__(self, source, last_run: dt.datetime, **kwargs):
        """
        Create a Visma API client.
        
        @@ Parameters
        @source (Sync): Must be a Sync instance.
        """

        self.name = "Visma API"
        self.source = source
        self.last_run = last_run

        # connection params
        params = source.credentialparameter_set.all()
        self.url = params.filter(key='host').first().value
        self.username = params.filter(key='user').first().value
        self.pwd = params.filter(key='password').first().value

        self.extra_parameters = kwargs

    def open_connection(self, **kwargs):
        """ Open and return a Visma API Client. """

        return visma.Client(
            url=self.url,
            username=self.username,
            pwd=self.pwd,
            **self.extra_parameters,
            **kwargs
        )

    def get_employees(self, fields: list, active: bool = None, \
            extensions: list = [], pageSize: int = 5, \
            all_pages: bool = False, tenant_filter: dict = None, \
            updatedFrom: dt.datetime = None, **kwargs):
        """
        Get employees from visma with spec_utils.visma module.
        
        @@ Parameters
        @fields (list):
            List of api.FieldDefinition elements.
        @active (bool):
            True/False to filter visma employees. None by default.
        @extensions (list):
            List of str with extensions to append to structure. Will be append
            with _extension_name.
        @pageSize (int):
            Num of results per page in Visma request. 5 by default.
        @all_pages (bool):
            Recursive get page to get all.
        @tenant_filter (dict):
            Dict to get results from specific tenant. First by default.
        @updatedFrom (datetime.datetime):
            Datetime to force get employees.
        @tenant_filter (dict):
            Dict to force results from specific tenant. First by default.

        @@ Returns
        @list: list of elements obtained from visma and processed with the 
            "fields" parameter.
        """

        # getting last run or default value
        date_start = self.last_run

        # with recived values
        if updatedFrom:
            date_start = dt.datetime.strptime(updatedFrom, "%Y%m%d%H%M%S")

        # open api connection with auto-disconnect
        with self.open_connection(tenant_filter=tenant_filter) as client:

            # out employees
            employees_detail = []

            # no detail
            response = client.get_employees(
                active=active,
                updatedFrom=date_start.strftime("%Y-%m-%d"),
                pageSize=pageSize,
                all_pages=all_pages
            )

            for result in response.get('values'):
                # get employee detail
                employee = client.get_employees(
                    employee=f'rh-{result.get("id")}'
                )
                # optional extension/s
                for extension in extensions:
                    employee.update({
                        f'_{extension}': client.get_employees(
                            employee=f'rh-{result.get("id")}',
                            extension=extension,
                            all_pages=True
                        ).get('values', [])
                    })

                # push employee in detail list
                employees_detail.append(employee)

        return api.apply_fields_def(
            structure=employees_detail,
            fields_def=[api.FieldDefinition.from_json(f) for f in fields]
        )

    def post_payments(self, structure: list, sync_cfgs: dict, \
            tenant_filter: dict = None, **kwargs):
        """
        Send structure with payment values to visma with spec_utils.visma mod.
        
        @@ Parameters
        @structure (list):
            List of dict of departments. Must have 'nif' and 'path' elements.
        @fields (list):
            List of api.FieldDefinition to apply in structure* structure.
        @tenant_filter (dict):
            Dict to force results to specific tenant. First by default.

        @@ Returns
        @bool: True if no error occurred in the nettime api.
        """

        # updating structure with field_def
        elements = api.ntRes_to_vismaPayments(
            syncs=structure,
            sync_cfgs=sync_cfgs
        )

        # if can't get elements
        if not elements:
            return True

        # open temporal visma client
        with self.open_connection(tenant_filter=tenant_filter) as client:

            # send data
            result = client.post_pay_elements(values=elements, **kwargs)

        # general propose
        if not result:
            return False

        # general propose
        return True
