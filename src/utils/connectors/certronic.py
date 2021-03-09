# -*- coding: utf-8 -*-

### built-in ###
import datetime as dt
from math import ceil

### django ###
# ...

### own ###
from utils import api

### third ###
from spec_utils import certronic


class Client:

    def __init__(self, source, last_run: dt.datetime, **kwargs):
        """
        Create a Certronic API client.
        
        @@ Parameters
        @source (Sync): Must be a Sync instance.
        """
        
        self.name = "Certronic API"
        self.source = source
        self.last_run = last_run

        # connection params
        params = source.credentialparameter_set.all()
        self.url = params.filter(key='host').first().value
        self.apikey = params.filter(key='apikey').first().value

        self.extra_parameters = kwargs

    def open_connection(self, **kwargs):
        """ Open and return a Certronic API Client. """

        return certronic.Client(
            url=self.url,
            apikey=self.apikey,
            **self.extra_parameters,
            **kwargs
        )

    def get_employees(self, fields: list, _from: str = None, \
            all_pages: bool = False, **kwargs):
        """
        Get employees from Certronic API module with recived parameters.

        @@ Parameters
        @fields (list):
            List of api.FieldDefinition elements.
        @_from (str):
            Optional string with datetime format (YYYYMMDDhhmmss) to filter 
            employees. Last Run by default
        @all_pages (bool):
            Optional to get all pages with _from and _to context.
            False by default
        @**kwargs (*dict):
            Extra parameters to pass to method certronic.get_employees.

        @@ Returns
        @list: List of employees
        """

        # get last run and current datetime
        date_start = self.last_run
        
        # with recived values
        if _from:
            date_start = dt.datetime.strptime(_from, "%Y%m%d%H%M%S")
        
        with self.open_connection() as client:
            
            # get from SM API
            ct_response = client.get_employees(
                updatedFrom=date_start,
                **kwargs
            )
            # get total pages
            _count = ct_response.get('count', 0)
            _pageSize = ct_response.get('pageSize')
            
            # calculate pages number
            _pages = ceil(_count / _pageSize) if _count else 1

            # aletrnative
            if all_pages and _pages > 1:
                for i in range(2, _pages +1):
                    ct_response["employees"].extend(
                        client.get_employees(
                            updatedFrom=date_start,
                            page=i,
                            **kwargs
                        ).get('employees')
                    )

        # apply field def
        return api.apply_fields_def(
            structure=ct_response.get('employees', []),
            fields_def=[api.FieldDefinition.from_json(f) for f in fields]
        )

    def post_clockings(self, fields: list, clockings: list, **kwargs):
        """
        Send clockings to Certronic API module with recived parameters.

        @@ Parameters
        @fields (list):
            List of api.FieldDefinition elements.
        @clockings (list):
            List with params of spec_utils.specmanagerapi.post_employee()
            To get more info of clockings structure, check help for 
            spec_utils.specmanagerapi.post_employee() method.
        @**kwargs (*dict):
            Extra parameters to pass to method post_clockings.

        @@ Returns
        @dict: Dict with Certronic API response.
        """

        # updating structure with fields
        clockings = api.apply_fields_def(
            structure=clockings,
            fields_def=[api.FieldDefinition.from_json(f) for f in fields]
        )

        # open api connection with auto-disconnect
        with self.open_connection() as client:

            # send data to module
            result = client.post_clockings(
                clockings=clockings,
                **kwargs
            )

        # return true for general propose
        return result







