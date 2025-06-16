"""
errors.py
methods to help with error handling
"""
def on_error(os_error):
    """
    helper function to be called for os.walk(root,onerror=on_error)
    """
    print('>>> on_error START')
    print(os_error)
    raise os_error