# -*- coding: utf-8 -*-

### built-in ###
import datetime as dt

### django ###
# ...

### own ###
from utils import processors as procs

### third ###
from spec_utils import exactian

import pandas as pd


class Client:

    def __init__(self, source, last_run: dt.datetime, **kwargs):
        """
        Create a Exactian API client.
        
        @@ Parameters
        @source (Sync): Must be a Sync instance.
        """

        self.name = "Exactian API"
        self.source = source
        self.last_run = last_run

        # connection params
        params = source.credentialparameter_set.all()
        self.url = params.filter(key='host').first().value
        self.username = params.filter(key='user').first().value
        self.pwd = params.filter(key='password').first().value

        self.extra_parameters = kwargs

    def open_connection(self, **kwargs):
        """ Open and return a Exactian API Client. """

        return exactian.Client(
            url=self.url,
            username=self.username,
            pwd=self.pwd,
            **self.extra_parameters,
            **kwargs
        )

    def get_employees(self, fields: list, **kwargs) -> list:
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
        with self.open_connection() as client:
            # get exactian structure
            employees = client.get_emnployees()

        return api.apply_fields_def(
            structure=employees,
            fields_def=[api.FieldDefinition.from_json(f) for f in fields]
        )
