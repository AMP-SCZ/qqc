from pathlib import Path
scripts_path = Path(__file__).parent.parent.parent / 'scripts'
import sys
sys.path.append(str(scripts_path))

from dicom_to_dpacc_bids import dicom_to_bids

raw_dicom_dir = Path(__file__).parent.parent.parent / 'data' / \
        'dicom_raw_source'



def test_dicom_to_bids():
    dicom_to_bids(raw_dicom_dir, 'test', 'testsubject', 'testsession')



