"""
main_template.py

Copy this file and place this in the root folder of this repo.
"""
import qc_pipelines as qcp

if __name__ == '__main__':
    CSV_RECORDS_KW = {'csv_kwargs': {'csv_filepath': 'sample_csv_database.csv'}}
    qcp.pull_records(source='csv', **CSV_RECORDS_KW)

    WALK_KWARGS = {'walk_kwargs': {'roots': ["sample_data/"]}}
    qcp.walk(**WALK_KWARGS)

    CMP_KWARGS = {'flag_kwargs': {'record_end_date': qcp.date(2025, 4, 30)},
        'duplicate_kwargs': {'duplicate_root': 'sample_data/duplicates'}}
    qcp.compare_sources_and_duplicates(**CMP_KWARGS)

    MOVE_KWARGS = {'move_kwargs': {'move_back': False}}
    qcp.move_duplicates(**MOVE_KWARGS)

    MOVE_KWARGS = {'move_kwargs': {'move_back': False}}
    qcp.move_and_update(**MOVE_KWARGS)
