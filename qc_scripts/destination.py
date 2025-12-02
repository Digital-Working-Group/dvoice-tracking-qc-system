"""
destination.py
writes destinations for passed files
"""
import os
import re
from tqdm import tqdm

def standardize_filename(match_groups, ext):
    """
    Standardizes the filename for the destination based on the information
    extracted from the source filename.
    """
    id_type = match_groups[0].upper() + match_groups[1].zfill(2)
    pid = match_groups[2].zfill(5)
    date = match_groups[3]
    tech_id = match_groups[4]
    location = match_groups[5].lower()
    return f'{id_type}_{pid}_{date}_{tech_id}_{location}{ext}'

def dst_filename(filepath, filename_prefix=None):
    """
    Makes sure that the filename is in the correct format 
    """
    pattern = re.compile(r'([A-Za-z]{2})(\d{1,2})_(\d{4,5})_(\d{8})_(\d{3,4})_(remote|in-person)', flags=re.IGNORECASE)
    dir_path, filename = os.path.split(filepath)
    name, ext = os.path.splitext(filename)

    match = pattern.search(name)
    if not match:
        raise ValueError("Filename does not contain the expected pattern")

    groups = match.groups()
    corrected_name = standardize_filename(groups, ext)
    if filename_prefix is not None:
        corrected_name = f'{filename_prefix}_{corrected_name}'
    return os.path.join(dir_path, corrected_name)

def dst_helper(data):
    """
    build correct dst based on location
    calls dst_filename to correct the filename to the correct format
    """
    dst_root = "passed_data/"
    for item in data:
        filename = os.path.basename(item['src'])
        dst = f"{dst_root}/{item['location']}/{item['idtype']}-{item['id']}/{item['id_date']}/{filename}"
        item["dst"] = dst_filename(dst)
    return data

def get_dst(input_data):
    """
    callable from the pipeline
    """
    for id_date, data in tqdm(input_data.items()):
        input_data[id_date] = dst_helper(data)
    return [{'final': input_data, "ext": "passed"}]

def get_src_dst(data, move_back=False, **__):
    """
    Getting src and dst for dictionary of a list of dictionaries
    """
    move_list = []
    for item in data:
        src, dst = item['src'], item['dst']
        if dst is None:
            return [[None, None, None]]
        if move_back:
            src = item['dst']
            dst = item['src']
            item['src'] = src
            item['dst'] = dst
        move_list.append([src, dst, item])
    return move_list
