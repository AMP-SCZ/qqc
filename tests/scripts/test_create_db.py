from pathlib import Path
scripts_path = Path(__file__).parent.parent.parent / 'scripts'
import sys
import re
sys.path.append(str(scripts_path))

from qqc.qqc.dicom import is_enhanced, is_xa30


def test_create_db():
    pass
