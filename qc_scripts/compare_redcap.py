from datetime import datetime
from tqdm import tqdm
from collections import defaultdict
from qc_scripts.utility.read import read_dictionary_file

def flag_id_date(input_data, **kwargs):
    """
    Compare id_dates in filenames to the records we have from redcap
    Inputs:

    """
    ## Get kwargs
    redcap_entries = kwargs.get('redcap_entries')
    record_end_date = kwargs.get('record_end_date', datetime.now())
    ext = kwargs.get('ext', '')
    rc_tester_id_fieldname = kwargs.get('rc_tester_id_fieldname')
    rc_date_fieldname = kwargs.get('rc_date_fieldname')
    ignore_flagged = kwargs.get('ignore_flagged_rc', [])


    ## Allows for input to be either a filepath or a dictionary of data
    if isinstance(input_data, str):
        input_data = read_dictionary_file(input_data)
    
    if isinstance(redcap_entries, str):
        redcap_entries = read_dictionary_file(redcap_entries)

    redcap_id_dates = list(redcap_entries.keys())
    flagged_no_redcap_entry = {}
    flagged_not_in_date_range = {}
    passed = {}
        
    # checks our dvrs to see if they have a redcap entry
    for id_date, data in tqdm(input_data.items()):
        ## add in validate fid
        if id_date not in redcap_id_dates:
            if id_date in ignore_flagged:
                passed[id_date] = data
                continue
            try:
                date_of_file = datetime.strptime(data[0]['date'], "%Y%m%d").date()
            except ValueError:
                flagged_not_in_date_range[id_date] = data
            if date_of_file > record_end_date:
                flagged_not_in_date_range[id_date] = data
            else:
                nearest = []
                # data =  get_creation_time(data)
                for idd in redcap_id_dates:
                    if data[0]['pid'] in idd:
                        for i in data:
                            try:
                                idd_date = datetime.strptime(idd.split('_')[-1], "%Y%m%d").date()
                                difference = abs((idd_date - date_of_file).days)
                            except ValueError:
                                differnece = 'Error'
                            ra = redcap_entries[idd][rc_tester_id_fieldname]
                            date = redcap_entries[idd][rc_date_fieldname].replace('-', '')
                            nearest.append({'id_date': idd, 'date': date, 'difference': difference, 'tester_id_completing': ra})
                            i['nearest'] = nearest

                flagged_no_redcap_entry[id_date] = data
        else:
            passed[id_date] = data
    return [{'final': passed, "ext": "passed"},
            {'final': flagged_no_redcap_entry, "ext": f"flagged_no_redcap_entry_{ext}"},
            {'final': flagged_not_in_date_range, "ext": f"flagged_not_in_date_range_{ext}"}]

def flag_tester_id(input_data, **kwargs):
    """
    Checks that the tester_id in the filename matches the one recorded in redcap
    """
    ## Get kwargs
    redcap_entries = kwargs.get('redcap_entries')
    ext = kwargs.get('ext', '')
    rc_tester_id_fieldname = kwargs.get('rc_tester_id_fieldname')
    ignore_flagged = kwargs.get('ignore_flagged_tester', [])

    if isinstance(input_data, str):
        input_data = read_dictionary_file(input_data)
    
    if isinstance(redcap_entries, str):
        redcap_entries = read_dictionary_file(redcap_entries)
    
    flagged_tester_id_mismatch = defaultdict(list)
    id_date_not_found = defaultdict(list)
    passed = defaultdict(list)
    for id_date, data in tqdm(input_data.items()):
        if id_date in ignore_flagged:
            passed[id_date] = data
            continue
        try:
            rc_tester_id = redcap_entries[id_date][rc_tester_id_fieldname]
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
            {'final': id_date_not_found, 'ext': f'flagged_tester_id_no_redcap_{ext}'}]

def check_location(input_data, **kwargs):
    """
    Checks remote vs in-person file matches REDCap keying
    Returns Boolean: True (match) or False (no match)
            walkdata updated with variables
    """
    redcap_entries = kwargs.get('redcap_entries')
    if isinstance(redcap_entries, str):
        redcap_entries = read_dictionary_file(redcap_entries)
        
    match = defaultdict(list)
    location_mismatch = defaultdict(list)
    for id_date, data in tqdm(input_data.items()):
        location_num = redcap_entries[id_date]['data_loc']
        for entry in data:
            if location_num == '0':
                entry['redcap_location'] = 'remote'
            elif location_num == '1':
                entry['redcap_location'] = 'in-person'
            else:
                entry['redcap_location'] = 'undefined'
            if entry['redcap_location'] != entry['location'] or entry['redcap_location'] == 'undefined':
                location_mismatch[id_date].append(entry)
            else:
                match[id_date].append(entry)
    return [{'final': match, "ext": "passed"},
            {'final': location_mismatch, "ext": "location_mismatch"}]