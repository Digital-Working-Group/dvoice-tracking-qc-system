"""
pull_redcap.py
methods involving pulling redcap data
"""
import requests
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
    settings = kwargs.get('settings', {})

    data = get_data_request(token, fields_list)
    req_js = requests.post(redcap_url, data=data, timeout=10).json()
    process = settings['process']
    return [{'final': process(req_js), 'ext': ext}]

def validate_redcap_entries(input_data, **kwargs):
    """
    Checks that id/idtypes match the schema and that the required fields are filled out
    """
    required_fieldnames = kwargs.get('required_fieldnames', [])

    if isinstance(input_data, str):
        input_data = read_dictionary_file(input_data)

    invalid_id = []
    missing_fields = []
    for id_date, data in input_data.items():
        if redcap_to_pid(data['record_id']) is None:
            invalid_id.append(input_data[id_date])
        for field in required_fieldnames:
            if data[field] == "" or data[field] is None:
                missing_fields.append(input_data[id_date])
                continue
    fix_redcap = {'invalid_id': invalid_id, 'missing_fields': missing_fields}
    return[{'final': fix_redcap, 'ext': 'fix_redcap'}]
