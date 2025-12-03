"""
methods for writing an excel file 
"""
import os
import copy
from datetime import datetime
import pandas as pd
from qc_scripts.utility.read import read_dictionary_file

def flatten(item, parent_key='', sep='_'):
    """
    Recursively flattens a structure of dicts and lists of dicts.
    """
    items = []
    if isinstance(item, dict):
        for k, v in item.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            items.extend(flatten(v, new_key, sep=sep).items())
    elif isinstance(item, list):
        for i, v in enumerate(item):
            new_key = f"{parent_key}{sep}{i}" if parent_key else ''
            items.extend(flatten(v, new_key, sep=sep).items())
    else:
        items.append((parent_key, item))
    return dict(items)

def flattened_to_df(input_data):
    """
    Flattens a nested dictionary or a dict with lists of dicts into a DataFrame.
    """
    data_dict = copy.deepcopy(input_data)
    flat_data = {}

    for key, val in data_dict.items():
        flat_data[key] = flatten(val)

    return pd.DataFrame.from_dict(flat_data, orient='index')

def autofit_column_width(writer, sheetname, df, extra_space=2, startcol=0):
    """
    autofits all columns in sheet to min width without obstructing items
    """
    worksheet = writer.sheets[sheetname]
    for idx, col in enumerate(df):  # loop through all columns
        series = df[col]
        max_len = max((
            series.astype(str).map(len).max(),  # len of largest item
            len(str(series.name))  # len of column name/header
            )) + extra_space  # adding a little extra space
        worksheet.set_column(idx+startcol, idx+startcol, max_len)

def output_flagged_xlsx(__, state_updates, func_name, ignore_write=None):
    """
    Helper for writing flagged files to an excel 
    to be passed as a write_output_func to a node
    """
    state_additions = copy.deepcopy(state_updates)
    ignore_list = ['passed']
    if ignore_write is not None:
        ignore_list.extend(ignore_write)
    for key, value in state_additions.items():
        if key in ignore_list:
            continue
        write_flagged_excel(value, f"{func_name}_{key}", key)

def write_flagged_excel(input_data, flag_type, ext):
    """
    Writes the files in the flagged dictionary to an xlsx
    """

    if isinstance(input_data, str):
        input_data = read_dictionary_file(input_data)

    if len(input_data) == 0:
        return

    summary_df = flattened_to_df(input_data)
    if 'nearest' in summary_df.columns:
        summary_df.drop('nearest', axis=1, inplace=True)
    summary_df['correction'] = 'NA'
    now = datetime.now()
    output_dir = f'flagged/{flag_type}'
    output_dir = os.path.join(output_dir, now.strftime("%Y%m%d"))
    os.makedirs(output_dir, exist_ok=True)
    out_fp = os.path.join(output_dir, f'{ext}_{flag_type}_{now.strftime("%Y%m%d_%H%M%S")}.xlsx')
    writer = pd.ExcelWriter(out_fp, engine='xlsxwriter')
    summary_df.to_excel(writer, sheet_name='Summary', index=False)
    autofit_column_width(writer, 'Summary', summary_df)
    if 'tester_id' in summary_df.columns:
        for group, data in summary_df.groupby(['tester_id']):
            tester_id = group[0]
            data.drop(labels='tester_id', axis=1, inplace=True)
            data.to_excel(writer, sheet_name=tester_id, index=False)
            autofit_column_width(writer, tester_id, data)
    writer.close()
