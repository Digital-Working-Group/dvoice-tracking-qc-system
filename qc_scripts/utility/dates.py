"""
dates.py
Utility functions to help with date formatting
"""

from datetime import datetime

def get_date_string(date_input, date_format=None):
    """
    Convert a datetime object or a date string to 'YYYYMMDD' format
    """
    if isinstance(date_input, datetime):
        return date_input.strftime('%Y%m%d')
    if isinstance(date_input, str):
        try:
            if date_format:
                dt = datetime.strptime(date_input, date_format)
            else:
                # Try parsing with common formats
                for fmt in ('%Y%m%d', '%m/%d/%Y', '%d%m%Y'):
                    try:
                        dt = datetime.strptime(date_input, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    raise ValueError(f"String '{date_input}' is not a valid date format.")
            return dt.strftime('%Y%m%d')
        except Exception as e:
            raise ValueError(f"Could not parse date string: {e}")
    else:
        raise TypeError("Input must be a datetime object or a string.")