"""
qc_pipelines.py
Holds pipeline scripts for each step of the example QC
"""
from datetime import date
from read_token import read_token
from qc_scripts.utility.pattern import example_pattern_data
from qc_scripts.walk import qc_walk
from qc_scripts.stream import Pipeline, SourceNode, FilterNode, ActionNode
from qc_scripts.records import pull_redcap, read_csv_records, validate_records
from qc_scripts.compare_records import flag_id_date, flag_tester_id, check_location
from qc_scripts.write_flagged_excel import write_flagged_excel
from qc_scripts.duplicates import clean_duplicates, flag_file_count
from qc_scripts.destination import get_dst, get_src_dst
from qc_scripts.move import move_files
from qc_scripts.clean_dataset import update_clean_dataset
from qc_scripts.utility.read import read_dictionary_file
from qc_scripts.utility import get_latest_data as gld
from qc_scripts.walk import match_filename_format

def csv_records(**kwargs):
    """
    Reads in a CSV in that contains the same fields as the example REDCap
    Validates idtype and id and checks that required fields have been filled out.
    """
    csv_kwargs = {
        'csv_filepath': 'sample_data/sample_csv_database.csv'}
    csv_kwargs.update(kwargs.get('csv_kwargs', {}))

    validate_kwargs = {
        'required_fieldnames': ['date_dc', 'data_loc'],
        'ext': 'csv_records'
    }
    validate_kwargs.update(kwargs.get('validate_kwargs', {}))

    (Pipeline('csv_records_pipeline')
     .add_node(SourceNode(func=read_csv_records, **csv_kwargs))
     .add_node(FilterNode(func=validate_records, input_key='csv_records', **validate_kwargs))
    ).run()

def pull_comparison_sources():
    """
    Pulls and formats data from the example REDCap
    Validates idtype and id and checks that required fields have been filled out.
    """
    rc_kwargs = {
        'fields_list': ['record_id',
                        'date_dc',
                        'tester_id',
                        'data_loc',
                        'information_sheet_complete'],
        'token': read_token,
        'redcap_url': gld.get_root_fp('redcap_url')
    }

    validate_kwargs = {
        'required_fieldnames': ['date_dc', 'data_loc']
    }

    (Pipeline('pull_sources_pipeline')
     .add_node(SourceNode(func=pull_redcap, **rc_kwargs))
     .add_node(FilterNode(func=validate_records, input_key='redcap_records', **validate_kwargs))
    ).run()

def walk(**kwargs):
    """
    Walks files in given root and separates by passed, pattern mismatch, and wrong extension
    """
    walk_kwargs = {
        'roots': ["sample_data/"],
        'ignore_list': [],
        'keep_exts': ('wav', 'm4a', 'mp3'),
        'pattern_list': example_pattern_data(),
        'make_kv': match_filename_format,
        'walk_kwargs': {'multiple_values': True, 'ext': 'walk'}
    }
    walk_kwargs.update(kwargs.get('walk_kwargs', {}))

    (Pipeline('walk_pipeline')
     .add_node(SourceNode(func=qc_walk, **walk_kwargs))
    ).run()

def compare_sources_and_duplicates(**kwargs):
    """
    Contains all data filters:
        - Compares id_date to records
        - Compares tester_id to records
        - Checks for duplicates
        - Checks for too many file occurrences
        - Compares location to records
        - Writes file destination path
    """
    records = read_dictionary_file(gld.get_filepath('csv_records_pipeline_csv_records'))

    flag_kwargs = {
        'record_end_date': date(2025, 4, 30),
        'rc_tester_id_fieldname': 'tester_id',
        'rc_date_fieldname': 'date_dc',
        'records': records,
        'ext': 'example'
    }
    flag_kwargs.update(kwargs.get('flag_kwargs', {}))

    duplicate_kwargs = {
        'duplicate_root': 'sample_data/duplicates/'
    }
    duplicate_kwargs.update(kwargs.get('duplicate_kwargs', {}))

    move_kwargs = {
        'move_back': False
    }
    move_kwargs.update(kwargs.get('move_kwargs', {}))

    (Pipeline('flag_pipeline')
        .update_state('walk_passed', gld.get_filepath('walk_pipeline_walk'))
        .add_node(FilterNode(func=flag_id_date, input_key='walk_passed', **flag_kwargs))
        .add_node(ActionNode(func=write_flagged_excel, input_keys=['flagged_no_redcap_entry_example'],
                             **{'flag_type': 'no_records_entry', 'ext': 'example'}))
        .add_node(FilterNode(func=flag_tester_id, **flag_kwargs))
        .add_node(ActionNode(func=write_flagged_excel, input_keys=['flagged_tester_id_mismatch_example'],
                             **{'flag_type': 'tester_id_mismatch', 'ext': 'example'}))
        .add_node(ActionNode(func=write_flagged_excel, input_keys=['flagged_tester_id_no_redcap_example'],
                             **{'flag_type': 'tester_id_no_records', 'ext': 'example'}))
        .add_node(FilterNode(func=clean_duplicates, **duplicate_kwargs))
        .add_node(ActionNode(func=move_files, input_keys=['duplicates'], **move_kwargs))
        .add_node(FilterNode(func=flag_file_count))
        .add_node(FilterNode(func=check_location, **{'records': records}))
        .add_node(FilterNode(func=get_dst))
    ).run()

def move_and_update():
    """
    Moves files to their destinations
    Updates the clean dataset with the files moved
    """
    move_kwargs = {
        'src_dst_func': get_src_dst,
        'move_back': False
        }

    clean_kwargs = {
        'clean_dataset': gld.get_filepath('clean_dataset')
    }

    (Pipeline('move_pipeline')
     .update_state('flag_pipeline_passed', gld.get_filepath('flag_pipeline_passed'))
     .add_node(ActionNode(func=move_files, input_keys=['flag_pipeline_passed'], **move_kwargs))
     .add_node(ActionNode(func=update_clean_dataset, input_keys=['flag_pipeline_passed'], **clean_kwargs))
    ).run()
