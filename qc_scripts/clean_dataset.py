"""
clean_dataset.py
methods for accessing and updating the clean dataset
"""
import os
import shutil
import json
from tqdm import tqdm
from qc_scripts.utility.read import read_dictionary_file

def deduplicate_by_src(dict_list):
    """
    Takes in a list of dictionaries and keep only unique dictionaries 
    """
    seen = set()
    unique_dicts = []
    for d in dict_list:
        src = d.get('src')
        if src not in seen:
            seen.add(src)
            unique_dicts.append(d)
    return unique_dicts

def update_clean_dataset(input_data, **kwargs):
    """
    Takes in final result from the pipeline and adds it to the clean dataset
    """
    ## kwargs
    clean_dataset = kwargs.get('clean_dataset')

    ## Take in a filepath or data
    if isinstance(input_data, str):
        input_data = read_dictionary_file(input_data)

    ## make a copy of the current clean_dataset
    dir_name, filename = os.path.split(clean_dataset)
    name, ext = os.path.splitext(filename)
    copy_name = os.path.join(dir_name, f'{name}_previous{ext}')
    shutil.copy2(clean_dataset, copy_name)

    ## read clean_dataset
    updated_clean = read_dictionary_file(clean_dataset)

    ## add new data to the clean dataset 
    for id_date, data in tqdm(input_data.items()):
        if id_date not in updated_clean:
            updated_clean[id_date] = data
        else:
            if updated_clean[id_date] is None:
                updated_clean[id_date] = data
            else:
                updated_clean[id_date].extend(data)
                updated_clean[id_date]= deduplicate_by_src(updated_clean[id_date])
    
    ## Write over old clean dataset
    with open(clean_dataset, 'w', encoding='utf-8') as f:
        json.dump(updated_clean, f, indent=4)
    print(f'See {clean_dataset} for updated clean dataset.')