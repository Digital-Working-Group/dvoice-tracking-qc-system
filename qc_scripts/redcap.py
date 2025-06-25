"""
pull_redcap.py
methods involving pulling redcap data
"""
import requests
from collections import defaultdict
from qc_scripts.utility.read import read_dictionary_file
from qc_scripts.utility.id_validation import redcap_to_pid

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
    r = requests.post(redcap_url, data=data, timeout=10).json()
    return [{'final': r, 'ext': ext}]
    req_js = requests.post(redcap_url, data=data, timeout=10).json()
    process = settings['process']
    return [{'final': process(req_js), 'ext': ext}]

def validate_redcap_entries(input_data, **kwargs):
    """
    Checks that id/idtypes match the schema and that the required fields are filled out
    """
    required_fieldnames = kwargs.get('required_fieldnames', [])
    ext = kwargs.get('ext', 'redcap_records')

    if isinstance(input_data, str):
        input_data = read_dictionary_file(input_data)

    redcap_records = defaultdict(lambda: defaultdict(str)) 
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
            redcap_records[key] = i

    fix_redcap = {'invalid_id': invalid_id, 'missing_fields': missing_fields}
    return[{'final': fix_redcap, 'ext': 'fix_redcap'},
           {'final': redcap_records, 'ext': ext}]