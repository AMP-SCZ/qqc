import re
from typing import Tuple


def get_naming_parts_bids(file_name: str) -> Tuple[str]:
    '''Return (subject_name, session_name, rest_of_str) from BIDS file'''
    subject_name = re.search(r'sub-([A-Za-z0-9]+)_', file_name).group(1)
    session_name = re.search(r'ses-([A-Za-z0-9]+)_', file_name).group(1)
    json_suffix = file_name.split(session_name)[1]

    return subject_name, session_name, json_suffix


