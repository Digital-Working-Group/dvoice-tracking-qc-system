"""
records.py
methods involving pulling, reading, or validating data from a REDCap or csv of records
"""
import csv
from collections import defaultdict
import requests
from qc_scripts.utility.read import read_dictionary_file
from qc_scripts.utility.id_validation import redcap_to_pid

def read_csv_records(**kwargs):
    """
    Reads data from csv
    """
    csv_filepath = kwargs.get('csv_filepath')
    ext = kwargs.get('ext', 'csv_records')
    data = []

    with open(csv_filepath, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)

    return[{'final': data, 'ext': ext}]

def get_data_request(token, fields_list):
    """
    Builds the data for the redcap api request
    Inputs:
        token: redcap API token
        fields_list: list of fieldnames to pull
    Returns:

    """
    data = {'token': token,
            'content': 'record',
            'action': 'export',
            'format': 'json',
            'type': 'flat',
            'csvDelimiter': '',
            'rawOrLabel': 'raw',
            'rawOrLabelHeaders': 'raw',
            'exportCheckboxLabel': 'false',
            'exportSurveyFields': 'false',
            'exportDataAccessGroups': 'false',
            'returnFormat': 'json'
            }
    for i, field in enumerate(fields_list):
        data[f'fields[{i}]'] = field
    return data

def pull_redcap(**kwargs):
    """
    Pulls data from redcap
    """
    token_func = kwargs.get('token')
    token = token_func()
    fields_list = kwargs.get('fields_list', [])
    redcap_url = kwargs.get('redcap_url')
    ext = kwargs.get('ext', 'redcap_records')

    data = get_data_request(token, fields_list)
    req_js = requests.post(redcap_url, data=data, timeout=10).json()
    return [{'final': req_js, 'ext': ext}]

def validate_records(input_data, **kwargs):
    """
    Checks that id/idtypes match the schema and that the required fields are filled out
    """
    required_fieldnames = kwargs.get('required_fieldnames', [])
    ext = kwargs.get('ext', 'validated_records')

    if isinstance(input_data, str):
        input_data = read_dictionary_file(input_data)

    records = defaultdict(lambda: defaultdict(str))
    invalid_id = []
    missing_fields = []

    for i in input_data:
        has_missing = False
        if i['date_dc'] != '' and i['record_id'] != '':
            date = i['date_dc']
            date = date.replace("-","")
            fid = redcap_to_pid(i['record_id'])
            key = f'{fid}_{date}'
            if fid is None:
                invalid_id.append({key: i})
                continue
            for field in required_fieldnames:
                if i[field] == "" or i[field] is None:
                    missing_fields.append({key: i})
                    has_missing = True
                    break
            if has_missing:
                continue
            records[key] = i

    fix_record= {'invalid_id': invalid_id, 'missing_fields': missing_fields}
    return[{'final': fix_record, 'ext': 'fix_record'},
           {'final': records, 'ext': ext}]
