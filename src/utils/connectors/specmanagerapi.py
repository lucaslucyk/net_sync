# -*- coding: utf-8 -*-

### built-in ###
import datetime as dt

### django ###
# ...

### own ###
from utils import api

### third ###
from spec_utils import specmanagerapi as smapi


class Client:

    def __init__(self, source, last_run: dt.datetime, **kwargs):
        """
        Create a SPECManager API client.
        
        @@ Parameters
        @source (Sync): Must be a Sync instance.
        """
        
        self.name = "SPEC Manager API"
        self.source = source
        self.last_run = last_run

        # connection params
        params = source.credentialparameter_set.all()
        self.url = params.filter(key='host').first().value
        self.apikey = params.filter(key='apikey').first().value

        self.extra_parameters = kwargs

    def open_connection(self, **kwargs):
        """ Open and return a SPEC Manager API Client. """

        return smapi.Client(
            url=self.url,
            apikey=self.apikey,
            **self.extra_parameters,
            **kwargs
        )

    def get_clockings(self, _type: str, fields: list, _from: str = None, \
            _to: str = None, all_pages: bool = False, **kwargs):
        """
        Get clockings from SPEC Manager API module with recived parameters.

        @@ Parameters
        @_type (str):
            String with employee type. E.g. 'employee', 'contractor'
        @fields (list):
            List of api.FieldDefinition elements.
        @_from (str):
            Optional string with datetime format (YYYYMMDDhhmmss) to filter 
            clockings. Last Run by default
        @_to (str):
            Optional string with datetime format (YYYYMMDDhhmmss) to filter 
            clockings. Now by default
        @all_pages (bool):
            Optional to get all pages with _from and _to context.
            False by default
        @**kwargs (*dict):
            Extra parameters to pass to method get_clockings.

        @@ Returns
        @list: List of clockings
        """

        # get last run and current datetime
        date_start = self.last_run
        date_stop = dt.datetime.now()
        
        # with recived values
        if _from:
            date_start = dt.datetime.strptime(_from, "%Y%m%d%H%M%S")
        if _to:
            date_stop = dt.datetime.strptime(_to, "%Y%m%d%H%M%S")
        
        with self.open_connection() as client:
            
            # get from SM API
            sm_response = client.get_clockings(
                _type=_type,
                _from=date_start,
                _to=date_stop,
                **kwargs
            )
            # get total pages
            _pages = sm_response.get('response', {}).get('pages', 1)

            # aletrnative
            if all_pages and _pages > 1:
                for i in range(2, _pages +1):
                    sm_response["response"]["clockings"].extend(
                        client.get_clockings(
                            _type=_type,
                            _from=date_start,
                            _to=date_stop,
                            page=i,
                            **kwargs
                        ).get('response').get('clockings')
                    )

        # apply field def or default return
        if fields:
            return api.apply_fields_def(
                structure=sm_response.get('response', {}).get('clockings', []),
                fields_def=[api.FieldDefinition.from_json(f) for f in fields]
            )

        # default
        return sm_response.get('response', {}).get('clockings', [])

    def post_employees(self, employees: list, fields: list = [], **kwargs):
        """
        Send employees to SPEC Manager API module with recived parameters.

        @@ Parameters
        @fields (list):
            List of api.FieldDefinition elements.
        @employees (list):
            List with params of spec_utils.specmanagerapi.post_employee()
            To get more info of employees structure, check help for 
            spec_utils.specmanagerapi.post_employee() method.
        @**kwargs (*dict):
            Extra parameters to pass to method post_employees.

        @@ Returns
        @dict: Dict with SPEC Manager API response.
        """

        # updating structure with fields
        if fields:
            employees = api.apply_fields_def(
                structure=employees,
                fields_def=[api.FieldDefinition.from_json(f) for f in fields]
            )

        # print(employees)

        # open api connection with auto-disconnect
        with self.open_connection() as client:

            # send data to module
            result = client.post_employees(
                employeeData=employees,
                **kwargs
            )

        # return true for general propose
        return result

