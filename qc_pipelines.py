"""
qc_pipelines.py
Holds pipeline scripts for each step of the example QC
"""
from datetime import date
from qc_scripts.compare_records import flag_id_date, flag_tester_id, check_location
from qc_scripts.clean_dataset import update_clean_dataset
from qc_scripts.destination import get_dst, get_src_dst
from qc_scripts.duplicates import clean_duplicates, flag_file_count
from qc_scripts.move import move_files
from qc_scripts.records import pull_redcap, read_csv_records, validate_records
from qc_scripts.stream import Pipeline, SourceNode, FilterNode, ActionNode
from qc_scripts.utility import get_latest_data as gld
from qc_scripts.utility.pattern import example_pattern_data
from qc_scripts.utility.read import read_dictionary_file
from qc_scripts.walk import match_filename_format, qc_walk
from qc_scripts.write_flagged_excel import output_flagged_xlsx

def get_rc_kwargs():
    """
    get REDCap keyword arguments, if source='redcap'
    """
    from read_token import read_token
    rc_kwargs = {
        'fields_list': ['record_id',
                        'date_dc',
                        'tester_id',
                        'data_loc',
                        'information_sheet_complete'],
        'token': read_token,
        'redcap_url': gld.get_root_fp('redcap_url')
    }
    return rc_kwargs

def pull_records(source='csv', **kwargs):
    """
    Reads in a CSV in that contains the same fields as the example REDCap
    Validates idtype and id and checks that required fields have been filled out.
    """
    # source = kwargs.get('source', 'csv')  ## 'csv' or 'redcap'

    csv_kwargs = {
        'csv_filepath': 'sample_csv_database.csv'}
    csv_kwargs.update(kwargs.get('csv_kwargs', {}))

    validate_kwargs = {
        'required_fieldnames': ['date_dc', 'data_loc'],
        'ext': 'validated_records'
    }
    validate_kwargs.update(kwargs.get('validate_kwargs', {}))

    if source.lower() == 'redcap':
        rc_kwargs = get_rc_kwargs()
        (Pipeline('records_pipeline')
        .add_node(SourceNode(func=pull_redcap, **rc_kwargs))
        .add_node(FilterNode(func=validate_records, input_key='redcap_records', **validate_kwargs))
        ).run()

    elif source.lower() == 'csv':
        (Pipeline('records_pipeline')
         .add_node(SourceNode(func=read_csv_records, **csv_kwargs))
         .add_node(FilterNode(func=validate_records, input_key='csv_records', **validate_kwargs))
        ).run()

    else:
        raise ValueError("source must be either 'csv' or 'redcap'")
    
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
        'multiple_values': True,
        'ext': 'walk'
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
    records = read_dictionary_file(gld.get_filepath('records_pipeline_validated_records'))

    flag_kwargs = {
        'record_end_date': date.today(),
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


    (Pipeline('flag_pipeline')
        .update_state('walk_passed', gld.get_filepath('walk_pipeline_walk'))
        .add_node(FilterNode(func=flag_id_date, input_key='walk_passed', write_output_func=output_flagged_xlsx,**flag_kwargs))
        .add_node(FilterNode(func=flag_tester_id, write_output_func=output_flagged_xlsx, **flag_kwargs))
        .add_node(FilterNode(func=clean_duplicates, **duplicate_kwargs))
        .add_node(FilterNode(func=flag_file_count))
        .add_node(FilterNode(func=check_location, **{'records': flag_kwargs['records']}))
        .add_node(FilterNode(func=get_dst))
    ).run()

def move_duplicates(**kwargs):
    """
    move duplicate files;
    """
    move_kwargs = {
        'src_dst_func': get_src_dst,
        'move_back': False
    }
    move_kwargs.update(kwargs.get('move_kwargs', {}))

    (Pipeline('move_duplicates_pipeline')
        .update_state('duplicates', gld.get_filepath('flag_pipeline_duplicates'))
        .add_node(ActionNode(func=move_files, input_keys=['duplicates'], **move_kwargs))
    ).run()

def move_and_update(**kwargs):
    """
    Moves files to their destinations
    Updates the clean dataset with the files moved
    """
    move_kwargs = {
        'src_dst_func': get_src_dst,
        'move_back': False
        }
    move_kwargs.update(kwargs.get('move_kwargs', {}))

    clean_kwargs = {
        'clean_dataset': gld.get_filepath('clean_dataset')
    }
    clean_kwargs.update(kwargs.get('clean_kwargs', {}))

    (Pipeline('move_pipeline')
     .update_state('flag_pipeline_passed', gld.get_filepath('flag_pipeline_passed'))
     .add_node(ActionNode(func=move_files, input_keys=['flag_pipeline_passed'], **move_kwargs))
     .add_node(ActionNode(func=update_clean_dataset, input_keys=['flag_pipeline_passed'], **clean_kwargs))
    ).run()
