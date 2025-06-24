"""
process_record.py
Holds methods for processing requests from data sources
"""
from collections import defaultdict
from id_validation import redcap_to_pid

def process_record(rc_output):
    """
    process redcap output
    """
    records = defaultdict(lambda: defaultdict(str))
    for item in rc_output:
        if item['date_dc'] != '' and item['record_id'] != '':
            date = item['date_dc']
            date = date.replace("-","")
            try:
                fid = redcap_to_pid(item['record_id'])
                records[f'{fid}_{date}'] = item
            except AssertionError:
                print(f'Error processing {item["record_id"]}. Please notify an RA to correct.')
    return records
