"""
pattern.py
Holds scripts defining patterns 
"""

def example_pattern_data(): 
    """
    expected pattern for filenames
    ID type: 2 letters followed by 1-2 numbers
    ID: 4-5 numbers
    Date: YYYYMMDD
    Location: Remote vs In-person
    """
    pattern = r'([A-Za-z]{2}\d{1,2})_(\d{4,5})_(\d{8})_(\d{3,4})_(remote|in-person)'
    indices = [(0, 'idtype'), (1, 'id'), (2, 'date'), (3, 'tester_id'), (4, 'location')]
    return [(pattern, indices)]