"""
main_template.py
Main is not version controlled, so copy over the contents of this file and comment/uncomment code as needed.
"""

from qc_pipelines import pull_comparison_sources, walk, compare_sources_and_duplicates, move_and_update

def pipeline_pull_compare_sources():
    """
    Calls pull_comparison_sources pipeline
    """
    pull_comparison_sources()

def pipeline_walk():
    """
    Calls walk pipeline
    """
    walk()

def pipeline_compare_sources_and_duplicates():
    """
    Calls compare_sources_and_duplicates pipeline
    """
    compare_sources_and_duplicates()

def pipeline_move_and_update():
    """
    Calls move_and_update pipeline
    """
    move_and_update()
    
if __name__ == '__main__':
    pull_comparison_sources()
    walk()
    compare_sources_and_duplicates()
    move_and_update()