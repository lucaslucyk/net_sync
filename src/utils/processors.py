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


def get_gender_acronym(obj: str):
    """ Return M of F depending if male or female recived. """

    # convert to lower for safety
    gender = obj.lower()

    # evaluate for next features
    if gender == "female":
        return "F"

    # default value
    return "M"
        
