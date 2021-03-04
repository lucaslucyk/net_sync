# -*- coding: utf-8 -*-

### built-in ###
import json
import datetime as dt

### django ###
# ...

### own ###
from utils import processors as procs

class NetTimeResult:
    """ Class to process formats from nettime result value. """

    def __init__(self, value):
        self.value = value

    @property
    def _timedelta(self):
        """ Return python datetime.timedelta object. """

        return dt.timedelta(minutes=self.value)

    @property
    def hours(self):
        """ Return the number of hours assuming that is a time format. """

        return int(self.value // 60)

    @property
    def minutes(self):
        """ Return the number of minutes assuming that is a time format. """

        return int(self.value)

    @property
    def seconds(self):
        """ Return the number of seconds assuming that is a time format. """

        return int(self.value * 60)

    @property
    def centesimal_time(self):
        """ Return time centesimal format assuming that is a time format. """

        dif = self.minutes - self.hours * 60
        return float('{:.2f}'.format(self.hours + dif / 60))

    def __repr__(self):
        return '{}(value={})'.format(self.__class__.__name__, self.value)

    def __bool__(self):
        return bool(self.value)

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


def apply_fields_def(structure: list, fields_def: list):
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

def ntRes_to_vismaPayments(self, syncs: list, sync_cfgs: dict, **kwargs):
    """
    Prepare visma payments request from nettime results.

    @@ Parameters
    @syncs (list):
        List of sync results from nettime (self.get_nt6_result_syncs).
    @sync_cfgs (dict):
        Dict with config to apply to syncs. Must include sync_type,
        employee_field, and concepts dict. Check docs for +info.

    @@ Returns
    @list: List of payment elements to send to Visma.
    """

    # out structure
    all_payments = []

    # all syncs recived
    for _sync in syncs:
        # all data* elements
        for elem in _sync.get('data'):
            # all concepts of config
            for concept, cfg in sync_cfgs.get(
                    _sync.get('sync_type')).get('concepts').items():

                # total value of current concept
                ntv = elem.get('totals').get(cfg.get('result'))

                # ignore next steps if is 0
                if not ntv and cfg.get('zero_ignore', True):
                    continue

                # if ntv != 0
                structure = {
                    "employeeExternalId": elem.get('employee').get(
                        sync_cfgs.get(
                            _sync.get('sync_type')
                        ).get('employee_field', 'employeeCode')
                    ),
                    "periodFrom": _sync.get('from'),
                    "periodTo": _sync.get('from'),
                    "reason": "",
                    "reasonTypeExternalId": "",
                    "action": 0,
                    "retroactive": False,
                    # "journalModelId": 0,
                    # "journalModelStructureId1": 0,
                    # "journalModelStructureId2": 0,
                    # "journalModelStructureId3": 0,
                    "conceptExternalId": concept,
                    "parameterId": cfg.get('parameter', 3),
                    #"dateFrom": "",
                    #"dateTo": "",
                    "value": getattr(
                        NetTimeResult(value=ntv),
                        cfg.get('property', 'centesimal_time')
                    )
                }

                # append structure to out elements
                all_payments.append(structure)

    # return structure
    return all_payments
