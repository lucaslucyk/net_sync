# -*- coding: utf-8 -*-

### built-in ###
# ...
### django ###
# ...

### own ###
from utils import processors as procs
from utils.api import FieldDefinition

### third ###
from spec_utils import visma
from spec_utils import nettime6 as nt6
from spec_utils import exactian
from spec_utils import specmanagerdb as smdb
import pandas as pd

class SyncMethods(object):

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

    def open_exactian_connection(self, source: str):
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
        return exactian.Client(url=host, username=username, pwd=pwd)

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

    def apply_fields_def(self, structure: list, fields_def: list):
        """
        Receives a json structure and returns another one applying the field 
        definition to each element of the original structure.

        @@ Parameters
        @structure (list):
            JSON structure where each element is a key:value pair dictionary.
        @fields_def (list):
            List of api.FieldDefinition elements.

        @@ Returns
        @list: List or result elements
        """

        # empty data by default
        out_data = []

        # for all elements in structure
        for elem in structure:
            _structure = {}
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

                # insert in _structure if has value or defaultget
                if not value and getattr(fd, 'default', None):
                    _structure.update({fd.out_name: fd.default})
                if value:
                    _structure.update({fd.out_name: value})

            # append complete _structure
            out_data.append(_structure)

        return out_data


    def get_nt6_employees(self, fields: list, filterExp: str = None) -> list:
        """
        Get employees from nettime with spec_utils.nettime6 module.
        
        @@ Parameters
        @fields (list):
            List of api.FieldDefinition elements.
        @filterExp (str):
            Nettime compliant filter expression. None by default.

        @@ Returns
        @list: list of elements obtained from nettime and processed with the 
            "fields" parameter.
        """

        # getting last run or default value
        last_run = '2000-01-01'
        if self.get_last_run():
            last_run = self.get_last_run().strftime("%Y-%M-%d")

        # open api connection with auto-disconnect
        with self.open_nt6_connection(source="origin") as client:

            # add expression for ignore old syncs (this.modified >= lastSync)
            query = nt6.Query(
                fields=[f.get('origin') for f in fields],
                filterExp='{}(this.modified >= "{}")'.format(
                    f'({filterExp}) && ' if filterExp else '',
                    last_run
                )
            )

            # get employees
            nt_response = client.get_employees(query=query)

        return self.apply_fields_def(
            structure=nt_response.get('items', []),
            fields_def=[FieldDefinition.from_json(f) for f in fields]
        )

    def get_visma_employees(self, fields: list, active: bool = None, \
            extensions: list = [], pageSize: int = 5, all_pages: bool = False):
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

        @@ Returns
        @list: list of elements obtained from visma and processed with the 
            "fields" parameter.
        """

        # getting last run or default value
        last_run = '2000-01-01'
        if self.get_last_run():
            last_run = self.get_last_run().strftime("%Y-%M-%d")
        
        # open api connection with auto-disconnect
        with self.open_visma_connection(source="origin") as client:

            # out employees
            employees_detail = []
            
            # no detail
            response = client.get_employees(
                active=False,
                updatedFrom=last_run,
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
                        ).get('values', [])
                    })

                # push employee in detail list
                employees_detail.append(employee)

        #print(employees_detail)
        return self.apply_fields_def(
            structure=employees_detail,
            fields_def=[FieldDefinition.from_json(f) for f in fields]
        )

    def get_exactian_employees(self, fields: list, **kwargs) -> list:
        """
        Get employees from exactian with spec_utils.exactian module.
        
        @@ Parameters
        @fields (list):
            List of api.FieldDefinition elements.

        @@ Returns
        @list: list of elements obtained from exactian and processed with the 
            "fields" parameter.
        """

        # open api connection with auto-disconnect
        with self.open_exactian_connection(source="origin") as client:
            # get exactian structure
            employees = client.get_emnployees()

        return self.apply_fields_def(
            structure=employees,
            fields_def=[FieldDefinition.from_json(f) for f in fields]
        )

    def get_smdb_employees(self, fields: list = [], **kwargs):
        """
        Get employees from SM with spec_utils.specmanagerdb module.
        
        @@ Parameters
        @fields (list):
            List of api.FieldDefinition elements.
        @**kwargs **optional**:
            The following parameters can be passed:
            @to_records (bool):
                False to get a pandas structure as a result. True by default.
            @top (int):
                Max results to get from specmanager database. 5 by Default.
            @where (str):
                String to determine the condition of the sql statement.
            @group_by (list):
                List of string to group items. Empty list by default.

        @@ Returns
        @list: list of elements obtained from nettime and processed with the 
            "fields" parameter.
        """
        
        # get manager fields from fields definition
        sm_fields = [f.get('origin') for f in fields]

        # open api connection with auto-disconnect
        with self.open_smdb_connection(source="origin") as client:
            sm_employees = client.get_employees(
                to_records=kwargs.get('to_records', True),
                fields=sm_fields or ['*'],
                top=kwargs.get('top', 5),
                where=kwargs.get('where', None),
                group_by=kwargs.get('group_by', []),
                table=kwargs.get('table', "PERSONAS"),
            )

        # return structure
        return self.apply_fields_def(
            structure=sm_employees,
            fields_def=[FieldDefinition.from_json(f) for f in fields]
        )

    def post_smdb_employees(self, employees: list, fields: list, **kwargs):
        """
        Send employees to nettime with spec_utils.smdb module.
        
        @@ Parameters
        @employees (list):
            List of dict to send to spec manager.
        @fields (list):
            List of api.FieldDefinition elements.
        @**kwargs **optional**:
            The following parameters can be passed:
            @to_records (bool):
                False to get a pandas structure as a result. True by default.
            @top (int):
                Max results to get from specmanager database. 5 by Default.
            @where (str):
                String to determine the condition of the sql statement.
            @group_by (list):
                List of string to group items. Empty list by default.

        @@ Returns
        @list: True if no error occurred inserting the values in database.
        """


        # updating structure with field_def
        employees = self.apply_fields_def(
            structure=employees,
            fields_def=[FieldDefinition.from_json(f) for f in fields]
        )

        # open api connection with auto-disconnect
        with self.open_smdb_connection(source="destiny") as client:
            
            # convert if is not dataframe
            if not isinstance(employees, pd.DataFrame):
                employees = pd.DataFrame.from_records(employees)

            # send data to module
            result = client.import_employees(
                employees=employees,
                source=str(self.origin),
                **kwargs
            )

        # return true for general propose
        return result

    def post_nt6_employees(self, employees: list, fields: list, **kwargs):
        """
        Send employees to nettime with spec_utils.nettime6 module.
        
        @@ Parameters
        @employees (list):
            List of dict to send to nettime.
        @fields (list):
            List of api.FieldDefinition to apply in employees* structure.

        @@ Returns
        @bool: True if no error occurred in the nettime api.
        """

        # updating structure with field_def
        employees = self.apply_fields_def(
            structure=employees,
            fields_def=[FieldDefinition.from_json(f) for f in fields]
        )
        
        # open api connection with auto-disconnect
        with self.open_nt6_connection(source="destiny") as client:
            # import employees one by one
            for employee in employees:
                response = client.import_employee(structure=employee)

        # return true for general propose
        return True

    def post_nt6_departments(self, structure: list, fields: list, \
            levels: list = [], reverse: bool = False):
        """
        Send structure to nettime with spec_utils.nettime6 module.
        
        @@ Parameters
        @structure (list):
            List of dict of departments. Must have 'nif' and 'path' elements.
        @fields (list):
            List of api.FieldDefinition to apply in structure* structure.
        @levels (list):
            List of str levels to create structure*. Empty by default.
        @reverse (bool):
            Use if path is in reverse order. False by default.

        @@ Returns
        @bool: True if no error occurred in the nettime api.
        """

        # updating structure with field_def
        structure = self.apply_fields_def(
            structure=structure,
            fields_def=[FieldDefinition.from_json(f) for f in fields]
        )

        # open api connection with auto-disconnect
        with self.open_nt6_connection(source="destiny") as client:

            for element in structure:
                # search employee by nif
                query = nt6.Query(
                    fields=["id", "nif"],
                    filterExp=f'this.nif = "{element.get("nif")}"',
                )
                results = client.get_employees(query=query)

                # set path to department
                if levels:
                    path = [element.get(level) for level in levels]
                else:
                    path = element.get('path')

                # update employee
                if results.get('total') == 1:
                    # assign with summary method
                    response = client.set_employee_department(
                        employee=results.get('items')[0].get('id'),
                        node_path=path[::-1 if reverse else 1]
                    )

        # return true for general propose
        return True