# -*- coding: utf-8 -*-

### built-in ###
import json
from re import split as re_split

### django ###
# ...

### own ###
from utils import processors as procs

### third ###
from spec_utils import visma
from spec_utils import nettime6 as nt6
from spec_utils import exactian
from spec_utils import specmanagerdb as smdb
import pandas as pd


class FieldDefinition:

    def __init__(self, out_name: str, in_name: str, steps: list=None, \
            default: str = None):
        self.out_name = out_name
        self.in_name = in_name
        self.steps = [self.Step.from_json(step) for step in steps]
        self.default = default

    def __str__(self):
        return repr(self)
    
    def __repr__(self):
        return '{}(out_name="{}", in_name="{}", steps={})'.format(
            self.__class__.__name__,
            self.out_name,
            self.in_name,
            self.steps
        )

    @classmethod
    def from_json(cls, parsed_js: dict):
        """
        Create an instance of FieldDefinition with the "parser_js" dict.
        
        @@ Parameters
        @parsed_js (dict):
            Dict that must contain the following keys:
            @origin (str):
                Name of field in origin (in) structure.
            @destiny (str):
                Name of field in destiny (out) structure.
            @default (any) *optional*:
                Any object to assign in case the value cannot be obtained or 
                any step* returns a null value.
            @steps (list) *optional*: 
                List of steps to apply in source field to get the output.
                The steps are recursively executed until get the value.
                Each step is made up of the following keys:
                @method (str):
                    Name of method to execute. Must exist in processors module.
                @args (list):
                    List of parameters to pass to the method. 
                    They can be numeric values, strings, etc.
                @kwargs (dict): 
                    Key:Value pairs, where the key is the name of the parameter 
                    with its respective value.
                    Use this to ensure future compatibility or to pass 
                    additional parameters.

        @@ Returns
        @FieldDefinition : Instance of FieldDefinition.
        """
        
        # if recives json unparsed
        if isinstance(parsed_js, str):
            parsed_js = json.loads(parsed_js)

        return cls(
            out_name=parsed_js.get('destiny'),
            in_name=parsed_js.get('origin'),
            steps=parsed_js.get('steps', []),
            default=parsed_js.get('default', None)
        )

    class Step:
        def __init__(self, method: str, _args: list = [], _kwargs: dict = {}):
            self.method = method
            self._args = _args
            self._kwargs = _kwargs

        def __str__(self):
            return repr(self)

        def __repr__(self):
            return '{}(method="{}"{}{})'.format(
                self.__class__.__name__,
                self.method,
                f', _args={self._args}' if self._args else '',
                f', _kwargs={self._kwargs}' if self._kwargs else ''
            )
        
        @classmethod
        def from_json(cls, parsed_js: dict):
            """
            Create an instance of Step with the "parser_js" dict.
            
            @@ Parameters
            @method (str):
                Name of method to execute. Must exist in processors module.
            @args (list):
                List of parameters to pass to the method. 
                They can be numeric values, strings, etc.
            @kwargs (dict): 
                Key:Value pairs, where the key is the name of the parameter 
                with its respective value.
                Use this to ensure future compatibility or to pass 
                additional parameters.

            @@ Returns
            @Step : Instance of Step.
            """
            # if recives json unparsed
            if isinstance(parsed_js, str):
                parsed_js = json.loads(parsed_js)

            return cls(
                method=parsed_js.get('method'),
                _args=parsed_js.get('args', []),
                _kwargs=parsed_js.get('kwargs', {})
            )


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
        if self.get_previous_run():
            last_run = self.get_previous_run().strftime("%Y-%m-%d %H:%M:%S")

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

    def get_nt6_results(self, params: dict, fields: list):
        """
        Get cube results from nettime with spec_utils.nettime6 module.
        
        @@ Parameters
        @params (dict):
            Dict parameters for parsed pass to client.get_cube_results(). Eg.
            {
                "dateIni": "2020-07-02",
                "dateEnd": "2020-07-04",
                "dimensions": [
                    ["id", "Apellidos_Nombre"],
                    ["date"],
                    [
                        "ResultValue_C.Min.NORMALES",
                        "ResultValue_S.Min.Jornada_teorica"
                    ]
                ]
            }
            *Last element of "dimensions" key will be interpreted how "column".
        @fields (list):
            List of api.FieldDefinition elements.
        
        @@ Returns
        @list: list of elements obtained from nettime and processed with the 
            "fields" parameter.
        """

        # open api connection with auto-disconnect
        with self.open_nt6_connection(source="origin") as client:
            # get results
            cube_results = client.get_cube_results(**params)

        return self.apply_fields_def(
            structure=cube_results,
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
        if self.get_previous_run():
            last_run = self.get_previous_run().strftime("%Y-%m-%d %H:%M:%S")

        # open api connection with auto-disconnect
        with self.open_visma_connection(source="origin") as client:

            # out employees
            employees_detail = []

            # no detail
            response = client.get_employees(
                active=active,
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
                            all_pages=True
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

    def get_smdb_results(self, fields: list, from_table: str, \
            marc_col: str, auto_update: bool = True, **kwargs):
        """ Get results from custom table in SPEC Manager. """

        # open api connection with auto-disconnect
        with self.open_smdb_connection(source="origin") as client:
            results = client.sync_results(
                from_table=from_table,
                marc_col=marc_col,
                auto_update=auto_update,
                to_records=kwargs.get('to_records', True),
                top=kwargs.get('top', 5),
            )

        # return structure
        return self.apply_fields_def(
            structure=results,
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

    def post_visma_payments(self, structure: list, fields: list, **kwargs):
        """
        Send structure with payment values to visma with spec_utils.visma mod.
        
        @@ Parameters
        @structure (list):
            List of dict of departments. Must have 'nif' and 'path' elements.
        @fields (list):
            List of api.FieldDefinition to apply in structure* structure.

        @@ Returns
        @bool: True if no error occurred in the nettime api.
        """

        # updating structure with field_def
        structure = self.apply_fields_def(
            structure=structure,
            fields_def=[FieldDefinition.from_json(f) for f in fields]
        )

        with self.open_visma_connection(source="destiny") as client:

            # send data
            result = client.post_pay_elements(values=structure, **kwargs)

        return True
