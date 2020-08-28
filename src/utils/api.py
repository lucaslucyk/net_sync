
class FieldDefinition:

    def __init__(self, out_name, in_name, steps):
        self.out_name = out_name
        self.in_name = in_name
        self.steps = [self.Step(*step) for step in steps]

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
    def parse_str(cls, string: str):
        field_dest, field_def = string.split("@")
        orig_steps = field_def.split("|")
        field_orig = orig_steps[0]
        steps = []

        if len(orig_steps) > 1:
            steps = orig_steps[1:]

        mapping = []
        for step in steps:
            mapping.append(step.split(':'))

        return cls(field_dest, field_orig, mapping)

    class Step:
        def __init__(self, method: str, parameters: str = None):
            self.method = method
            self.parameters = parameters

        def __str__(self):
            return repr(self)

        def __repr__(self):
            return '{}(method="{}", parameters="{}")'.format(
                self.__class__.__name__,
                self.method,
                self.parameters
            )
