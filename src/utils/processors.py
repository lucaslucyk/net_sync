from dateutil.parser import parse

def get_from_dict(obj: dict, key: str):
    """ Extract a key from a dictionary. None by default."""

    return obj.get(key, None)

def get_from_list(obj: list, element: str = "__all__"):
    """ 
    Extract an element from a list. Can use a number or global values:
        - __all__
        - __first__
        - __last__
    """

    translate = {
        "__all__": obj,
        "__first__": obj[0],
        "__last__": obj[-1]
    }

    try:
        # if contain an expression
        if element in translate.keys():
            return translate.get(element)

        # if is numeric position
        return obj[element]
    
    except:
        return None

def split(obj: str, sep: str = None, maxsplit: int = -1) -> list:
    """
    Return a list of the words in the string, using sep as the delimiter string.

    @@ Parameters
    @obj (str):
        String to split.
    @sep (str):
        The delimiter according which to split the string.
        None (default value) means split according to any whitespace,
        and discard empty strings from the result.
    @maxsplit (int):
        Maximum number of splits to do.
        -1 (the default value) means no limit.

    @@ Returns
    @list: List of str splitted by sep* parameter.
    """

    return obj.split(sep=sep, maxsplit=maxsplit)

def get_gender_acronym(obj: str) -> str:
    """ Return M of F depending if male or female recived. """

    # convert to lower for safety
    gender = obj.lower()

    # evaluate for next features
    if gender == "female":
        return "F"

    # default value
    return "M"
        
def time_format(obj: str, fmt: str, **kwargs) -> str:
    """
    Converts a string to a date and returns it in the format indicated by the 
    fmt* parameter.
    
    @@ Parameters
    @fmt (str):
        Compatible string with datetime.strftime behavior.
        More info in:
        https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    @**kwargs:
        Parameters to format string to date.
        These will be passed to the dateutil.parser.parse method.
        More info in:
        https://dateutil.readthedocs.io/en/stable/parser.html

    @@ Returns
    @str: String with formatted date.
    """

    # parse str to datetime object
    py_dt = parse(obj, **kwargs)

    # format and return
    return py_dt.strftime(fmt)

def replace(obj: str, old: str, new: str):
    """ Replace the old str with new str in obj. """

    # replace and return
    return obj.replace(old, new)


def extract(obj, end: int = None, start: int = None, step: int = None):
    """
    Extract elements of an iterable from start to end (not including it) with 
    the indicated step.
    If it does not receive parameters, returns the same object.
    """

    # for safety
    if end > len(obj):
        end = len(obj)

    # process and return
    return obj[start:end:step]
