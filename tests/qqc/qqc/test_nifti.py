import socket
import pandas as pd
import re
from pathlib import Path
from qqc.qqc.nifti import compare_volume_to_standard_all_nifti, \
    compare_volume_to_standard_all_nifti_test, is_nifti_16bit, \
    is_dwi_dir_16bit, is_session_dir_16bit, NoDwiException, \
    compare_bit_to_std, get_smoothness, get_smoothness_in_each_shell, \
    get_smoothness_in_each_shell_df, get_smoothness_all_nifti
from qqc.utils.writer import write_df_to_derivatives
from qqc.qqc.figures import create_smoothness_figure
from qqc.qqc.smoothness import highlight_smoothness_deviations
import multiprocessing
import logging
import numpy as np
import seaborn as sns

logger = logging.getLogger(__name__)

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


def test_compare_bit_to_std():
    print()
    input_dir = '/data/predict1/home/kcho/MRI_site_cert/qqc_output/rawdata/sub-GW00005/ses-202304131'
    standard_dir = '/data/predict1/data_from_nda/MRI_ROOT/rawdata/sub-SI05265/ses-202302011'
    qc_out_dir = Path('.')

    compare_bit_to_std(input_dir, standard_dir, qc_out_dir)


import time
import logging

def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Function {func.__name__} runtime: {end_time - start_time} seconds")
        return result
    return wrapper


@timing_decorator
def test_get_smoothness():
    print()
    input_nifti = '/data/predict1/data_from_nda/MRI_ROOT/rawdata/sub-BI02450/ses-202304111/dwi/sub-BI02450_ses-202304111_acq-176_dir-PA_run-1_dwi.nii.gz'
    input_nifti = '/data/predict1/data_from_nda/MRI_ROOT/rawdata/sub-BI02450/ses-202304111/dwi/sub-BI02450_ses-202304111_acq-176_dir-PA_run-1_sbref.nii.gz'

    fwhm_list, acf_list = get_smoothness(input_nifti)
    fwhm_combined = fwhm_list[-1]
    acf_combined = acf_list[-1]
    print(fwhm_list)
    print(acf_list)
    print(fwhm_combined)
    print(acf_combined)
    assert len(fwhm_list) == 4
    assert len(acf_list) == 4


@timing_decorator
def test_get_smoothness_separate_for_shell():
    print()
    input_nifti = '/data/predict1/data_from_nda/MRI_ROOT/rawdata/sub-BI02450/ses-202304111/dwi/sub-BI02450_ses-202304111_acq-176_dir-PA_run-1_dwi.nii.gz'
    # out_list = get_smoothness_in_each_shell(input_nifti)
    # print(out_list)
    df = get_smoothness_in_each_shell_df(input_nifti)
    print(df)
    subject = 'BI02450'
    session = '202304111'
    title = 'smoothness'
    write_df_to_derivatives(subject, session, df, title)


@timing_decorator
def test_get_smoothness_all_nifti():
    input_dir = '/data/predict1/data_from_nda/MRI_ROOT/rawdata/sub-BI02450/ses-202304111'
    def get_subject_session_from_input_dir(input_dir):
        subject = re.search('sub-(\w{2}\d{5})', input_dir).group(1)
        session = re.search('ses-(\d{9})', input_dir).group(1)
        return subject, session

    subject, session = get_subject_session_from_input_dir(input_dir)
    df = get_smoothness_all_nifti(input_dir)
    title = 'smoothness'
    write_df_to_derivatives(subject, session, df, title)


def get_smoothness_for_a_input_dir(input_dir):
    def get_subject_session_from_input_dir(input_dir):
        subject = re.search('sub-(\w{2}\d{5})', input_dir).group(1)
        session = re.search('ses-(\d{9})', input_dir).group(1)
        return subject, session

    subject, session = get_subject_session_from_input_dir(input_dir)
    
    GE = False
    if any([x in subject for x in ['CA', 'GA', 'KC']]):
        GE = True
    logger.info(f"GE machine: {GE}")
    
    df = get_smoothness_all_nifti(input_dir, GE=GE)
    title = 'smoothness'
    write_df_to_derivatives(subject, session, df, title)


def get_subject_session_from_input_dir(input_dir):
    subject = re.search('sub-(\w{2}\d{5})', input_dir).group(1)
    session = re.search('ses-(\d{9})', input_dir).group(1)
    return subject, session

@timing_decorator
def test_get_smoothness_all_dpacc(only_GE=False):
    rawdata_root = Path('/data/predict1/data_from_nda/MRI_ROOT/rawdata')

    pool = multiprocessing.Pool(processes=8)
    # Store the results of asynchronous calls.
    results = []

    def print_output(output):
        print(output)

    for input_dir in rawdata_root.glob('sub-*/ses-*'):
        subject = re.search('sub-(\w{2}\d{5})', str(input_dir)).group(1)
        session = re.search('ses-(\d{9})', str(input_dir)).group(1)
        
        if only_GE:
            ge_data = False
            for ge_site in ['GA', 'CA', 'KC']:
                if ge_site in subject:
                    ge_data = True
            if ge_data:
                pass
            else:
                continue
                    
        
        print(input_dir)
        mri_root = '/data/predict1/data_from_nda/MRI_ROOT'
        qqc_out_path = Path(mri_root) / \
                f'derivatives/quick_qc/sub-{subject}/ses-{session}'
        title = 'smoothness'
        df_out = qqc_out_path / f'{title}.csv'
        if df_out.is_file():
            print('done')
            # continue

        result = pool.apply_async(get_smoothness_for_a_input_dir,
                args=(str(input_dir),), callback=print_output)
        results.append(result)

    # Close the pool and wait for all processes to finish.
    pool.close()
    pool.join()

def print_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    
    # Create console handler and set level to INFO
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Add formatter to console handler
    ch.setFormatter(formatter)
    
    # Add console handler to logger
    logger.addHandler(ch)
    
    return logger


@timing_decorator
def test_load_smoothness_ampscz():
    nifti_session_dir = '/data/predict1/data_from_nda/MRI_ROOT/rawdata/sub-BI02450/ses-202304111'
    fig_out = 'test.png'
    create_smoothness_figure(nifti_session_dir, fig_out)
    df_ses_checked = highlight_smoothness_deviations(nifti_session_dir)
    print(df_ses_checked)

def run_and_save(nifti_session_dir, outcsv):
    smoothness_df = get_smoothness_all_nifti(nifti_session_dir)
    smoothness_df.to_csv(outcsv)

@timing_decorator
def test_running_smoothness_on_all_available_data():
    mri_root = Path('/data/predict1/data_from_nda/MRI_ROOT')
    rawdata_root = mri_root / 'rawdata'
    qqc_out_root = mri_root / 'derivatives/quick_qc'

    pool = multiprocessing.Pool(processes=8)
    # Store the results of asynchronous calls.
    results = []

    def print_output(output):
        print(output)

    for qc_out_dir in qqc_out_root.glob('sub*/ses*'):
        logger.info(qc_out_dir)
        fig_out = qc_out_dir / 'smoothness.png'
        session = qc_out_dir.name
        subject = qc_out_dir.parent.name
        # if not subject == 'sub-IR01762':
            # continue
        nifti_session_dir = rawdata_root / subject / session
        smoothness_csv = qc_out_dir / 'smoothness.csv'
        if not smoothness_csv.is_file():
            # smoothness_df = get_smoothness_all_nifti(nifti_session_dir)
            # smoothness_df.to_csv(qc_out_dir / 'smoothness.csv')
            out_csv = qc_out_dir / 'smoothness.csv'
            result = pool.apply_async(run_and_save,
                    args=(str(nifti_session_dir), str(out_csv)),
                    callback=print_output)
            results.append(result)

    # Close the pool and wait for all processes to finish.
    pool.close()
    pool.join()
        # continue

        # logger.info(f'{subject} {session} Smoothness check')
        # smoothness_fig_out = qc_out_dir / 'smoothness.png'
        # create_smoothness_figure(nifti_session_dir, smoothness_fig_out)

        # df_ses_checked = highlight_smoothness_deviations(nifti_session_dir)
        # smoothness_check_out = qc_out_dir / 'smoothness_check.csv'
        # df_ses_checked.reset_index(drop=True).to_csv(smoothness_check_out)


def test_get_smoothness_with_error():
    nifti_loc = '/data/predict1/data_from_nda/MRI_ROOT/rawdata/sub-IR01762/ses-202212131/anat/sub-IR01762_ses-202212131_rec-norm_run-1_T1w.nii.gz'
    smoothness_tuple = get_smoothness(nifti_loc)
    print(smoothness_tuple)



if __name__ == '__main__':
    only_GE = True
    logger = print_logger('test_nifti')
    logger.info('Starting test_get_smoothness_all_dpacc')
    test_get_smoothness_all_dpacc(only_GE=only_GE)
    logger.info('Finished test_get_smoothness_all_dpacc')
