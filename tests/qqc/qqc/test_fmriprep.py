from pathlib import Path
from qqc.qqc.fmriprep import run_fmriprep_on_data


def test_run_preproc():
    root_dir = Path('/data/predict/kcho/flow_test/MRI_ROOT')
    rawdata_dir = root_dir / 'rawdata'
    subject_id = 'sub-NL00000'
    session_id = 'ses-202112071'
    fmriprep_outdir_root = root_dir / 'derivatives/fmriprep'
    fs_outdir_root = root_dir / 'derivatives/freesurfer'

    run_fmriprep_on_data(
            rawdata_dir,
            subject_id,
            session_id,
            fmriprep_outdir_root,
            fs_outdir_root=fs_outdir_root)


def test_run_preproc_real_participant():
    root_dir = Path('/data/predict/data_from_nda/MRI_ROOT')
    rawdata_dir = root_dir / 'rawdata'
    subject_id = 'sub-OR00697'
    session_id = 'ses-202208151'
    fmriprep_outdir_root = root_dir / 'derivatives/fmriprep'
    fs_outdir_root = root_dir / 'derivatives/freesurfer'

    run_fmriprep_on_data(
        rawdata_dir,
        subject_id,
        session_id,
        fmriprep_outdir_root,
        fs_outdir_root=fs_outdir_root)


def test_after_removing_DSTP_from_json():
    root_dir = Path('/data/predict/data_from_nda_dev/MRI_ROOT')
    rawdata_dir = root_dir / 'rawdata'
    subject_id = 'sub-AD00001'
    session_id = 'ses-202109061'
    fmriprep_outdir_root = root_dir / 'derivatives/fmriprep'
    fs_outdir_root = root_dir / 'derivatives/freesurfer'

    run_fmriprep_on_data(
        rawdata_dir,
        subject_id,
        session_id,
        fmriprep_outdir_root,
        fs_outdir_root=fs_outdir_root)
