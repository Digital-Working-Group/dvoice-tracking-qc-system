"""
main_template.py
Main is not version controlled, so copy over the contents of this file and comment/uncomment code as needed.
"""
import qc_pipelines as qcp

if __name__ == '__main__':
    # CSV_RECORDS_KW = {'csv_kwargs': {'csv_filepath': 'sample_data/sample_csv_database.csv'}}
    # qcp.csv_records(**CSV_RECORDS_KW)

    # qcp.pull_comparison_sources()
    ## Run only csv_records() [option #1] OR pull_comparison_sources() [option #2]

    # WALK_KWARGS = {'walk_kwargs': {'roots': ["sample_data/"]}}
    # walk(**WALK_KWARGS)

    CMP_KWARGS = {'flag_kwargs': {'record_end_date': qcp.date.today()},
        'duplicate_kwargs': {'duplicate_root': 'sample_data/duplicates'},
        'move_kwargs': {'move_back': False}}
    qcp.compare_sources_and_duplicates(**CMP_KWARGS)

    # move_and_update()
