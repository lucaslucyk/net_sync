# -*- coding: utf-8 -*-

### built-in ###
from dateutil.parser import parse
import datetime as dt
import functools
import operator

### django ###
# ...
### own ###
from . import tupleware

### third ###
from unidecode import unidecode

def set_value(obj: dict, value):
    """ Return a value to set in a like structure. """
    return value

def rget(obj: dict, key: str, *args):
    """ Recursive get() with obj.get(key, *args) path. """
    def _get(obj, key):
        return obj.get(key, *args)
    return functools.reduce(_get, [obj] + key.split('.'))

def rgetattr(obj, attr, *args):
    """ Recursive getattr() with obj.attr path. """
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)
    return functools.reduce(_getattr, [obj] + attr.split('.'))


def rsetattr(obj, attr, val):
    """ Recursive setattr() with obj.attr path. """
    pre, _, post = attr.rpartition('.')
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)


def filter_json(obj: list, attribute: str, value, operation: str = 'eq',
    negative: bool = False, exclude: bool = False, *args, **kwargs):
    """
    Filters the elements of the list that match the indicated operation.
    More info in:
    https://docs.python.org/3/library/operator.html#mapping-operators-to-functions

    @@ Parameters
    @obj (list):
        Element to process.
    @attribute (str):
        Path to element to apply operation* and compare with value*.
    @value (any):
        Value to compare with attribute selected.
    @operation (str):
        Operation to get from operator module. 'eq' by default (==).
    @negative (bool):
        Inform if you want to deny the comparison.
    @excluce (bool):
        Informs if you want to exclude the matching elements
        (it includes them by default eliminating those that do not match)
    @\*args:
        Elements to pass to the selected operator.
    @\*\*kwargs:
        KW Elements to pass to the selected operator.
    """

    # list of dict to list of NamedTupleWare
    #objects = tupleware.tupleware(obj)

    # method of operator to execute.
    # 'eq' by default
    method = getattr(operator, operation)

    # out elements
    elements = []

    #for element in objects:
    for element in obj:
        # get attr value and execute method of operator
        # res = method(
        #     rgetattr(element, attribute, None), value, *args, **kwargs)
        res = method(rget(element, attribute, None), value, *args, **kwargs)
        
        # negate if recives 'negative' parameter
        if negative:
            res = not res

        if res:
            # if not exclude, append element to out elements
            elements.append(element) if not exclude else None
        else:
            # if operator don't match but must exclude matches,
            # append element to out elements
            elements.append(element) if exclude else None

    # return elements
    #return tupleware.to_dict(elements)
    return elements


def get_from_dict(obj: dict, key: str):
    """ Extract a key from a dictionary. None by default."""

    return obj.get(key, None)


def get_from_list(obj: list, element: str = "__all__"):
    """ 
    Extract an element from a list. Can use a number or global values:

    @@ Parameters
    @obj (list):
        Element to process.
    @element (str or int):
        Element to extract. The value can be str (name) or int (position).
        Possible str values:
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


def to_datetime(obj: str, fmt: str, **kwargs) -> dt.datetime:
    """
    Converts a string to a datetime using format indicated by the 
    fmt* parameter.
    
    @@ Parameters
    @fmt (str):
        Compatible string with datetime.strftime behavior.
        More info in:
        https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior

    @@ Returns
    @dt.datetime: Datetime from str with fmt format.
    """

    # format and return
    return dt.datetime.strptime(obj, fmt)


def replace(obj: str, old: str, new: str):
    """ Replace the old str with new str in obj. """

    # replace and return
    return obj.replace(old, new)


def extract(obj, end: int = None, start: int = None, step: int = None):
    """
    Extract elements of an iterable from start to end (not including it) with 
    the indicated step.
    If it does not receive parameters, returns the same object.

    @@ Parameters
    @obj (iterable):
        Iterable to process.
    @end (int):
        Last element to get of iterable (not including).
    @start (int):
        First element to get of iterable (including).
    @step (int):
        Step to get the values. Use -1 to reverse.

    @@ Returns
    @iterable: Iterable processed with recived values.
    """

    # for safety
    if end > len(obj):
        end = len(obj)

    # process and return
    return obj[start:end:step]

def to_ascii(obj):
    """
    Remove characters non ascii from a word, replacing for match ascii.
    """

    return unidecode(obj)

def str_method(obj, method: str):
    """
    Apply a method to obj (str).
    """

    func = getattr(obj, method, None)
    
    if not func:
        return None
    
    return func()

def str_attr(obj, attr: str):
    """
    Get a attribute of str.
    """

    return getattr(obj, attr, None)

def date_to_ActiveDays(obj, is_active: bool = True):
    """
    Convert a str date to ActiveDays structure for nettime.
    """
    _obj = obj
    if _obj.__class__.__name__ not in ["datetime", "date"]:
        _obj = parse(_obj)

    return {
        "validity": [{
            "start": _obj.date().isoformat(),
            "end": "{}T00:00:00-03:00".format(
                "2040-12-31" if is_active else dt.date.today().isoformat()
            )
        }]
    }
