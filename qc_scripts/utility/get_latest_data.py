"""
get_latest_data.py
get latest data JSON paths
based of get_latest_data from fhs_dcdt_quality_control repo
"""
from qc_scripts.utility.read import read_dictionary_file

def get_filepath(key, static_json="static.json"):
    """
    get filepath associated with key
    """
    return read_dictionary_file(static_json)[key]

def get_root_fp(key, static_json="config.json"):
    """
    get filepath associated with key
    """
    return read_dictionary_file(static_json)[key]
