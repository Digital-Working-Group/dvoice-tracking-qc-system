"""
log_helper.py
methods to simplify logging
"""

def add_readables_to_kwargs(readables, kwarg_dict, read_function, **kwargs):
    """
    read a dictionary from readables once and pass it to
    a kwargs dictionary. this is an alternative to passing
    a dictionary directly to kwargs, in order to save on logging space,
    since we log arguments and kwargs. this way we only need to log
    the path from a json, rather than the entire dict contents

    parameters:
        readables(dict): k=key, v=path_to_json
        kwarg_dict(dict): dict being used as kwargs.
    output:
        kwargs[key] = read_function(path_to_json)
    """
    read_function_kw = kwargs.get('read_function_kw', {})
    for key, readable_json in readables.items():
        kwarg_dict[key] = read_function(readable_json, **read_function_kw)

def truncate_max_length(data, **kwargs):
    """
    20250529
    Stops logging over a certain maximum length
    """ 

    for key, value in data.items():
        max_lengths = kwargs.get('max_iterable_length_allowed', {dict: 250, list: 250, tuple: 250})
        max_len = next((length for typ, length in max_lengths.items() if isinstance(value, typ)), None)
        value_len = count_all_items(value)
        if max_len is not None and value_len >= max_len:
            data[key] = {
                '_exceeded_max_length_to_log': {
                    'max_length_allowed': max_len,
                    'length_of_data': value_len
                }
            }
        else:
            data[key] = value
    return data

def count_all_items(obj):
    """
    recursively count all items in a dictionary, list, tuple, or set
    """ 
    if isinstance(obj, dict):
        return sum(count_all_items(v) for v in obj.values()) + len(obj)
    elif isinstance(obj, (list, tuple, set)):
        return sum(count_all_items(v) for v in obj)
    else:
        return 1
    
def len_dict_list_values(dictionary):
    """
    if a dictionary has lists for values, get the
    length of all the values
    """ 
    if isinstance(dictionary, list):
        return len(dictionary)
    if len(dictionary) == 0:
        return None
    first_value = next(iter(dictionary.values()))
    if isinstance(first_value, list):
        return sum([len(v) for _, v in dictionary.items()])
    return None