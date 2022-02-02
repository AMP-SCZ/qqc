from phantom_check.qqc.nifti import compare_volume_to_standard_all_nifti
import pandas as pd
from pathlib import Path
import socket


if socket.gethostname() == 'mbp16':
    raw_dicom_dir = Path(__file__).parent.parent.parent / 'data' / \
            'dicom_raw_source'

    standard_dir = Path(__file__).parent.parent.parent / 'data' / \
            'dicom_raw_source'
else:
    raw_dicom_dir = Path('/data/predict/phantom_data'
                         '/kcho/tmp/PHANTOM_20211022')
    standard_dir = Path('/data/predict/phantom_human_pilot/rawdata'
                        '/sub-ProNETUCLA/ses-humanpilot')


def test_compare_volume_to_standard_all_nifti():

    input_dir = '/data/predict/phantom_data/phantom_data_BIDS/sub-ProNETSeoul/ses-phantom'
    # standard_dir = standard_dir
    qc_out_dir = Path('.')

    compare_volume_to_standard_all_nifti(
            input_dir, standard_dir, qc_out_dir, False)

