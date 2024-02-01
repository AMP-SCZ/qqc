import re
import sys
from pathlib import Path

orig_paths = sys.path
new_paths = [x for x in orig_paths if 'qqc' not in x]
CURRENT_FILE = Path(__file__)
qqc_root = CURRENT_FILE.parent.parent.parent.parent
sys.path = new_paths + [str(qqc_root)]

from ampscz_asana.lib.server_scanner import get_most_recent_file, \
        get_subject_timepoint, return_matching_visit_status, \
        get_visit_df
import pandas as pd
from datetime import datetime


def test_get_most_recent_file():
    data_root = Path('/data/predict1/data_from_nda')
    root = data_root / 'MRI_ROOT/derivatives/google_qc'
    most_recent_file = get_most_recent_file(root)
    today = datetime.today()
    
    assert str(today.year) in most_recent_file.name
    assert str(today.month) in most_recent_file.name

    try:
        assert str(today.day) in most_recent_file.name
    except:
        assert str(today.day - 1) in most_recent_file.name


def test_get_subject_timepoint():
    visit_df = get_visit_df()
    subject_id = 'MA13030'
    visit_stat = get_subject_timepoint(visit_df, subject_id)
    assert len(visit_stat) == 2


def test_return_matching_visit_status():
    subject_ids = ['MA13030', 'PV18146', 'CM18195']
    subject_visit_dict = return_matching_visit_status(subject_ids)
    assert type(subject_visit_dict) == dict
    assert len(list(subject_visit_dict.values())[0]) == 2
    assert len(subject_visit_dict) == len(subject_ids)

    print(subject_visit_dict)

    subject_df = pd.DataFrame({'subject': ['MA13030', 'PV18146', 'CM18195']})
    subject_visit_dict = return_matching_visit_status(subject_df.subject)
    assert type(subject_visit_dict) == dict
    assert len(list(subject_visit_dict.values())[0]) == 2
    assert len(subject_visit_dict) == len(subject_df)
    subject_df['visit_status_string'] = subject_df['subject'].map(
            subject_visit_dict).str[0]

    print(subject_df)


