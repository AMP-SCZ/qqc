from qqc.heudiconv_ctrl import run_heudiconv
from pathlib import Path

def test_heudiconv():
    bids_root = Path('/data/predict1/data_from_nda/MRI_ROOT')
    dicom_clearned_up_output = bids_root / 'sourcedata'
    qc_out_dir = Path(
            '/data/predict1/data_from_nda/MRI_ROOT/derivatives/quick_qc/sub-CA00152/ses-202301041')
    nifti_session_dir = Path('/data/predict1/data_from_nda/MRI_ROOT/rawdata')
    run_heudiconv(dicom_clearned_up_output,
                  'CA00152',
                  '202301041',
                  nifti_session_dir,
                  qc_out_dir,
                  False)

def test_heudiconv_2():
    bids_root = Path('/data/predict1/data_from_nda/MRI_ROOT')
    dicom_clearned_up_output = bids_root / 'sourcedata'
    qc_out_dir = Path(
            '/data/predict1/data_from_nda/MRI_ROOT/derivatives/quick_qc/sub-CA00152/ses-202301041')
    nifti_session_dir = Path('/data/predict1/data_from_nda/MRI_ROOT/rawdata')
    run_heudiconv(dicom_clearned_up_output,
                  'CA00229',
                  '202212121',
                  nifti_session_dir,
                  qc_out_dir,
                  False)
