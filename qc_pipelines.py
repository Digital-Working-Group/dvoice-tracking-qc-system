"""
qc_pipelines.py
Holds pipeline scripts for each step of the example QC
"""
from datetime import date
from read_token import read_token
from qc_scripts.utility.pattern import example_pattern_data
from qc_scripts.walk import qc_walk
from qc_scripts.stream import Pipeline, SourceNode, FilterNode, ActionNode
from qc_scripts.redcap import pull_redcap, validate_redcap_entries
from qc_scripts.compare_redcap import flag_id_date, flag_tester_id, check_location
from qc_scripts.write_flagged_excel import write_flagged_excel
from qc_scripts.duplicates import clean_duplicates, flag_file_count
from qc_scripts.destination import get_dst, get_src_dst
from qc_scripts.move import move_files
from qc_scripts.clean_dataset import update_clean_dataset
from qc_scripts.utility.read import read_dictionary_file
from qc_scripts.utility import get_latest_data as gld
from qc_scripts.walk import match_filename_format

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
     .add_node(FilterNode(func=validate_redcap_entries, input_key='redcap_records', **validate_kwargs))
    ).run()

def walk():
    """
    Walks files in given root and separates by passed, pattern mismatch, and wrong extention
    """

    kwargs = {
        'pattern_list': example_pattern_data(),
        'make_kv': match_filename_format,
        'roots': ["sample_data/"],
        'ignore_list': [],
        'keep_exts': ('wav', 'm4a', 'mp3'),
        'walk_kwargs': {'multiple_values': True, 'ext': 'walk'}
    }

    (Pipeline('walk_pipeline')
     .add_node(SourceNode(func=qc_walk, **kwargs))
    ).run()

def compare_sources_and_duplicates():
    """
    Contains all data filters:
        - Compares id_date to REDCap
        - Compares tester_id to REDCap
        - Checks for duplicates
        - Checks for too many file occurences 
        - Compares location to REDCap
        - Writes file destination path
    """
    redcap_entries = read_dictionary_file(gld.get_filepath('pull_sources_pipeline_redcap_records'))

    kwargs = {
        'record_end_date': date(2025, 4, 30),
        'rc_tester_id_fieldname': 'tester_id',
        'rc_date_fieldname': 'date_dc',
        'redcap_entries': redcap_entries,
        'ext': 'example'
    }

    ## Not being used - check with Cody if we want to be moving the duplicates
    duplciate_kwargs = {
        'duplicate_root': 'sample_data/duplicates/'
    }

    (Pipeline('flag_pipeline')
        .update_state('walk_passed', gld.get_filepath('walk_pipeline_walk'))
        .add_node(FilterNode(func=flag_id_date, input_key='walk_passed', **kwargs))
        .add_node(ActionNode(func=write_flagged_excel, input_keys=['flagged_no_redcap_entry_example'], 
                             **{'flag_type': 'no_redcap_entry', 'ext': 'example'}))
        .add_node(FilterNode(func=flag_tester_id, **kwargs))
        .add_node(ActionNode(func=write_flagged_excel, input_keys=['flagged_tester_id_mismatch_example'], 
                             **{'flag_type': 'tester_id_mismatch', 'ext': 'video'}))
        .add_node(ActionNode(func=write_flagged_excel, input_keys=['flagged_tester_id_no_redcap_example'], 
                             **{'flag_type': 'tester_id_no_redcap', 'ext': 'video'}))
        .add_node(FilterNode(func=clean_duplicates, **duplciate_kwargs))
        .add_node(FilterNode(func=flag_file_count))
        .add_node(FilterNode(func=check_location, **{'redcap_entries': redcap_entries}))
        .add_node(FilterNode(func=get_dst))
    ).run()

def move_and_update():
    """
    Moves files to their destinations
    Updates the clean dataset with the files moved
    """
    kwargs = {
        'src_dst_func': get_src_dst,
        'move_back': False,
        'clean_dataset': gld.get_filepath('clean_dataset')
        }

    (Pipeline('move_pipeline')
     .update_state('flag_pipeline_passed', gld.get_filepath('flag_pipeline_passed'))
     .add_node(ActionNode(func=move_files, input_keys=['flag_pipeline_passed'], **kwargs))
     .add_node(ActionNode(func=update_clean_dataset, input_keys=['flag_pipeline_passed'], **kwargs))
    ).run()
