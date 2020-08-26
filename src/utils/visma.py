from string import digits as str_digits, ascii_lowercase as str_letters
from random import choice as r_choice
from urllib.parse import urlparse, urlencode, urljoin
from base64 import b64encode, b64decode
import requests
import datetime
import re

#import nettime6 as nt6

class JsonObject:
    """ Convert a dict['element'] for access like object.property. """

    def __init__(self, json: dict):
        for k, v in json.items():
            setattr(self, k, v)

class Client:

    class Account:
        def __init__(self, **kwargs):
            self.tenants = [JsonObject(tnt) for tnt in kwargs.get('tenants')]
            self.user_info = JsonObject(kwargs.get('user_info'))
            self.roles = [JsonObject(roles) for roles in kwargs.get('roles')]

        @property
        def ft_id(self):
            """ Return the id of the first available tenant. """
            return getattr(self.tenants[0], 'Id', None)
    
    class Authentication:
        def __init__(self, **kwargs):
            self.access_token = kwargs.get('access_token')
            self.token_type = kwargs.get('token_type', '').capitalize()
            self.expires = self.get_expires(kwargs.get('expires_in'))

            self.rol = kwargs.get('rol')
            self.user_info = kwargs.get('user_info')

        def __str__(self):
            return f'{self.token_type} {self.access_token}'

        def __bool__(self):
            return self.is_alive

        def get_expires(self, expires_in: int) -> datetime.datetime:
            now = datetime.datetime.now()
            return now + datetime.timedelta(seconds=expires_in - 10)

        @property
        def is_alive(self):
            return self.expires > datetime.datetime.now()

        @property
        def is_expired(self):
            return not self.is_alive

    def __init__(self, url: str, username: str, pwd: str, *args, **kwargs):
        """ Create a conection with visma app using recived parameters. """

        #super().__init__(*args, **kwargs)

        self.client_url = urlparse(url)
        self.username = username
        self.pwd = b64encode(pwd.encode('utf-8'))

        self.authentication = None
        self.account = None

        # connect client and set authentication object automatically
        self.connect()

        # set account data automatically
        self.account = self.Account(
            tenants=self.get(path='/Admin/account/tenants'),
            user_info=self.get(path='/Admin/account/user-info'),
            roles=self.get(path='/Admin/account/roles')
        )

    def __str__(self):
        return '{}{} en {}'.format(
            f'{self.access_token} para ' if self.access_token else '',
            self.username,
            self.client_url.geturl()
        )

    def __repr__(self):
        return "{}(url='{}', username='{}', pwd='{}')".format(
            self.__class__.__name__,
            self.client_url.geturl(),
            self.username,
            b64decode(self.pwd).decode('utf-8'),
        )

    @property
    def headers(self):
        """ Get headers of the client with current data """

        # empty headers initial
        data = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip,deflate",
        }

        # logged user
        if self.authentication:
            data["Authorization"] = str(self.authentication)

        # tenant obtained
        if self.account:
            data["X-RAET-Tenant-Id"] = getattr(self.account, 'ft_id', None)

        return data
    
    @property
    def is_connected(self):
        """ Informs if client has headers and access_token. """

        return bool(self.authentication)

    @property
    def session_expired(self):
        """
        Informs if the session has expired and it is necessary to reconnect.
        """

        return getattr(self.authentication, 'is_expired', None)

    def get(self, path: str, params: dict = None, **kwargs):
        """
        Sends a GET request to nettime url.

        :param path: path to add to URL for the new :class:`Request` object.
        :param params: (optional) Dictionary, list of tuples or bytes to send
            in the query string for the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`dict` object
        :rtype: dict
        """

        # check if session has expired
        if self.session_expired:
            self.reconnect()

        # safety only
        if not self.is_connected and not kwargs.get('force', None):
            raise ConnectionError("Cliente desconectado. Utilice connect().")

        # query prepare
        query = {
            "url": urljoin(self.client_url.geturl(), path),
            "params": params,
            "headers": self.headers,
            "timeout": kwargs.get("timeout", 10),
        }

        # consulting nettime
        response = requests.get(**query)

        # raise if was an error
        if response.status_code not in range(200, 300):
            raise ConnectionError(response.text)

        # to json -> json
        try:
            return response.json()
        except:
            return {}

    def post(self, path, data=None, json=None, **kwargs):
        """
        Sends a POST request to nettime url.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) json data to send in the body of the 
            :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`dict` object
        :rtype: dict
        """

        # check if session has expired
        if self.session_expired:
            self.reconnect()

        # wait active conection
        if not self.is_connected and not kwargs.get('force', None):
            raise ConnectionError("Cliente desconectado. Utilice connect().")

        # query prepare
        query = {
            "url": urljoin(self.client_url.geturl(), path),
            "data": data,
            "json": json,
            "headers": self.headers,
            "timeout": kwargs.get("timeout", 10),
        }

        # consulting nettime
        response = requests.post(**query)

        # raise if was an error
        if response.status_code not in range(200, 300):
            raise ConnectionError(response.text)

        # to json -> json
        try:
            return response.json()
        except:
            return {}

    def connect(self):
        """ Connect the client to get access_token and headers values. """

        # None or not is_alive
        if self.is_connected:
            return

        # url and data prepare
        data = {
            "username": self.username,
            "password": b64decode(self.pwd).decode('utf-8'),
            "grant_type": "password"
        }
        response = self.post(
            path='/Admin/authentication/login',
            data=data,
            force=True
        )

        # if everything ok
        self.authentication = self.Authentication(**response)

    def disconnect(self):
        """ Disconnect the client if is connected. """

        # None or not is_alive
        if not self.is_connected:
            return

        response = self.post(path='/Admin/authentication/logout')
        self.authentication = None

    def reconnect(self):
        """ Reconnect client cleaning headers and access_token. """

        # clean token for safety
        self.authentication = None
        self.connect()

    def get_employees(self, employee: str = None, extension: str = None, \
            **kwargs):
        """
        Use the endpoint to obtain the employees with the received data.
        
        :param employee: Optional internal id (rh-#) or external id (#).
        :param extension: Oprtional str for add to endpoint.
            :Possible cases:
            'addresses', 'phones', 'phases', 'documents', 'studies',
            'structures', 'family-members', 'bank-accounts',
            'accounting-distribution', 'previous-jobs', *'image'*.
        :param **kwargs: Optional arguments that ``request`` takes.
            :Possible cases:
            'orderBy': Results order. Format: Field1-desc|asc, Field2-desc|asc.
            'page': Number of the page to return.
            'pageSize': The maximum number of results to return per page.
            'active': Indicates whether to include only active Employees, 
                inactive Employees, or all Employees.
            'updatedFrom': Expected format "yyyy-MM-dd". If a date is provided, 
                only those records which have been modified since that date are 
                considered. If no Date is provided (or None), all records will 
                be returned.
        
        :return: :class:`dict` object
        :rtype: json
        """
        
        # path prepare
        path = '/WebApi/employees{}{}'.format(
            f'/{employee}' if employee else '',
            f'/{extension}' if employee and extension else '',
        )

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
            "active": kwargs.get("active", None),
            "updatedFrom": kwargs.get("updatedFrom", None)
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def get_addresses(self, address: str = None, extension: str = None, \
            **kwargs):

        # check validity
        if address and extension:
            raise KeyError("No se pueden especificar un address y extension.")
        
        # path prepare
        path = '/WebApi/addresses{}{}'.format(
            f'/{address}' if address else '',
            f'/{extension}' if extension else '',
        )

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def get_birth_places(self, **kwargs):
        
        # path prepare
        path = '/WebApi/birth-places'

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
            "countryId": kwargs.get("countryId", None),
            "search": kwargs.get("search", None),
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def get_countries(self, **kwargs):

        # path prepare
        path = '/WebApi/countries'

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
            "search": kwargs.get("search", None),
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def get_family_members(self, **kwargs):

        # path prepare
        path = '/WebApi/family-members/types'

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def get_journals(self, journal: str = None, extension: str = "lines", \
            **kwargs):

        # path prepare
        path = '/WebApi/journals{}{}'.format(
            f'/{journal}' if journal and extension else '',
            f'/{extension}' if journal and extension else '',
        )

        # getting default date
        today = datetime.date.today()

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
            "dateFrom": kwargs.get("dateFrom", today.isoformat()),
            "dateTo": kwargs.get("dateTo", None),
            "processDate": kwargs.get("processDate", None),
            "companyId": kwargs.get("companyId", None),
            "companyName": kwargs.get("companyName", None),
            "account": kwargs.get("account", None),
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def get_leaves(self, extension: str = None, **kwargs):

        # path prepare
        path = '/WebApi/leaves{}'.format(
            f'/{extension}' if journal and extension else '',
        )

        # getting default date
        today = datetime.date.today()

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "dateFrom": kwargs.get("dateFrom", today.isoformat()),
            "typeLeaveId": kwargs.get("typeLeaveId", None),
            "leaveState": kwargs.get("leaveState", None),
            "employeeId": kwargs.get("employeeId", None),
            "dateTo": kwargs.get("dateTo", None),
            "dayType": kwargs.get("dayType", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
            "search": kwargs.get("search", None),
            "year": kwargs.get("year", None),
            "typeId": kwargs.get("typeId", None),
            "holidayModelId": kwargs.get("holidayModelId", None)
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def get_loans(self, **kwargs):

        # path prepare
        path = '/WebApi/loans'

        # getting default date
        today = datetime.date.today()

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "dateFrom": kwargs.get("dateFrom", today.isoformat()),
            "employeeId": kwargs.get("employeeId", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
            "search": kwargs.get("search", None)
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def get_nationalities(self, **kwargs):

        # path prepare
        path = '/WebApi/loans'

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
            "search": kwargs.get("search", None)
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def get_pay_elements(self, employeeExternalId: str, **kwargs):

        # path prepare
        path = '/WebApi/pay-elements/individual'

        # parameters prepare
        params = {
            "employeeExternalId": employeeExternalId,
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
            "search": kwargs.get("search", None),
            "dateFrom": kwargs.get("dateFrom", None),
            "dateTo": kwargs.get("dateTo", None),
            "conceptExternalId": kwargs.get("conceptExternalId", None)
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def post_pay_elements(self, **kwargs):
        pass

    def get_payments(self, extension: str, **kwargs):

        # path prepare
        path = f'/WebApi/payments/{extension}'

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5)
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def get_payments(self, extension: str, **kwargs):

        # path prepare
        path = f'/WebApi/payrolls/{extension}'

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
            "search": kwargs.get("search", None),
            "year": kwargs.get("year", None),
            "month": kwargs.get("month", None),
            "periodId": kwargs.get("periodId", None),
            "companyId": kwargs.get("companyId", None),
            "modelId": kwargs.get("modelId", None),
            "stateId": kwargs.get("stateId", None),
            "conceptTypeId": kwargs.get("conceptTypeId", None),
            "printable": kwargs.get("printable", None),
            "search": kwargs.get("search", None),
            "employeeId": kwargs.get("employeeId", None),
            "accumulatorId": kwargs.get("accumulatorId", None),
            "processId": kwargs.get("processId", None),
            "conceptId": kwargs.get("conceptId", None),
            "conceptCode": kwargs.get("conceptCode", None),
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def get_phases(self, phase: str = None, **kwargs):

        # path prepare
        path = '/WebApi/phases{}'.format(
            f'/{phase}' if phase else '',
        )

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
            "dateFrom": kwargs.get("dateFrom", None),
            "dateTo": kwargs.get("dateTo", None),
            "type": kwargs.get("type", None),
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def get_phones(self, phone: str = None, extension: str = None, **kwargs):

        # check validity
        if phone and extension:
            raise KeyError("No se pueden especificar un phone y extension.")

        # path prepare
        path = '/WebApi/phones{}{}'.format(
            f'/{phone}' if phone else '',
            f'/{extension}' if extension else '',
        )

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def get_scales(self, scale: int, **kwargs):

        # path prepare
        path = '/WebApi/scales'

        # parameters prepare
        params = {
            "id": scale,
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
            "coordinates": kwargs.get("coordinates", None),
            "order": kwargs.get("order", None),
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def get_seizures(self, startDate: str, **kwargs):

        # path prepare
        path = '/WebApi/seizures'

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
            "startDate": startDate,
            "employeeId": kwargs.get("employeeId", None),
            "stateId": kwargs.get("stateId", None)
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def get_structures(self, extension: str = None, **kwargs):

        # path prepare
        path = '/WebApi/structures{}'.format(
            f'/{extension}' if extension else ''
        )

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
            "typeId": kwargs.get("typeId", None),
            "active": kwargs.get("active", None),
            "search": kwargs.get("search", None)
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def get_sync(self, extension: str = None, applicationName: str = None, \
            **kwargs):

        if not extension and not applicationName:
            raise KeyError("Debe especificar un applicationName.")

        # path prepare
        path = '/WebApi/sync{}'.format(
            f'/{extension}' if extension else ''
        )

        # parameters prepare
        params = {
            "applicationName": applicationName,
            "parentEntity": kwargs.get("parentEntity", None),
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
            "lastUpdate": kwargs.get("lastUpdate", None),
        }

        # request.get -> json
        return self.get(path=path, params=params)
    
    def post_sync(self, **kwargs):
        pass

    def get_time_management(self, extension: str = None, **kwargs):
        
        # path prepare
        path = '/WebApi/sync{}'.format(
            f'/{extension}' if extension else ''
        )

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
            "employeeId": kwargs.get("employeeId", None),
            "dateFrom": kwargs.get("dateFrom", None),
            "dateTo": kwargs.get("dateTo", None),
            "typeOfHours": kwargs.get("typeOfHours", None),
            "search": kwargs.get("search", None),
            "shiftId": kwargs.get("shiftId", None),
            "statusId": kwargs.get("statusId", None),
            "clockId": kwargs.get("clockId", None),
            "subShiftId": kwargs.get("subShiftId", None),
            "active": kwargs.get("active", None),
            "detail": kwargs.get("detail", None),
            "structureTypeId1": kwargs.get("structureTypeId1", None),
            "structureId1": kwargs.get("structureId1", None),
            "structureTypeId2": kwargs.get("structureTypeId2", None),
            "structureId2": kwargs.get("structureId2", None),
            "structureTypeId3": kwargs.get("structureTypeId3", None),
            "structureId3": kwargs.get("structureId3", None),
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def post_time_management(self, **kwargs):
        pass

    def get_version(self):
        """
        Get current version information related with the assemblies name and 
        version.
        """

        # request.get -> json
        return self.get(path='/WebApi/version')
