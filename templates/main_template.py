"""
main_template.py
Main is not version controlled, so copy over the contents of this file and comment/uncomment code as needed.
"""
from qc_pipelines import pull_comparison_sources, walk, compare_sources_and_duplicates, move_and_update, csv_records
    
if __name__ == '__main__':
    csv_records()
    pull_comparison_sources()
    ## Run only csv_records() [option #1] OR pull_comparison_sources() [option #2]
    walk()
    compare_sources_and_duplicates()
    move_and_update()