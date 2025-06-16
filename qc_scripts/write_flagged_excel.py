"""
methods for writing an excel file 
"""
import os
import copy
import pandas as pd
from datetime import datetime
from qc_scripts.utility.read import read_dictionary_file

def flattened_to_df(input_data):
    flatten_data = {}
    data_dict = copy.deepcopy(input_data)
    for key, value1 in data_dict.items():
        if isinstance(value1, dict):
            flatten_data[key] = value1
        elif isinstance(value1, list) and all(isinstance(i, dict) for i in value1):
            for item in value1:
                for key2, val in item.items():
                    if isinstance(val, list):
                        for idx, subitem in enumerate(val):
                            if isinstance(subitem, dict):
                                for key3, item3 in subitem.items():
                                    item[f'{key2}_{key3}_{idx}'] = item3
                        break
                flatten_data[key] = item
    return pd.DataFrame.from_dict(flatten_data, orient='index')

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

def write_flagged_excel(input_data, **kwargs):
    """
    Writes the files in the flagged dictionary to a csv
    """
    ## get kwargs
    flag_type = kwargs.get('flag_type', 'no_match')
    ext = kwargs.get('ext', 'redcap_flagged')

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