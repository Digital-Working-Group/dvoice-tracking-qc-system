"""
move_file.py
"""
import os
import shutil
import subprocess
from tqdm import tqdm
from collections import defaultdict
from qc_scripts.utility.read import read_dictionary_file
from qc_scripts.utility.yield_data import yield_data
from qc_scripts.utility.log_helper import add_readables_to_kwargs

def shutil_move(src, dst, **kwargs):
    src_exists = os.path.isfile(src)
    dst_exists = os.path.isfile(dst)
    do_make_parent = kwargs.get('do_make_parent', True)
    if do_make_parent:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
    if src_exists == True:
        shutil.move(src, dst)
    status = gen_status(src_exists, dst_exists)
    return status, src_exists, dst_exists

def linux_copy(src, dst, **kwargs):
    """
    copy using cp;
    """
    command = f'cp "{src}" "{dst}"'
    return subprocess_copy(src, dst, command, **kwargs)

def linux_move(src, dst, **kwargs):
    """
    move file using mv;
    uses shutil if filename is changing
    """
    if os.path.basename(src) != os.path.basename(dst):
        return shutil_move(src, dst, **kwargs)
    command = f'mv "{src}" "{dst}"'
    return subprocess_copy(src, dst, command, **kwargs)

def windows_copy(src, dst, **kwargs):
    """
    copy using subprocess windows command;
    """
    src_par = os.path.dirname(src)
    dst_par = os.path.dirname(dst)
    fname = os.path.basename(dst)
    command = f'robocopy "{src_par}" "{dst_par}" "{fname}" /mt'
    return subprocess_copy(src, dst, command, **kwargs)

def windows_move(src, dst, **kwargs):
    """
    move using subprocess windows command;
    uses shutil if filename is changing
    """
    src_par = os.path.dirname(src)
    dst_par = os.path.dirname(dst)
    fname = os.path.basename(dst)
    command = f'robocopy "{src_par}" "{dst_par}" "{fname}" /mt /mov'
    if os.path.basename(src) != fname:
        command = f'move /Y "{src}" "{dst}"'
    return subprocess_copy(src, dst, command, **kwargs)

def subprocess_copy(src, dst, command, **kwargs):
    """
    call subprocess on a command and copy;
    """
    silent = kwargs.get('silent', True)
    return_src_dst_exist = kwargs.get('return_src_dst_exist', True)
    do_make_parent = kwargs.get('do_make_parent', True)
    check_exists = kwargs.get('check_exists', os.path.isfile)
    sub_kw = {'shell': True}
    if silent:
        sub_kw['stdout'] = subprocess.DEVNULL
    if do_make_parent:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
    src_exists = check_exists(src)
    dst_exists = check_exists(dst)
    if not dst_exists:
        with subprocess.Popen(command, **sub_kw) as process:
            process.communicate() ## returns std_out_data, std_err_data;
    src_exists = check_exists(src)
    dst_exists = check_exists(dst)
    if not dst_exists:
        print('dst does not exist still!!!!!!!!')
        input()
    status = gen_status(src_exists, dst_exists)
    if not return_src_dst_exist:
        return status
    return status, src_exists, dst_exists

def gen_status(src_exists, dst_exists):
    """
    status helper;
    """
    if src_exists and not dst_exists:
        status = 'only_src_exists'
    elif src_exists and dst_exists:
        status = 'both_exist'
    elif not src_exists and dst_exists:
        status = 'only_dst_exists'
    else:
        status = 'neither_exist'
    return status


def kv_status_src_dst_exist(*args):
    """
    make_kv() helper for move_data()
    parameters:
        args(list):
            args -> key, data, status
        status(tuple): status, src_exists, dst_exists
    """
    key, data, status = args
    try:
        status, src_exists, dst_exists = status
    except ValueError as error:
        print(status)
        raise error
    data.update({'status': status, 'src_exists': src_exists, 'dst_exists': dst_exists})
    return key, data

def move_data(data_json, **kwargs):
    """
    parameters:
        data_json(str): path to json where k=anything, v=anything
        kwargs(dict):
            get_src_dst(callable): get_src_dst(value, **kw); returns src, dst, data
                where data can be anything we want to return from each item that we
                are getting from a given src dst

            get_src_dst_kw(dict): keywords for get_src_dst()

            move_function(callable): move_function(src, dst, **kw); returns status
                where status tells us if a file was moved successfully or not

            move_function_kw(dict): keywords for move_function

            make_key(callable): make_key(key, **kw); returns what we want to use
                as a key to the final dictionary

            make_key_kw(dict): keywords for make_key()

            make_value(callable): make_value(key, new_key, status, data, **kw);
                returns what we want to use as a value in the final dictionary

            make_value_kw(dict): keywords for make_value()

            multiple_values(boolean): indicates whether we want to accept
                multiple_values for a given key in the final dictionary

            ext(str): string extension to the save name of the json file
    """
    read_data_file = kwargs.get('read_data_file', read_dictionary_file)
    read_data_file_kw = kwargs.get('read_data_file_kw', {})
    readables = kwargs.get("readables", {})
    readables_read_func = kwargs.get('readables_read_func', read_dictionary_file)
    readables_read_func_kw = kwargs.get('readables_read_func_kw', {})

    data_iterator = kwargs.get('data_iterator', yield_data)
    include_all_args = kwargs.get('include_all_args', False)
    get_src_dst = kwargs.get("get_src_dst")
    get_src_dst_kw = kwargs.get("get_src_dst_kw", {})

    continue_if_all_none = kwargs.get('continue_if_all_none', False)

    count = kwargs.get('count')
    limit = kwargs.get('limit')

    move_function = kwargs.get("move_function")
    move_function_kw = kwargs.get("move_function_kw", {})

    make_key = kwargs.get("make_key", lambda k: k)
    make_key_kw = kwargs.get("make_key_kw", {})

    make_value = kwargs.get("make_value")
    make_value_kw = kwargs.get("make_value_kw", {})

    make_kv = kwargs.get('make_kv')
    make_kv_kw = kwargs.get('make_kv_kw', {})

    add_src_and_dst_to_data = kwargs.get("add_src_and_dst_to_data", False)
    src_key = kwargs.get('src_key', 'src')
    dst_key = kwargs.get('dst_key', 'dst')
    multiple_values = kwargs.get("multiple_values", True)
    ext = kwargs.get("ext", "")
    debug = kwargs.get('debug', False)


    for kwarg in [get_src_dst_kw]:
        readables_read_func_kw = {'read_function_kw': readables_read_func_kw}
        add_readables_to_kwargs(readables, kwarg, readables_read_func, **readables_read_func_kw)

    folder_list_idx = 0
    final = {} if not multiple_values else defaultdict(list)
    for key, value in tqdm(read_data_file(data_json, **read_data_file_kw).items()):
        for item in data_iterator(value):
            if count is not None and count == limit:
                count = 0
                folder_list_idx += 1
            get_src_dst_kw.update({'folder_list_idx': folder_list_idx})
            if not include_all_args:
                args = (item, )
            else:
                args = (key, value, item)
            for src, dst, data in get_src_dst(*args, **get_src_dst_kw):
                ## >1 usage of data will refer to the same dict object;
                if continue_if_all_none and src is None and dst is None and data is None:
                    continue
                data = dict(data)
                if count is not None:
                    count += 1
                status = move_function(src, dst, **move_function_kw)

                if make_kv is None:
                    new_key = make_key(key, **make_key_kw)
                    new_value = make_value(key, new_key, status, data, **make_value_kw)
                else:
                    new_key, new_value = make_kv(key, data, status, **make_kv_kw)

                if add_src_and_dst_to_data:
                    new_value.update({src_key: src, dst_key: dst})

                if multiple_values:
                    final[new_key].append(new_value)
                else:
                    assert new_key not in final, f"{new_key}, {new_value}"
                    final[new_key] = new_value
                if debug:
                    print(dst)
    return {'final': final, '_ext': ext}