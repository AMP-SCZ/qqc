from ampscz_asana.lib.server_scanner import get_most_recent_file
import re
from pathlib import Path
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
