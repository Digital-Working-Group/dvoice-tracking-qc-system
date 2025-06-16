"""
main_template.py
Main is not version controlled, so copy over the contents of this file and comment/uncomment code as needed.
"""

from qc_pipelines import pull_comparison_sources, walk, compare_sources_and_duplicates, move_and_update

if __name__ == '__main__':
    pull_comparison_sources()
    walk()
    compare_sources_and_duplicates()
    move_and_update()