# -*- coding: utf-8 -*-

### built-in ###
import datetime as dt

### django ###
# ...

### own ###
# ...

### third ###
from spec_utils import specmanagerdb as smdb
import pandas as pd

class Client:

    def __init__(self, source, last_run: dt.datetime, **kwargs):
        """
        Create a SPECManager DB API client.
        
        @@ Parameters
        @source (Sync): Must be a Sync instance.
        """

        self.name = "SPECManager DB API"
        self.source = source
        self.last_run = last_run

        # connection params
        params = source.credentialparameter_set.all()
        self.server = params.filter(key='server').first().value
        self.username = params.filter(key='user').first().value
        self.pwd = params.filter(key='password').first().value
        self.database = params.filter(key='database').first().value
        self.controller = params.filter(key='controller').first().value

        self.extra_parameters = kwargs

    def open_connection(self, **kwargs):
        """ Open and return a SPECManager DB API Client. """

        # create and return client
        return smdb.Client(
            username=self.username,
            pwd=self.pwd,
            server=self.server,
            database=self.database,
            controller=self.controller,
            **self.extra_parameters,
            **kwargs
        )

    def get_employees(self, fields: list = [], **kwargs):
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
        with self.open_connection() as client:
            sm_employees = client.get_employees(
                to_records=kwargs.get('to_records', True),
                fields=sm_fields or ['*'],
                top=kwargs.get('top', 5),
                where=kwargs.get('where', None),
                group_by=kwargs.get('group_by', []),
                table=kwargs.get('table', "PERSONAS"),
            )

        # return structure
        return api.apply_fields_def(
            structure=sm_employees,
            fields_def=[api.FieldDefinition.from_json(f) for f in fields]
        )

    def get_results(self, fields: list, from_table: str, \
            marc_col: str, auto_update: bool = True, **kwargs):
        """ Get results from custom table in SPEC Manager. """

        # open api connection with auto-disconnect
        with self.open_connection() as client:
            results = client.sync_results(
                from_table=from_table,
                marc_col=marc_col,
                auto_update=auto_update,
                to_records=kwargs.get('to_records', True),
                top=kwargs.get('top', 5),
            )

        # return structure
        return api.apply_fields_def(
            structure=results,
            fields_def=[api.FieldDefinition.from_json(f) for f in fields]
        )

    def post_employees(self, employees: list, fields: list, **kwargs):
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
        employees = api.apply_fields_def(
            structure=employees,
            fields_def=[api.FieldDefinition.from_json(f) for f in fields]
        )

        # open api connection with auto-disconnect
        with self.open_connection() as client:

            # convert if is not dataframe
            if not isinstance(employees, pd.DataFrame):
                employees = pd.DataFrame.from_records(employees)

            # send data to module
            result = client.import_employees(
                employees=employees,
                source=str(self.source),
                **kwargs
            )

        # return true for general propose
        return result
