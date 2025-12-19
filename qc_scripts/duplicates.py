"""
duplicates.py
Methods for dealing with duplicate data
"""
import os
import filecmp
import hashlib
from collections import defaultdict
from tqdm import tqdm
import soundfile as sf

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

def file_hash(path):
    """
    Generate MD5 hash for a file
    """
    hasher = hashlib.md5()
    with open(path, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def get_duration(filepath):
    """
    Gets the duration of an audio file in seconds
    """
    try:
        with sf.SoundFile(filepath) as f:
            frames = len(f)
            samplerate = f.samplerate
            duration = frames / samplerate
        return duration
    except Exception as e:
        print(f"Error getting duration for {filepath}: {e}")
        return None

def are_duplicates(file1, file2, hash=False, duration=False, shallow=True):
    """
    Checks if two files are duplicates.
        shallow: If True, only file signatures (type, size, modification time) 
                 are compared. If False, file contents are compared.
    """
    file1_path = file1['src']
    file2_path = file2['src']
    ## default result is only filecmp
    result = filecmp.cmp(file1_path, file2_path, shallow)
    if hash is True:
        result = result and (file_hash(file1_path) == file_hash(file2_path))
    if duration is True:
        result = result and (get_duration(file1_path) != get_duration(file2_path))
    return result

def check_file_extension(file1, file2):
    """
    Checks if files have the same extension
    """
    ext1 = os.path.splitext(file1)[1].lower()
    ext2 = os.path.splitext(file2)[1].lower()
    return ext1 == ext2

def clean_duplicates(input_data, **kwargs):
    """
    Duplicate cleaning function for 2+ duplicates;
    Writes the destination for duplicate files.
    """
    duplicate_root = kwargs.get('duplicate_root', '')
    compare_hash = kwargs.get('compare_hash', True)
    compare_duration = kwargs.get('compare_duration', True)

    duplicates_output = defaultdict(list)

    for id_date, data in tqdm(input_data.items()):
        items = list(data)
        n = len(items)

        # Build duplicate using groups of duplicate files
        groups = []
        used = set()

        for i in range(n):
            if i in used:
                continue

            group = {i}
            for j in range(i + 1, n):
                if are_duplicates(items[i], items[j], hash=compare_hash, duration=compare_duration):
                    group.add(j)

            if len(group) > 1:
                used |= group # union of used and group
                groups.append(group)

        # Keep only first item in each group; mark rest as duplicates
        cleaned_items = items.copy()

        for group in groups:
            group = list(group)
            keep = group[0] ## keeping only the first item in each group
            for idx in group[1:]:
                item_dup = items[idx]
                filename = os.path.basename(item_dup['src'])
                item_dup['dst'] = f"{duplicate_root}/{filename}"
                item_dup['duplicate_src'] = items[keep]['src']
                duplicates_output[id_date].append(item_dup)

                # remove from cleaned list
                if item_dup in cleaned_items:
                    cleaned_items.remove(item_dup)

        # update cleaned list
        input_data[id_date] = cleaned_items

    return [
        {"final": input_data, "ext": "passed"},
        {"final": duplicates_output, "ext": "duplicates"}
    ]
