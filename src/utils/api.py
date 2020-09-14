import json
from re import split as re_split

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

            
