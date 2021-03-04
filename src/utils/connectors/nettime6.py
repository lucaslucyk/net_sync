### built-in ###
from dateutil.parser import parse
import datetime as dt

### own ###
from utils import api

### third ###
from spec_utils import nettime6 as nt6


class Client:

    def __init__(self, source, last_run: dt.datetime, **kwargs):
        """
        Create a NetTime 6 API client.
        
        @@ Parameters
        @source (Sync): Must be a Sync instance.
        """

        self.name = "NetTime 6 API"
        self.source = source
        self.last_run = last_run

        # connection params
        params = source.credentialparameter_set.all()
        self.url = params.filter(key='host').first().value
        self.username = params.filter(key='user').first().value
        self.pwd = params.filter(key='password').first().value

        self.extra_parameters = kwargs

    def open_connection(self, **kwargs):
        """ Open and return a NetTime 6 API Client. """

        return nt6.Client(
            url=self.url,
            username=self.username,
            pwd=self.pwd,
            **self.extra_parameters,
            **kwargs
        )

    def get_employees(self, fields: list, _from: str = None, \
            filterExp: str = None) -> list:
        """
        Get employees from nettime with spec_utils.nettime6 module.
        
        @@ Parameters
        @fields (list):
            List of api.FieldDefinition elements.
        @_from (str):
            Optional string with datetime format (YYYYMMDDhhmmss) to filter 
            employees. Last Run by default
        @filterExp (str):
            Nettime compliant filter expression. None by default.

        @@ Returns
        @list: list of elements obtained from nettime and processed with the 
            "fields" parameter.
        """

        # getting last run or default value
        date_start = self.last_run

        # with recived values
        if _from:
            date_start = dt.datetime.strptime(_from, "%Y%m%d%H%M%S")

        # open api connection with auto-disconnect
        with self.open_connection() as client:

            # add expression for ignore old syncs (this.modified >= lastSync)
            query = nt6.Query(
                fields=[f.get('origin') for f in fields],
                filterExp='{}(this.modified >= "{}")'.format(
                    f'({filterExp}) && ' if filterExp else '',
                    date_start.strftime("%Y-%m-%d %H:%M:%S")
                )
            )

            # get employees
            nt_response = client.get_employees(query=query)

        return api.apply_fields_def(
            structure=nt_response.get('items', []),
            fields_def=[api.FieldDefinition.from_json(f) for f in fields]
        )

    def get_result_syncs(self, results: list = [], \
            employee_fields: list = [], per_day: bool = True, \
            named_totals: bool = True, to_dict: bool = True, \
            dict_type: str = 'dict' , transpose: bool = True, \
            sync_container: str = 'Custom', sync_fields: list = [], \
            sync_filterExp: str = '', from_view: bool = False, **kwargs):
        """
        Get cube results with Custom config from nettime with 
        spec_utils.nettime6 module.
        
        @@ Parameters
        @results (list):
            List of results to get. Eg.
            [
                "ResultValue_A.Value.Saldo_Franco_Compensatorio",
                "ResultValue_A.Value.EXTRAS_50",
                "ResultValue_A.Value.Hs_Extras_50_Aprob",
                "ResultValue_A.Value.Hs_EXTRAS_50_Aprob_SAB",
                "ResultValue_A.Value.EXTRAS_100",
                "ResultValue_A.Value.Hs_Extras_100_Aprob",
                "ResultValue_A.Value.HS_EXTRAS_100_Aprob_SAB"
            ]
        @employee_fields (list):
            List of fields to get from employee. Eg.
            ["id", "employeeCode", "Apellidos_Nombre"],
        @per_day (bool) = True:
            Use to get day by day results, otherwise only totals will be geted.
        @named_totals (bool) = True:
            Use to get name of results in totals context.
        @transpose (bool) = True:
            Use to swap rows and columns of pandas DataFrame.
        @to_dict (bool) = True:
            Use to transform pandas DataFrame to dict.
        @dict_type (str) = 'dict':
            Param to pass to DataFrame.to_dict().
        @sync_container (str) = 'Custom':
            Name of container with data.
        @sync_fields (list):
            List of fields to get elements from container. Default:
            [
                "id",
                "name",
                "nsDateFrom", "nsDateTo",
                "nsDateZImp",
                "nsFilter",
                "nsSynchronized"
            ]
        @sync_filterExp (str):
            Filter to get elements from container. Default:
            '(this.type="net_sync" && this.nsSynchronized=false)'
        @from_view (bool) = False:
            Use this to not configure the results fields and employee_fields, 
            but you need to set a view in nettime custom sync.
            ** IMPORTANT: The view must be created in NetTime v6.
        @**kwargs (*dict):
            Extra parameters to pass to method get_cube_results.
        
        @@ Returns
        @list: list of elements obtained from nettime and processed with the 
            "fields" parameter.
        """

        def get_dimensions(view: dict):
            """ Get employee fields and reults from a results view. """

            # if can't get view
            if not isinstance(view, dict) or "fields" not in view.keys():
                return

            # filter and return employee fields and results
            _employee_f = list(filter(
                lambda d: d['view'] == 'employee',
                view.get('fields')
            ))
            _results_f = list(filter(
                lambda d: d['view'] == 'results',
                view.get('fields')
            ))

            # return names how list
            return {
                "_emp_fields": [ef.get('name') for ef in _employee_f],
                "_results_fields": [rf.get('name') for rf in _results_f]
            }

        def get_filters(view: dict):
            """ Get filters structure from a results view. """

            # if can't get view
            if not isinstance(view, dict) or "sysFilters" not in view.keys():
                return []

            # out prepare
            out_filters = []
            
            # filter proccess
            for _filter in view.get('sysFilters').split(";"):
                # split data
                spplited = _filter.split('|')

                # structure with data
                out_filters.append({
                    "id": spplited[0],
                    "op": spplited[1],
                    "name": spplited[2],
                    "system": spplited[3]
                })

            # return all filters
            return out_filters

        # list of all elements to return
        all_elements = []

        ### prepare to the nettime syncs that need to run.
        # filter expression
        if not sync_filterExp:
            sync_filterExp = '({} && {})'.format(
                'this.type="net_sync"',
                'this.nsSynchronized=false'
            )
        
        # fields to get
        if not sync_fields:
            sync_fields = [
                "id",
                "name",
                "type",
                "nsDateFrom",
                "nsDateTo",
                "nsDateZImp",
                "nsFilter",
                "nsSynchronized",
                "nsFieldView"
            ]

        # query prepare
        query = nt6.Query(fields=sync_fields, filterExp=sync_filterExp)

        # open api connection with auto-disconnect
        with self.open_connection() as client:

            # get need syncs
            need_syncs = client.get_elements(
                container=sync_container,
                query=query
            )

            ### no syncs to run
            if not need_syncs.get('total'):
                return {}

            # syncs to run exist
            for sync in need_syncs.get('items'):
                
                # query prepare
                params = {}
                params.update({
                    "dateIni": parse(sync.get('nsDateFrom')).date().isoformat(),
                    "dateEnd": parse(sync.get('nsDateTo')).date().isoformat(),
                })

                # if filter was selected
                if "nsFilter" in sync.keys():
                    params["filters"] = [{
                        "id": sync.get('nsFilter'),
                        "op": "AND"
                    }]

                # dims prepare
                dims = {
                    "_emp_fields": employee_fields,
                    "_results_fields": results
                }

                # get dimensions from view or params
                if from_view:
                    # get field_view definition
                    view = client.get_element_def(
                        container="FieldView",
                        elements=[sync.get('nsFieldView')]
                    )

                    # update filters
                    params["filters"] = get_filters(view=view[0])

                    # get dimensions
                    _nt_dims = get_dimensions(view=view[0])

                    # update if can get values
                    dims = _nt_dims if _nt_dims else dims

                # update vars with params or view values
                _ef = employee_fields or dims.get('_emp_fields')
                _rf = results or dims.get('_results_fields')
                
                # update params
                params["dimensions"] = [_ef, _rf]

                # only if per_day is specified
                if per_day:
                    params.get("dimensions").append(["date"])

                # get results
                cube_results = client.get_cube_results(**params, **kwargs)

                # out data
                out_data = []

                # process nettime response
                for result in cube_results:
                    # initial structure
                    structure = {"employee": {}}
                    
                    # to size reduce
                    if named_totals:
                        structure["totals"] = dict(zip(
                            _rf,
                            result.get("values")
                        ))
                    else:
                        structure["totals"] = result.get("values")
                    
                    # update person fields
                    for i in range(len(_ef)):
                        structure.get("employee").update({
                            _ef[i]: result.get("dimKey")[i]
                        })

                    # if results per date -or month-
                    if 'children' in result.keys():
                        structure["frame"] = pd.DataFrame(
                            [c.get("values") for c in result.get("children")],
                            columns=_rf,
                            index=[c.get("dimKey")[0] \
                                for c in result.get("children")]
                        )
                        # swap rows and columns
                        if transpose:
                            structure["frame"] = structure.get("frame").T
                            
                        # convert dataframe to dict
                        if to_dict:
                            structure["frame"] = structure.get(
                                "frame").to_dict(dict_type)

                    # append structure
                    out_data.append(structure)

                # append data to output list
                all_elements.append({
                    "sync_id": sync.get("id"),
                    "sync_name": sync.get("name"),
                    "sync_type": sync.get("type"),
                    "from": params.get("dateIni"),
                    "to": params.get("dateEnd"),
                    "data": out_data
                })

                # update synchronized property
                sync["nsSynchronized"] = True
                response = client.save_element(
                    container="Custom",
                    elements=[sync.get('id')],
                    dataObj=sync
                )

        # return all structures
        return all_elements

    def post_employees(self, employees: list, fields: list, **kwargs):
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
        employees = api.apply_fields_def(
            structure=employees,
            fields_def=[api.FieldDefinition.from_json(f) for f in fields]
        )

        # open api connection with auto-disconnect
        with self.open_connection() as client:
            # import employees one by one
            for employee in employees:
                response = client.import_employee(structure=employee)

        # return true for general propose
        return True

    def post_departments(self, structure: list, fields: list, \
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
        structure = api.apply_fields_def(
            structure=structure,
            fields_def=[api.FieldDefinition.from_json(f) for f in fields]
        )

        # open api connection with auto-disconnect
        with self.open_connection() as client:

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

