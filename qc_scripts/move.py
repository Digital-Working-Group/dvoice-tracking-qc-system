"""
move.py: move functions for files
"""
import os
from datetime import datetime
import qc_scripts.utility.move_commands as mf
from qc_scripts.utility.read import read_dictionary_file

def move_files(input_data, **kwargs):
    """
    moving  files to their destinations
    """
    start_time = datetime.now()

    ## get kwargs
    move_back = kwargs.get('move_back', False)
    move_function_kw = kwargs.get('move_function_kw', {})
    add_move_kw = kwargs.get ('add_move_kw', {})
    ext = kwargs.get('ext', 'move')
    read_data_file = kwargs.get('read_data_file', lambda d: d)

    if isinstance(input_data, str):
        input_data = read_dictionary_file(input_data)

    if move_back:
        ext += '_move_back'
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
    
    def wrap_src_dst(func, move_back=False):
        def wrapper(data, **kwargs):
            return func(data, move_back, **kwargs)
        return wrapper

    src_dst_func = wrap_src_dst(kwargs.get('src_dst_func', get_src_dst), move_back)
    move_function = mf.windows_move if os.sep == "\\" else mf.linux_move
    move_kwargs = {'get_src_dst': src_dst_func,
        'move_function': move_function, 'move_function_kw': move_function_kw,
        'make_kv': mf.kv_status_src_dst_exist, 'read_data_file': read_data_file, 'ext': ext}
    if add_move_kw != {}:
        move_kwargs.update(add_move_kw)
    result = mf.move_data(input_data, **move_kwargs)
    result['ext'] = result['_ext']
    return [result]