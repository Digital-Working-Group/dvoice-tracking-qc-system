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
    full_path, _, _, _ = data
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
    KWARGS:
        roots (list): roots to walk
        ext (str): file extention, optional
        ignore_list (list): dirs/files to ignore, optional
        keep_exts (tuple): file extentions to pass walk
        pattern_list (list): look for this pattern in the filename, optional
        walk_files_func (func): default is full_file_gen
        make_kv (func): how to create the key-value pairs in the result
        walk_kwargs (dict): additional kwargs to be passed in to qc_scripts.utility.walk
    """
    ## kwargs
    roots = kwargs.get('roots')
    ignore_list = kwargs.get('ignore_list', [])
    keep_exts = kwargs.get('keep_exts', '')
    pattern_list = kwargs.get('pattern_list', None)
    walk_files_func = kwargs.get('walk_files_func', full_file_gen)
    data_func = kwargs.get('data_func', None)
    make_kv = kwargs.get('make_kv', default_make_kv)
    walk_kwargs = kwargs.get('walk_kwargs', {'ext': 'walk'})


    walk_results = []
    walk_files_kw = {'ignore_list': ignore_list}
    if data_func:
        walk_files_kw.update({'func': data_func})
    make_kv_kw = {'keep_exts': keep_exts}
    if pattern_list:
        make_kv_kw.update({'pattern_data': pattern_list})
    walk_data = {'walk_func': walk_files_func, 'walk_func_kw': walk_files_kw,
        'make_kv': make_kv, 'make_kv_kw': make_kv_kw}
    root_dict = {}
    for root in roots:
        root_dict[root] = walk_data
    walk_results = walk(root_dict, **walk_kwargs)

    return walk_results

def walk(root_dict, **kwargs):
    """
    root_dict(list[str: dict]): keys=roots, values=dict with walk function info;
    """
    multiple_values = kwargs.get('multiple_values', False)
    ignore_others = kwargs.get('ignore_others', False)
    ext = kwargs.get('ext', '')
    final = defaultdict(list) if multiple_values else {}
    other = defaultdict(list)
    for root, root_data in root_dict.items():
        walk_func = root_data.get('walk_func')
        walk_func_kw = root_data.get('walk_func_kw', {})
        make_kv = root_data.get('make_kv')
        make_kv_kw = root_data.get('make_kv_kw', {})
        for data in walk_func(root, **walk_func_kw):
            key, value = make_kv(root, data, **make_kv_kw)
            if key is None:
                if not ignore_others:
                    nkey, nval = value
                    other[nkey].append(nval)
            else:
                if multiple_values:
                    final[key].append(value)
                else:
                    assert key not in final, key
                    final[key] = value
    return [{'final': final, 'ext': ext}, {'final': other, 'ext': f'other_{ext}'}]

def full_file_gen(root, onerror=on_error, topdown=True, funct=None, **kwargs):
    """
    same as file_gen, but includes dirnames as well;
    """
    ignore_list = kwargs.pop("_ignore_list", [])
    ignore_list = kwargs.pop("ignore_list", ignore_list)
    keep_exts = kwargs.pop('_keep_exts', None)
    keep_exts = kwargs.pop('keep_exts', keep_exts)
    conv_to_altsep = kwargs.pop('conv_to_altsep', False)
    if keep_exts is not None:
        keep_exts = tuple((s.lower() for s in keep_exts))
    for dirpath, dirnames, filenames in os.walk(root, onerror=onerror, topdown=topdown):
        if ignore_list != []:
            dirnames[:] = [directory for directory in dirnames if directory.split(os.sep)[-1]\
                    not in ignore_list]
        for file in filenames:
            if keep_exts is not None:
                if not file.lower().endswith(keep_exts):
                    continue
            full_path = os.path.join(dirpath, file)
            if conv_to_altsep:
                dirpath = dirpath.replace(os.sep, os.altsep)
                file = file.replace(os.sep, os.altsep)
                dirnames = [d.replace(os.sep, os.altsep) for d in dirnames]
                full_path = full_path.replace(os.sep, os.altsep)
            if funct is not None:
                yield funct((full_path, dirpath, dirnames, file), **kwargs)
            else:
                yield (full_path, dirpath, dirnames, file)