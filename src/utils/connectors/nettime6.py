from string import digits as str_digits, ascii_lowercase as str_letters
from random import choice as r_choice
from urllib.parse import urlparse, urlencode, urljoin
from base64 import b64encode, b64decode
import requests
import datetime
import re

__version__ = "0.1-Alpha"
__nettime__ = "6.0.1.17769"

def random_str(size=5, chars=str_digits + str_letters):
    """ Return a str of 'size' len with numbers and ascii lower letters. """

    return ''.join(r_choice(chars) for _ in range(size))

def create_random_suffix(name=""):
    """ Create a random name adding suffix after of clean recived name. """

    clean = re.sub('[^a-zA-Z0-9]', '_', name)
    clean += '_' if name else "" 
    clean += random_str(size=5)

    return clean

class Query:

    def __init__(self, fields: list, \
            startDate: str = datetime.date.today().isoformat(), \
            filterExp: str = ""):
        self.queryfields = self.QueryFields(fields, startDate)
        self.filterExp = self.filter_prepare(expression=filterExp)

    def prepare(self):
        """ Format a query in str for use in url. """

        query = '{}"fields":{}'.format('{', self.queryfields.prepare())

        if self.filterExp:
            query += f',"filterExp":"{self.filterExp}"'

        query += '}'
        return query

    def filter_prepare(self, expression: str = ""):
        return expression.replace('"', "'")

    class QueryFields:
        def __init__(self, names: list, \
                startDate: str = datetime.date.today().isoformat()):
            self.names = names
            self.startDate = startDate

        def prepare(self):
            """ Format a query in str for use in url. """

            fields = []
            for field in self.names:
                fields.append({
                    "name": field,
                    "startDate": self.startDate
                })

            return str(fields).replace("'", '"').replace(" ", "")


class Client:

    def __init__(self, url: str, username: str, pwd: str, *args, **kwargs):
        """ Create a conection with nettime app using recived parameters. """

        super().__init__(*args, **kwargs)
        self.client_url = urlparse(url)
        self.username = username
        self.pwd = b64encode(pwd.encode('utf-8'))

        ### None values
        self.access_token = None
        self.headers = None
        self.user_rol = None

        #connect client automatically
        self.connect()

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
    def is_connected(self):
        """ Informs if client has headers and access_token. """

        return bool(self.headers) and bool(self.access_token)

    def connect(self):
        """ Connect the client to get access_token and headers values. """

        if self.is_connected:
            return

        # url and data prepare
        url = urljoin(self.client_url.geturl(), '/api/login')
        data = {
            "username": self.username,
            "pwd": b64decode(self.pwd).decode('utf-8'),
        }
        response = requests.post(url, data=data)

        if response.status_code not in range(200, 300):
            raise ConnectionError(response.text)

        json_data = response.json()

        if not json_data.get("ok"):
            raise ConnectionError(json_data.get("message"))

        self.access_token = json_data.get("access_token")
        self.headers = self.get_headers()
        self.settings = self.get_settings()
        self.user_rol = self.get_user_rol()

    def reconnect(self):
        """ Reconnect client cleaning headers and access_token. """

        #clean token and headers for safety
        self.access_token = None
        self.headers = None

        self.connect()

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

        if not self.is_connected:
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

        # if session was closed, reconect client and try again
        if response.status_code == 401:
            self.reconnect()
            return self.post(path, params=params, **kwargs)

        # raise if was an error
        if response.status_code not in range(200, 300):
            raise ConnectionError(response.text)

        # to json
        return response.json()

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

        # wait active conection
        if not self.is_connected:
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

        # if session was closed, reconect client and try again
        if response.status_code == 401:
            self.reconnect()
            return self.post(path, data=data, json=json, **kwargs)

        # raise if was an error
        if response.status_code not in range(200, 300):
            raise ConnectionError(response.text)

        # to json -> json
        return response.json()

    def get_headers(self):
        """ Return headers for a specific conection """

        if not self.access_token:
            raise ConnectionError("El cliente esta desconectado.")

        return {
            "DNT": "1",
            "Content-Type": "application/json;charset=UTF-8",
            "Accept-Encoding": "gzip,deflate",
            "Cookie": f"sessionID={self.access_token}; i18next=es",
        }

    def disconnect(self):
        """ Disconnect a client to lock the access_token. """

        if not self.is_connected:
            return
        
        # disconnect ...
        response = self.post(path='/api/logout')

        # reset values
        self.access_token = None
        self.headers = None

    def get_settings(self):
        """ Get settings of netTime Server. """

        return self.get(path='/api/settings')

    def get_user_rol(self):
        """ Get user_rol of current session. """

        return self.settings.get('rol', None)

    def get_days_offset(self, days: list):
        """ 
        Convert a list of datetime.date or str format to int offset with \
        self.setting.firstDate.
        """

        # wait active conection
        if not self.is_connected:
            raise ConnectionError("Cliente desconectado. Utilice connect().")

        firstYear = self.settings.get('firstDate', None)
        if not firstYear:
            raise RuntimeError("No se puede obtener el setting firstDate.")
        
        # set first_date
        first_date = datetime.date(firstYear, 1, 1)

        # process dates
        days_numbers = []
        for day in days:
            # ensure datetime.date type
            if not isinstance(day, datetime.date):
                day = datetime.date.fromisoformat(day)

            delta = day - first_date
            days_numbers.append(delta.days)

        return days_numbers

    def get_days_from_ofsets(self, ofsets: list):
        """ 
        Convert a list of int offset to datetime.date or str format with \
        self.setting.firstDate.
        """

        # wait active conection
        if not self.is_connected:
            raise ConnectionError("Cliente desconectado. Utilice connect().")

        firstYear = self.settings.get('firstDate', None)
        if not firstYear:
            raise RuntimeError("No se puede obtener el setting firstDate.")

        # set first_date
        first_date = datetime.date(firstYear, 1, 1)

        # process dates
        dates = []
        for offset in offsets:
            date = first_date + datetime.timedelta(days=offset)
            dates.append(date.isoformat())
        
        return dates
        
    def get_fields(self, container: str, filterFields: bool = False):
        """ Get all fields of an specific container. """

        # prepare task parameters
        params = {
            "container": container,
            "filterFields": filterFields
        }

        # request.get
        return self.get(path='/api/container/fields', params=params)
    
    def get_elements(self, container: str, query = Query(["id", "name"]), \
            *args, **kwargs):
        """ Get elements of an specific container for general propose. """

        # prepare task parameters
        params = {
            "pageStartIndex": 0,
            "pageSize": kwargs.get("pageSize", 50),
            "search": kwargs.get("search", ""),
            "order": kwargs.get("order", ""),
            "desc": kwargs.get("desc", ""),
            "container": container,
            "query": query.prepare()
        }

        # request.get -> json
        json_response = self.get(path='/api/container/elements', params=params)

        # get task results
        if json_response.get('taskId', None):
            json_response = self.get_task_response(json_response.get('taskId'))

        return json_response

    def get_employees(self, query=Query(["id", "nif"]), *args, **kwargs):
        """ Get employees from nettime. """

        # use get general propose
        employees = self.get_elements(
            container="Persona", query=query, *args, **kwargs)

        return employees

    def container_action_exec(self, container: str, action: str, \
            elements: list, _all: bool = False, dataObj: dict = None, \
            *args, **kwargs):
        """ Execute an action for a container. """

        # prepare task parameters
        json_data = {
            "container": container,
            "action": action,
            "all": _all,
            "elements": elements,
            "dataObj": dataObj
        }
        json_data.update(kwargs)

        # request.get -> json
        return self.post(path='/api/container/action/exec', json=json_data)

    def save_element(self, container: str, dataObj: dict, \
            elements: list = [], _all: bool = False):
        """ Update an element of a container with the received values. """

        # data prepare
        data = {
            "action": "Save",
            "container": container,
            "elements": elements,
            "_all": _all,
            "dataObj": dataObj,
        }

        # executing and processing
        return self.container_action_exec(**data)

    def delete_element(self, container: str, elements: list, \
            _confirm: bool = True, _all: bool = False):
        """ Delete an element of a container with the received values. """

        # data prepare
        data = {
            "action": "Delete",
            "container": container,
            "elements": elements,
            "_all": _all,
        }

        # default auto confirm
        if _confirm:
            data["dataObj"] = {
                "_confirm": _confirm,
            }

        # executing and processing
        return self.container_action_exec(**data)

    def get_for_duplicate(self, container: str, element: int, \
            _all: bool = False):
        """ Get form for a new element with data of recived element. """

        # data prepare
        data = {
            "action": "Copy",
            "container": container,
            "elements": [element],
            "_all": _all,
        }

        # executing and processing
        response = self.container_action_exec(**data)

        if not response:
            raise ValueError("Error obteniendo el formulario de duplicado.")
        
        # data of response
        obj = response[0]
        return obj.get("dataObj")


    def get_element_def(self, container: str, elements: list, \
            _all: bool = False, read_only: bool = False, *args, **kwargs):
        """ Get all properties of an object/s. """

        # data prepare
        data = {
            "container": container,
            "elements": elements,
            "_all": _all,
            "action": "editForm" if not read_only else "View",
        }
        data.update(kwargs)

        # executing and processing
        response = self.container_action_exec(**data)

        elem_defs = []
        for elem in response:
            elem_defs.append(elem.get("dataObj"))

        return elem_defs

    def get_create_form(self, container: str, *args, **kwargs):
        """ Get default data for a new element. """
        
        # data prepare
        data = {
            "container": container,
            "elements": [-1],
        }

        # execute and process
        response = self.get_element_def(**data, **kwargs)

        if not response:
            raise ValueError("Error obteniendo formulario de creación")

        return response[0]

    def get_day_info(self, employee: int, \
            _from: str = datetime.date.today().isoformat(), \
            to: str = datetime.date.today().isoformat()):
        """ 
        Get info, days, shifts, and results for a employe in a specific period. 
        """

        # prepare task parameters
        params = {
            "idemp": employee,
            "from": _from,
            "to": to
        }

        # request.get -> json
        return self.get(path='/api/day/results', params=params)

    def get_access_clockings(self, employee: int, \
            _from: str = datetime.date.today().isoformat(), \
            to: str = datetime.date.today().isoformat()):
        """ Get access clockings for a employe in a specific period. """

        # prepare task parameters
        params = {
            "idemp": employee,
            "from": _from,
            "to": to
        }

        # request.get -> json
        return self.get(path='/api/access/clockings', params=params)

    def get_task_status(self, task: int):
        """ Get status of an async task. """

        # prepare task parameters
        params = {
            "taskid": task
        }

        # request.get -> json
        return self.get(path='/api/async/status', params=params)

    def get_task_response(self, task: int):
        """ Return the result of a async task. """

        # ensure the task is complete
        task_status = self.get_task_status(task)
        while not task_status.get("completed", False):
            task_status = self.get_task_status(task)

        # prepare task parameters
        params = {
            "taskid": task
        }

        # request.get -> json
        return self.get(path='/api/async/response', params=params)

    def get_results(self, employee: int, \
            _from: str = datetime.date.today().isoformat(), \
            to: str = datetime.date.today().isoformat()):
        """ Get results of day for a employee. """

        # prepare task parameters
        params = {
            'idemp': employee,
            'from': _from,
            'to': to,
        }

        # generate async task
        async_task = self.get(path='/api/results', params=params)

        # get task results
        return self.get_task_response(async_task.get('taskId'))

    def clocking_prepare(self, employee: int, date_time: datetime.datetime, \
            reader: int = -1, clocking_id: int = -1, action: str = None):
        """ Return a dict element with recived data. """

        # ensure datetime.datetime type
        if not isinstance(date_time, datetime.datetime):
            date_time = datetime.datetime.fromisoformat(date_time)

        # prepare structure
        clocking_data = {
            "id": clocking_id,
            "action": action,
            "app": True,
            "type": "timetypes",
            "date": date_time.isoformat(timespec='milliseconds'),
            "idReader": reader,
            "idElem": 0,
            "isNew": True if clocking_id == -1 else False,
        }

        return clocking_data
        
    def post_clocking(self, employee: int, date: str, time: str, \
            reader: int = -1, *args, **kwargs):
        """ Add a clocking to a employee in a specific date an time. """

        if self.user_rol == 'Persona':
            raise ValueError("Método no soportado para el tipo 'Persona'.")

        #teime process
        if not isinstance(date, datetime.date):
            date = datetime.date.fromisoformat(date)

        if not isinstance(date, datetime.time):
            time = datetime.datetime.strptime(time, "%H:%M").time()

        date_time = datetime.datetime.combine(date, time)

        json_data = {
            "idEmp": employee,
            "date": date.isoformat(),
            "clockings": [
                self.clocking_prepare(
                    employee=employee,
                    date_time=date_time,
                    reader=reader,
                    action=kwargs.get("action", None),
                    clocking_id=kwargs.get("clocking_id", -1)
                )
            ],
        }

        return self.post(path='/api/day/post/', json=json_data)

    def get_day_clockings(self, employee: int, \
            date: str = datetime.date.today().isoformat()):
        """
        Get all the clockings (Horario) of an employe in a specific day.
        ** This method use portal API.
        """

        # prepare task parameters
        params = {
            'path': '/api/clockings',
            'method': 'get',
            'idemp': employee,
            'date': date,
        }

        # generate async task
        async_tasK = self.get(path='/api/clockings', params=params) 

        # get and return task results
        return self.get_task_response(async_tasK.get('taskId'))

    def add_clocking(self, employee: int, date: str, time: str, \
            reader: int = -1):
        """ Add a clocking using post_clocking() method. """
        
        return self.post_clocking(employee=employee, date=date, time=time)

    def edit_clocking(self, employee: int, clocking_id: int, date: str, \
            time: str):
        """ Delete a clocking using post_clocking() method. """

        return self.post_clocking(
            employee=employee,
            date=date,
            time=time,
            clocking_id=clocking_id
        )

    def delete_clocking(self, employee: int, clocking_id: int, date: str, \
            time: str):
        """ Delete a clocking using post_clocking() method. """

        return self.post_clocking(
            employee=employee,
            date=date,
            time=time,
            action="Delete",
            clocking_id=clocking_id
        )

    def add_planning(self, employee: int, name: str, days: list, \
            allDay: bool = True, timetype: int = 0):
        """
        Create an absence planning for an employee on the indicated days using 
        the received timetype.
        """

        # getting form and update data
        planning = self.get_create_form("Persona", action="NewPlanificacion")
        planning.update({
            "name": name,
            "allDay": allDay,
            "allDayId": timetype,  # Timetype ID
            "employee": [employee],  # Employee ID
            "dateInterval": self.get_days_offset(days),
        })

        # prepare and save data
        data = {
            "container": "IncidenciaFutura",
            "dataObj": planning,
        }
        return self.save_element(**data)

    def add_activator(self, name: str, employees: list, days: list, \
            activator: int, value: int = None, comment: str = None):
        """
        Create an activator for an employee on the indicated days using \
        the received activator id.
        """

        new_activator = self.get_create_form(container="UsoActivadores")
        new_activator.update({
            "name": name,
            "multiname": {"es-ES": name},
            "activators": [{
                "activator": activator,
                "value": value,
            }],
            "comment": comment,
            "days": self.get_days_offset(days),
            "employees": employees,
        })

        # prepare and save data
        data = {
            "container": "UsoActivadores",
            "dataObj": new_activator,
        }
        return self.save_element(**data)

    def get_activity_monitor(self, employees: list, _from: str, to: str):
        """ Return the activity monitor structure. """
        
        # prepare task parameters
        json_data = {
            'clockings': True,
            'from': _from,
            'to': to,
            'ids': employees
        }

        # generate async task
        async_tasK = self.post(
            path='/api/planification/manager',
            json=json_data
        )

        # get and return task results
        return self.get_task_response(async_tasK.get('taskId'))

    def get_cube_results(self, dimensions: list, dateIni: str, dateEnd: str, \
            interFilters: list = [], filters: list = [], ids: list = []):
        """
        Gets nettime results using the "Results Query" window engine.

        :param dimensions: List of list where each one contains the desired 
            fields or results. The order of the values does matter.
        :param dateIni: Start day where you want to calculate.
        :param dateIni: End day where you want to calculate.
        :param interfilters: (Optional) If you use the dimension "system", 
            specify the ids of the results in this parameter.
        :param filters: (Optional) Nettime compatible filter expression.
        :param ids: (Optional) List of employee ids in case you want to filter.
        
        :return: :class:`list` object
        :rtype: json
        """

        # prepare task parameters
        json_data = {
            "container": "Persona",
            "dateIni": dateIni,
            "dateEnd": dateEnd,
            "ids": ids,
            "filters": filters,
            "dimensions": dimensions,
            "interFilters": interFilters,
        }

        # post and return response
        return self.post(path='/api/data/cube', json=json_data)

    def set_employee_calendar(self, employee: int, calendar: str):
        """ Get a calendar with name and assign to employee. """

        # searching employee
        emp = self.get_element_def("Persona", elements=[employee])
        if not emp:
            raise ValueError("No se encuentra el empleado.")

        # searching calendar
        query = Query(
            fields=["id", "name"],
            filterExp=f"this.name == '{calendar}'"
        )
        calendars = self.get_elements(container="Calendario", query=query)
        if not calendars.get('total'):
            raise ValueError("No se encuentra el calendario.")

        # processing calendars
        employee_calendar = emp[0].get("Calendar")
        employee_calendar["Calendars"] = calendars.get('items')
        
        # assign position
        for i in range(len(employee_calendar["Calendars"])):
            employee_calendar["Calendars"][i].update({"__elemPosition": i})

        # saving data
        data = {
            "container": "Persona",
            "elements": [employee],
            "dataObj": {
                "Calendar": employee_calendar
            }
        }

        return self.save_element(**data)

    def create_department_node(self, name: str, parent: int = -1, **kwargs):
        """ Create a new node in department structure. """

        # constant return if element exist
        EXIST_TEXT = "Ya existe un elemento con el mismo nombre descriptivo."

        # getting form
        node = self.get_create_form("Arbol")
        node['name'] = name
        node['idNodeParent'] = parent
        node['internalName'] = kwargs.get('internalName', None)

        # save new node
        new_elem = self.save_element(container="Arbol", dataObj=node)

        if new_elem[0].get('message') == EXIST_TEXT:
            return self.create_department_node(
                name=name,
                parent=parent,
                internalName=create_random_suffix(name),
            )
        
        # if couldn't be created
        if new_elem[0].get('type') != 6:
            raise RuntimeError(new_elem[0].get('message'))
        
        return new_elem

    def set_employee_department(self, employee: int, node_path: list, \
            auto_create: bool = True):
        """ Get a Department with list of names and assign to employee. """

        def make_filter(parent: int):
            # create dynamic function
            def node_filter(department):
                return department['idNodeParent'] == parent
            
            # return fynamic func
            return node_filter

        depto_id_rel = {}
        for i in range(len(node_path)):
            # get elements by name
            query = Query(
                fields=["id", "name", "idNodeParent"],
                filterExp=f"this.name = '{node_path[i]}'"
            )
            departs = self.get_elements(container="Arbol", query=query)

            # create dynamic filter
            filter_node = make_filter(depto_id_rel.get(node_path[i-1], -1))

            # filter elements
            search = list(filter(filter_node, departs.get('items')))

            if not search:
                # raise if not auto_create
                if not auto_create:
                    raise ValueError("Nodo no encontrado")

                # create node
                new_node = self.create_department_node(
                    name=node_path[i],
                    parent=depto_id_rel.get(node_path[i-1], -1)
                )

                # refresh search
                search = [new_node[0].get('dataObject')]
            
            # put result in rels
            depto_id_rel.update({node_path[i]: search[0].get('id')})

        # department structure
        object_assign = []
        if node_path:
            object_assign = [{'id': depto_id_rel.get(node_path[-1])}]

        # saving data
        data = {
            "container": "Persona",
            "elements": [employee],
            "dataObj": {
                "Departments": object_assign
            }
        }

        return self.save_element(**data)



        



