"""
compare_records.py
Methods for comparing file data to records
"""
from datetime import datetime
from collections import defaultdict
from tqdm import tqdm
from qc_scripts.utility.read import read_dictionary_file

def flag_id_date(input_data, **kwargs):
    """
    Compare id_dates in filenames to the records we have from records

    """
    ## Get kwargs
    records = kwargs.get('records')
    record_end_date = kwargs.get('record_end_date', datetime.now())
    ext = kwargs.get('ext', '')
    rc_tester_id_fieldname = kwargs.get('rc_tester_id_fieldname')
    rc_date_fieldname = kwargs.get('rc_date_fieldname')
    ignore_flagged = kwargs.get('ignore_flagged_rc', [])


    ## Allows for input to be either a filepath or a dictionary of data
    if isinstance(input_data, str):
        input_data = read_dictionary_file(input_data)
    
    if isinstance(records, str):
        records = read_dictionary_file(records)

    record_id_dates = list(records.keys())
    flagged_no_record = {}
    passed = {}
        
    # checks our dvrs to see if they have a record
    for id_date, data in tqdm(input_data.items()):
        ## add in validate fid
        if id_date not in record_id_dates:
            if id_date in ignore_flagged:
                passed[id_date] = data
                continue
            nearest = []
            # data =  get_creation_time(data)
            for idd in record_id_dates:
                if data[0]['pid'] in idd:
                    for i in data:
                        try:
                            idd_date = datetime.strptime(idd.split('_')[-1], "%Y%m%d").date()
                            difference = abs((idd_date - date_of_file).days)
                        except ValueError:
                            difference = 'Error'
                        ra = records[idd][rc_tester_id_fieldname]
                        date = records[idd][rc_date_fieldname].replace('-', '')
                        nearest.append({'id_date': idd, 'date': date, 'difference': difference, 'tester_id_completing': ra})
                        i['nearest'] = nearest

            flagged_no_record[id_date] = data
        else:
            date_of_file = datetime.strptime(data[0]['date'], "%Y%m%d").date()
            if date_of_file <= record_end_date:
                passed[id_date] = data
                
    return [{'final': passed, "ext": "passed"},
            {'final': flagged_no_record, "ext": f"flagged_no_records_{ext}"}]

def flag_tester_id(input_data, **kwargs):
    """
    Checks that the tester_id in the filename matches the one recorded in records
    """
    ## Get kwargs
    records = kwargs.get('records')
    ext = kwargs.get('ext', '')
    rc_tester_id_fieldname = kwargs.get('rc_tester_id_fieldname')
    ignore_flagged = kwargs.get('ignore_flagged_tester', [])

    if isinstance(input_data, str):
        input_data = read_dictionary_file(input_data)
    
    if isinstance(records, str):
        records = read_dictionary_file(records)
    
    flagged_tester_id_mismatch = defaultdict(list)
    id_date_not_found = defaultdict(list)
    passed = defaultdict(list)
    for id_date, data in tqdm(input_data.items()):
        if id_date in ignore_flagged:
            passed[id_date] = data
            continue
        try:
            rc_tester_id = records[id_date][rc_tester_id_fieldname]
        except KeyError:
            print(f'{id_date} not found in {rc_tester_id_fieldname}')
            id_date_not_found[id_date] = (data)
        else:
            for item in data:
                if item['tester_id'] != rc_tester_id:
                    item['rc_tester_id'] = rc_tester_id
                    flagged_tester_id_mismatch[id_date].append(item)
                else:
                    passed[id_date].append(item)

    return [{'final': passed, "ext": "passed"},
            {'final': flagged_tester_id_mismatch, "ext": f"flagged_tester_id_mismatch_{ext}"},
            {'final': id_date_not_found, 'ext': f'flagged_tester_id_no_records_{ext}'}]

def check_location(input_data, **kwargs):
    """
    Checks remote vs in-person file matches record keying
    Returns Boolean: True (match) or False (no match)
            walkdata updated with variables
    """
    records = kwargs.get('records')
    if isinstance(records, str):
        records = read_dictionary_file(records)
        
    match = defaultdict(list)
    location_mismatch = defaultdict(list)
    
    for id_date, data in tqdm(input_data.items()):
        location = records[id_date]['data_loc']
        for entry in data:
            entry['location'] = entry['location'].lower()
            if location == '0' or location == 'remote':
                entry['record_location'] = 'remote'
            elif location == '1' or location == 'in-person':
                entry['record_location'] = 'in-person'
            else:
                entry['record_location'] = 'undefined'
            if entry['record_location'] != entry['location'] or entry['record_location'] == 'undefined':
                location_mismatch[id_date].append(entry)
            else:
                match[id_date].append(entry)

    return [{'final': match, "ext": "passed"},
            {'final': location_mismatch, "ext": "location_mismatch"}]