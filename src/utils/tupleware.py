from collections import namedtuple, OrderedDict
import functools

__author__ = 'github.com/hangtwenty'

def tupleware(obj):
    """ Convert mappings to 'tuplewares' recursively.
    Lets you use dicts like they're JavaScript Object Literals (~=JSON)...
    It recursively turns mappings (dictionaries) into namedtuples.
    Thus, you can cheaply create an object whose attributes are accessible
    by dotted notation (all the way down).
    Use cases:
        * Fake objects (useful for dependency injection when you're making
         fakes/stubs that are simpler than proper mocks)
        * Storing data (like fixtures) in a structured way, in Python code
        (data whose initial definition reads nicely like JSON). You could do
        this with dictionaries, but namedtuples are immutable, and their
        dotted notation can be clearer in some contexts.
    .. doctest::
        >>> t = tupleware({
        ...     'foo': 'bar',
        ...     'baz': {'qux': 'quux'},
        ...     'tito': {
        ...             'tata': 'tutu',
        ...             'totoro': 'tots',
        ...             'frobnicator': ['this', 'is', 'not', 'a', 'mapping']
        ...     }
        ... })
        >>> t # doctest: +ELLIPSIS
        NamedTupleWare(
            tito=NamedTupleWare(...),
            foo='bar',
            baz=NamedTupleWare(qux='quux')
        )
        >>> t.tito # doctest: +ELLIPSIS
        NamedTupleWare(frobnicator=[...], tata='tutu', totoro='tots')
        >>> t.tito.tata
        'tutu'
        >>> t.tito.frobnicator
        ['this', 'is', 'not', 'a', 'mapping']
        >>> t.foo
        'bar'
        >>> t.baz.qux
        'quux'
    Args:
        mapping: An object that might be a mapping. If it's a mapping, convert
        it (and all of its contents that are mappings) to namedtuples
        (called 'NamedTupleWares').
    Returns:
        A tupleware (a namedtuple (of namedtuples (of namedtuples (...)))).
        If argument is not a mapping, it just returns it (this enables the
        recursion).
    """

    if isinstance(obj, dict):
        fields = sorted(obj.keys())
        namedtuple_type = namedtuple(
            typename='NamedTupleWare',
            field_names=fields,
            rename=True,
        )
        field_value_pairs = OrderedDict(
            (str(field), tupleware(obj[field])) for field in fields
        )
        try:
            return namedtuple_type(**field_value_pairs)
        except TypeError:
            # Cannot create namedtuple instance so fallback to dict
            # (invalid attribute names)
            return dict(**field_value_pairs)
    elif isinstance(obj, (list, set, tuple, frozenset)):
        return [tupleware(item) for item in obj]
    else:
        return obj

def to_dict(tupleware):
    """ Convert a tupleware (NamedTupleWare) -or list of- to dict. """

    if isinstance(tupleware, list):
        # if list of tupleware, returns list of dict
        return [to_dict(element) for element in tupleware]
    else:
        dict_element = {}
        # get fields of object
        for field in tupleware._fields:
            # get value of attr
            value = getattr(tupleware, field)
            # if value is a NamedTupleWare class, convert again
            if value.__class__.__name__ == tupleware.__class__.__name__:
                value = to_dict(value)
            
            # insert k,v in dictionary
            dict_element.update({field: value})

        # return dictionary
        return dict_element
