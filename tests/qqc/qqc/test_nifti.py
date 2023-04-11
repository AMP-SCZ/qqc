from qqc.qqc.nifti import compare_volume_to_standard_all_nifti, \
    compare_volume_to_standard_all_nifti_test, is_nifti_16bit, \
    is_dwi_dir_16bit, is_session_dir_16bit, NoDwiException

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

def test_philips():
    root_dir = Path('/data/predict/kcho/philips/new_unzip/Philips_Copenhagen_20220908_test/BIDS')
    input_dir = root_dir / 'rawdata/sub-cp/ses-20220908'
    qc_out_dir = root_dir

    standard_dir = Path('/data/predict/data_from_nda/MRI_ROOT/rawdata/sub-YA01508/ses-202208261')
    standard_dir = Path('/data/predict/data_from_nda_dev/MRI_ROOT/rawdata/sub-AD00001/ses-202109061')
    # compare_volume_to_standard_all_nifti(input_dir, standard_dir, qc_out_dir)
    compare_volume_to_standard_all_nifti_test(input_dir, standard_dir, qc_out_dir)

def test_GE():
    ga = Path('/data/predict/phantom_data/kcho/GE_experiment/GA/dcm2niix_output')
    kcl = Path('/data/predict/phantom_data/kcho/GE_experiment/KCL/dcm2niix_output')
    standard_dir = Path('/data/predict/phantom_data/kcho/GE_experiment/GE_Sept/BIDS/rawdata/sub-GE/ses-sept')
    # compare_volume_to_standard_all_nifti(input_dir, standard_dir, qc_out_dir)
    compare_volume_to_standard_all_nifti_test(ga, standard_dir, ga)
    compare_volume_to_standard_all_nifti_test(kcl, standard_dir, kcl)


def test_XA30():
    input_dir = Path('/data/predict1/data_from_nda/MRI_ROOT/rawdata/sub-ME97666/ses-202212202')
    standard_dir = Path('/data/predict1/kcho/MRI_site_cert/qqc_output/rawdata/sub-LS/ses-202211071')
    # compare_volume_to_standard_all_nifti(input_dir, standard_dir, qc_out_dir)
    compare_volume_to_standard_all_nifti(input_dir, standard_dir, Path('prac'))



def test_16bit():
    mri_root = Path('/data/predict1/data_from_nda/MRI_ROOT')
    rawdata_root = mri_root / 'rawdata'
    nifti_roots = rawdata_root.glob('sub-*/ses-*')
    for nifti_root in nifti_roots:
        try:
            if is_session_dir_16bit(nifti_root):
                print('16bit', nifti_root)
            else:
                print('No 16bit', nifti_root)
        except NoDwiException:
            print('No DWI')
# def test_is_nifti_16bit():
    # diffusion_data

