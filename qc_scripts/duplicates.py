"""
duplicates.py
Methods for dealing with duplicate data
"""
import os
import filecmp 
from itertools import combinations
from tqdm import tqdm

def flag_file_count(input_data, **kwargs):
    """
    Makes sure that every has less or equal to the expected filecount
    """
    passed = {}
    extra_files = {}
    expected_count = kwargs.get('expected_count', 1)
    for id_date, data in tqdm(input_data.items()):
        if len(data) > expected_count:
            extra_files[id_date] = data
        else:
            passed[id_date] = data
    return [{'final': passed, 'ext': 'passed'},
            {'final': extra_files, 'ext': 'extra_files'}]


def are_duplicates(file1, file2, shallow=True):
    """
    Checks if two files are duplicates.
        shallow: If True, only file signatures (type, size, modification time) 
                 are compared. If False, file contents are compared.
    """
    file1_path = file1['src']
    file2_path = file2['src']
    return filecmp.cmp(file1_path, file2_path, shallow)

def check_file_extension(file1, file2):
    """
    Checks if files have the same extention
    """
    ext1 = os.path.splitext(file1)[1].lower()
    ext2 = os.path.splitext(file2)[1].lower()
    return ext1 == ext2

def clean_duplicates(input_data, **kwargs):
    """
    Method to be added to pipeline
    """
    ## get_kwargs
    duplicate_root = kwargs.get('duplicate_root', '')

    duplicates = {}

    for id_date, data in tqdm(input_data.items()):
        unique = data
        for item1, item2 in combinations(data, 2):
            if are_duplicates(item1, item2):
                filename = os.path.basename(item2['src'])
                item2['dst'] = f'{duplicate_root}/{filename}'
                item2['duplicate_src'] = item1['src']
                duplicates[id_date] = item2
                data.remove(item2)
        input_data[id_date] = unique
    return [{'final': input_data, "ext": "passed"},
            {'final': duplicates, "ext": "duplicates"}]