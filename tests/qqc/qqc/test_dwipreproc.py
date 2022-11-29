from pathlib import Path
from qqc.qqc.dwipreproc import run_quick_dwi_preproc_on_data


def test_run_preproc():
    root_dir = Path('/data/predict/kcho/flow_test/MRI_ROOT')
    rawdata_dir = root_dir / 'rawdata'
    subject_id = 'sub-NL00000'
    session_id = 'ses-202112071'
    dwipreproc_outdir_root = root_dir / 'derivatives/dwipreproc'

    run_quick_dwi_preproc_on_data(
            rawdata_dir,
            subject_id,
            session_id,
            dwipreproc_outdir_root,
            bsub=True)



def test_run_preproc_OR():
    root_dir = Path('/data/predict/data_from_nda/MRI_ROOT')
    rawdata_dir = root_dir / 'rawdata'
    subject_id = 'sub-OR00697'
    session_id = 'ses-202208151'
    dwipreproc_outdir_root = root_dir / 'derivatives/dwipreproc'

    run_quick_dwi_preproc_on_data(
            rawdata_dir,
            subject_id,
            session_id,
            dwipreproc_outdir_root,
            bsub=True)



def test_run_preproc_LA():
    root_dir = Path('/data/predict/data_from_nda/MRI_ROOT')
    rawdata_dir = root_dir / 'rawdata'
    subject_id = 'sub-LA04513'
    session_id = 'ses-202208311'
    dwipreproc_outdir_root = root_dir / 'derivatives/dwipreproc'

    run_quick_dwi_preproc_on_data(
            rawdata_dir,
            subject_id,
            session_id,
            dwipreproc_outdir_root,
            bsub=False)


def test_run_preproc_SI():
    root_dir = Path('/data/predict/phantom_data/kcho/SI_data/MRI_root')
    rawdata_dir = root_dir / 'rawdata'
    subject_id = 'sub-SI00010'
    session_id = 'ses-202210141'
    dwipreproc_outdir_root = root_dir / 'derivatives/dwipreproc'

    run_quick_dwi_preproc_on_data(
            rawdata_dir,
            subject_id,
            session_id,
            dwipreproc_outdir_root,
            bsub=False)


def test_calgary_oct():
    root_dir = Path('/data/predict/phantom_data/kcho/GE_experiment/MRI_root')
    rawdata_dir = root_dir / 'rawdata'
    subject_id = 'sub-Calgary'
    session_id = 'ses-Oct'
    dwipreproc_outdir_root = root_dir / 'derivatives/dwipreproc'

    run_quick_dwi_preproc_on_data(
            rawdata_dir,
            subject_id,
            session_id,
            dwipreproc_outdir_root,
            bsub=True)

def test_GA_oct():
    root_dir = Path('/data/predict/phantom_data/kcho/GE_experiment/MRI_root')
    rawdata_dir = root_dir / 'rawdata'
    subject_id = 'sub-GA'
    session_id = 'ses-Oct'
    dwipreproc_outdir_root = root_dir / 'derivatives/dwipreproc'

    run_quick_dwi_preproc_on_data(
            rawdata_dir,
            subject_id,
            session_id,
            dwipreproc_outdir_root,
            bsub=True)
