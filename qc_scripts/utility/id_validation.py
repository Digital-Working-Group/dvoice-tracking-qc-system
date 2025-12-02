"""
id_validation.py
validate IDs
"""
import re

def get_pid(data, add_fid_idx='pid'):
    """
    if pid in data, get it.
    else, construct from idtype and id.
    """
    if 'pid' in data:
        fid = data['pid']
        idtype, _id = fid.split('-')
    else:
        idtype, _id = data['idtype'], data['id']
        if add_fid_idx is not None:
            data[add_fid_idx] = validate_idtype_and_id(idtype, _id)
    return validate_idtype_and_id(idtype, _id)

def validate_idtype_and_id(idtype, _id):
    """
    validate idtype and id string
    """
    idtype, _id = validate_idtype(idtype), validate_id(_id.zfill(5))
    if idtype is None or _id is None:
        return None
    return f"{idtype}-{_id}"

def validate_idtype(idtype):
    """
    check if idtype is valid, else raise assertion error;
    """
    pattern = r'^([A-Za-z]{2})(\d{1,2})$'
    match = re.fullmatch(pattern, idtype)
    if match:
        letters, digits = match.groups()
        digits = digits.zfill(2)
        if digits == '00':
            return None
        return letters.upper() + digits
    raise AssertionError(f"invalid idtype of {idtype}")

def validate_id(_id, remove_non_digits=True):
    """
    check if id is valid, else raise assertion error;
    """
    if remove_non_digits:
        _id = re.sub(r'[^0-9]', "", _id)
    length = len(_id)
    if length < 5:
        raise AssertionError(f"{_id} is < length 5;")
    elif length == 5:
        return _id
    raise AssertionError(f"{_id} is > length 5;")

def redcap_to_pid(redcap_id):
    """
    Convert to padded id and idtype. Do not allow the ID type to be '00
    """

    match = re.fullmatch(r'^([A-Za-z]{2}\d{1,2})(\d{5})$', redcap_id)
    if match:
        id_type, _id = match.groups()
        result = validate_idtype_and_id(id_type, _id)
        if result is not None:
            return result

    # Try 4-digit ID
    match = re.fullmatch(r'^([A-Za-z]{2}\d{1,2})(\d{4})$', redcap_id)
    if match:
        id_type, _id = match.groups()
        result = validate_idtype_and_id(id_type, _id)
        if result is not None:
            return result

    return None
