"""
process_record.py
Holds methods for processing requests from data sources
"""
from collections import defaultdict
from qc_scripts.utility.id_validation import redcap_to_pid

def process_record(r):
    records = defaultdict(lambda: defaultdict(str))
    for i in r:
        if i['date_dc'] != '' and i['record_id'] != '':
            date = i['date_dc']
            date = date.replace("-","")
            try:
                fid = redcap_to_pid(i['record_id'])
                records[f'{fid}_{date}'] = i
            except AssertionError:
                print(f'Error processing {i['record_id']}. Please notify an RA to correct.')
    return records