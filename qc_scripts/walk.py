"""
walk.py: Abstracted walk for all QCs
"""
import os
import re
from collections import defaultdict
from qc_scripts.utility.dates import get_date_string
from qc_scripts.utility.id_validation import get_pid
from qc_scripts.utility.errors import on_error

def default_make_kv(__, data, **_):
    """
    default kv for walk
    """ 
    return data[0], {}

def match_filename_format(_, data, **kwargs):
    """
    Matches filename pattern data and extract 
    fid, id_date, date, full_path
    something_<idtype>_<id>_<date>_<tech_id>_optional.ext
    """
    pattern_data = kwargs.get('pattern_data')
    keep_exts = tuple((s.lower() for s in kwargs.get('keep_exts')))
    full_path = data
    filename = os.path.basename(full_path)
    if not filename.lower().endswith(keep_exts):
        return None, ('unwanted_ext', full_path)
    value = match_pattern_data(filename.lower(), pattern_data)
    if value == {}:
        return None, ('no_match', full_path)
    pid = get_pid(value)
    try:
        date = get_date_string(value['date'])
        id_date = f"{pid}_{date}"
        value.update({'pid': pid, 'id_date': id_date, 'date': date, 'src': full_path})
        return id_date, value
    except ValueError:
        return None, ('invalid_date', full_path)
    

def match_pattern_data(string, pattern_data):
    """
    find pattern data match;
    """
    value = {}
    pattern_data = [(re.compile(p), i) for p, i in pattern_data]
    for compiled, indices in pattern_data:
        search = compiled.search(string)
        if search is None:
            continue
        groups = search.groups()
        for idx, key in indices:
            value[key] = groups[idx]
        ## stop once we match one pattern
        return value
    return value

def qc_walk(**kwargs):
    """
    Walks a given root and creates key value pairs based on the make_kv function provided.
    """
    roots = kwargs.get('roots')
    ignore_list = kwargs.get('ignore_list', [])
    keep_exts = kwargs.get('keep_exts', None)
    pattern_list = kwargs.get('pattern_list', None)
    make_kv = kwargs.get('make_kv', match_filename_format)
    make_kv_kw = kwargs.get('make_kv_kw', {})
    ext = kwargs.get('ext', 'walk')
    multiple_values = kwargs.get('multiple_values', True)

    make_kv_kw.update({'keep_exts': keep_exts})
    if pattern_list:
        make_kv_kw.update({'pattern_data': pattern_list})

    final = defaultdict(list) if multiple_values else {}
    other = defaultdict(list)

    for root in roots:
        for data in full_file_gen(root, ignore_list=ignore_list):
            key, value = make_kv(root, data, **make_kv_kw)
            # if no key is returned, the key and value will be the same.
            if key is None:
                nkey, nval = value
                other[nkey].append(nval)
            else:
                ## Allows for keys to have multiple values
                if multiple_values:
                    final[key].append(value)
                ## Otherwise keys may only have one value
                else:
                    assert key not in final, key
                    final[key] = value

    return [{'final': final, 'ext': ext}, {'final': other, 'ext': f'other_{ext}'}]

def full_file_gen(root, onerror=on_error, topdown=True, ignore_list=[]):
    """
    Walks a directory and yields the full file paths.
    """
    for dirpath, dirnames, filenames in os.walk(root, onerror=onerror, topdown=topdown):
        if ignore_list != []:
            dirnames[:] = [directory for directory in dirnames if directory.split(os.sep)[-1]\
                    not in ignore_list]
        for file in filenames:
            yield os.path.join(dirpath, file).replace(os.sep, os.altsep)