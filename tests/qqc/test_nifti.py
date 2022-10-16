from qqc.qqc.nifti import compare_volume_to_standard_all_nifti
from pathlib import Path


def test_compare_data_to_standard_all_nifti():
    input_dir = '/data/predict/phantom_data/kcho/GE_experiment/GE_Sept/BIDS/rawdata/sub-GE/ses-sept'
    standard_dir = '/data/predict/data_from_nda_dev/MRI_ROOT/rawdata/sub-AD00001/ses-202109061'
    qc_out_dir = Path('/data/predict/phantom_data/kcho/GE_experiment/GE_Sept/BIDS/derivatives/quick_qc/sub-GE/ses-sept')
    compare_volume_to_standard_all_nifti(input_dir, standard_dir, qc_out_dir)

