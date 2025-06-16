"""
filepath.py
holds methods for helping build or modify filepaths
"""
import os

def append_to_end(filepath, str_to_append):
    """
    append something between a filepath and its extension
    """
    base, ext = os.path.splitext(filepath)
    return f"{base}{str_to_append}{ext}"
