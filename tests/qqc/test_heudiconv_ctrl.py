from qqc.heudiconv_ctrl import run_heudiconv
from pathlib import Path


def test_run_heudiconv():
    dicom_input_root = Path('/data/predict/phantom_data/site_data'
            '/ProNET_Calgary_GE/human_pilot/dicom/test/sourcedata')
    subject_name = 'CG'
    session_name = '1'
    nifti_root_dir = Path('/data/predict/phantom_data/site_data/'
                          'ProNET_Calgary_GE/human_pilot/dicom/test/rawdata')
    qc_out_dir = Path('/data/predict/phantom_data/site_data/'
                      'ProNET_Calgary_GE/human_pilot/dicom/test/'
                      'derivatives/quick_qc/sub-CG2/ses-1')

    qc_out_dir.mkdir(exist_ok=True, parents=True)

    # testing without distortion maps - manually removed to another dir
    # to different output dir
    run_heudiconv(dicom_input_root, subject_name, session_name,
                  nifti_root_dir, qc_out_dir)

# def test_print_s_for_UCLA():
    # dicom_input_root = Path('/data/predict/phantom_data/site_data'
            # '/ProNET_Calgary_GE/human_pilot/dicom/test/sourcedata')

    # # dicom_input_root = Path('/data/predict/kcho/flow_test/MRI_ROOT/sourcedata')
    # subject_name = 'UCLA'
    # session_name = '1'
    # nifti_root_dir = Path('/data/predict/phantom_data/site_data/'
                          # 'ProNET_Calgary_GE/human_pilot/dicom/test/rawdata4')
    # qc_out_dir = Path('/data/predict/phantom_data/site_data/'
                      # 'ProNET_Calgary_GE/human_pilot/dicom/test/'
                      # 'derivatives/quick_qc/sub-CG2/ses-1')

    # qc_out_dir.mkdir(exist_ok=True, parents=True)
    # # testing without distortion maps - manually removed to another dir
    # # to different output dir
    # run_heudiconv(dicom_input_root, subject_name, session_name,
                  # nifti_root_dir, qc_out_dir)


def test_run_heudiconv_on_jena():
    dicom_clearned_up_output = Path(
            '/data/predict/data_from_nda_dev/MRI_ROOT/sourcedata')
    subject_name = 'JE00052'
    session_name = '202202281'
    bids_rawdata_dir = 'test_rawdata'
    qc_out_dir = 'test_qc'

    run_heudiconv(dicom_clearned_up_output, subject_name,
                  session_name, bids_rawdata_dir, qc_out_dir)


def test_run_heudiconv_on_jena_xa30():
    dicom_clearned_up_output = Path(
            '/data/predict/data_from_nda_dev/MRI_ROOT/sourcedata')
    subject_name = 'JE00068'
    session_name = '202206282'
    bids_rawdata_dir = 'test_rawdata'
    qc_out_dir = 'test_qc'
    run_heudiconv(dicom_clearned_up_output, subject_name,
                  session_name, bids_rawdata_dir, qc_out_dir)


def test_run_heudiconv_on_t1_only_jena_xa30():
    dicom_clearned_up_output = Path(
            '/data/predict/phantom_data/kcho/devel_soft/qqc/tests/qqc/test_sourcedata')
    subject_name = 'JE00068'
    session_name = '202206282'
    bids_rawdata_dir = 'test_rawdata2'
    qc_out_dir = 'test_qc'
    run_heudiconv(dicom_clearned_up_output, subject_name,
                  session_name, bids_rawdata_dir, qc_out_dir)
