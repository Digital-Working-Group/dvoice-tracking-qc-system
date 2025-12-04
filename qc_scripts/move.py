"""
move.py: move functions for files
"""
import os
from collections import defaultdict
from tqdm import tqdm
import qc_scripts.utility.move_commands as mf
from qc_scripts.utility.read import read_dictionary_file

def get_src_dst(data, move_back, **_):
    """
    Getting src and dst
    """
    src, dst = data['src'], data['dst']
    if dst is None:
        return [[None, None, None]]
    if move_back:
        src, dst = dst, src
        data = data.copy()
        data['src'], data['dst'] = src, dst
    return [[src, dst, data]]

def move_files(input_data, **kwargs):
    """
    moving  files to their destinations
    """
    ## get kwargs
    move_back = kwargs.get('move_back', False)
    ext = kwargs.get('ext', 'move')
    read_data_file = kwargs.get('read_data_file', lambda d: d)
    ## Should I allow multiple values here
    multiple_values = kwargs.get('multiple_values', True)

    if isinstance(input_data, str):
        input_data = read_dictionary_file(input_data)

    print(f'The input data has the following keys: {input_data.keys()}')

    if move_back:
        ext += '_move_back'

    src_dst_func = kwargs.get('src_dst_func', get_src_dst)
    move_function = mf.shutil_move if os.sep == "\\" else mf.linux_move
    final = {} if not multiple_values else defaultdict(list)

    for key, value in tqdm(read_data_file(input_data).items()):
        for src, dst, data in src_dst_func(value, move_back):
            data = dict(data)
            status = move_function(src, dst)
            new_key, new_value = mf.kv_status_src_dst_exist(key, data, status)

            if multiple_values:
                final[new_key].append(new_value)
            else:
                assert new_key not in final, f"{new_key}, {new_value}"
                final[new_key] = new_value

    return [{'final': final, 'ext': ext}]
