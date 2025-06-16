"""
read.py
holds all utility methods for reading files 
"""
import os
import csv
import json
from collections import defaultdict

def json_load(filename):
     """
     open a json-like file object
     """
     with open(filename, 'r') as file:
          final = json.load(file)
     return final

def efficient_read(filename):
    """
    read a formatted text file;
    """
    final = {}
    with open(filename, 'r') as file:
        for line in file:
            line = line.rstrip('\n')
            line = line.split(':*')
            key = line[0]
            value = line[-1]
            final[key] = value
    return final

def read_dictionary_file(filename, **kwargs):
    """
    read a json or text dictionary file;
    """
    stop_after = kwargs.get('stop_after')
    _, ext = os.path.splitext(filename)
    if ext == '.txt':
        data = efficient_read(filename)
    elif ext == '.json':
        try:
            data = json_load(filename)
        except json.decoder.JSONDecodeError as error:
            print(f'filename: {filename}\n\n')
            raise error
    else:
        raise TypeError('{} is not of ext .txt or .json, cannot read'.format(filename))
    if stop_after is None:
        return data
    new_data = {}
    for idx, key in enumerate(data):
        if idx >= stop_after:
            return new_data
        new_data[key] = data[key]
    return new_data