"""
read_token_template.py
read_token.py is not version controlled because it contains the path to your REDCap token.
"""

def read_token():
    """
    get token
    """
    token_loc = "YOUR TOKEN HERE"
    with open(token_loc, 'r') as infile:
        for line in infile:
            return line.strip()
    print("Key not found")
    return None