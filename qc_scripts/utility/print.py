"""
print.py
Methods to help with formating prints
"""

import json

def pprint_dict(data, **kwargs):
    """
    parameters:
        data(dictionary): dictionary to be pretty-printed
        **kwargs(key-word-args, dictionary): key word args to be
            passed to json.dumps
    """
    indent = kwargs.pop('indent', 4)
    sort_keys = kwargs.pop('sort_keys', True)
    do_print = kwargs.pop('do_print', True)
    default = kwargs.pop('default', None)
    if kwargs != {}:
        print(">>> Warning! kwargs contains unused args")
        print(kwargs)
        print(">>>")
    string = json.dumps(data, indent=indent, default=default, sort_keys=sort_keys)
    if do_print:
        print(string)
    return string