from pathlib import Path
from qqc.qqc.mriqc import run_mriqc_on_data, \
        remove_DataSetTrailingPadding_from_json_files


def test_run_preproc():
    root_dir = Path('/data/predict/kcho/flow_test/MRI_ROOT')
    rawdata_dir = root_dir / 'rawdata'
    subject_id = 'sub-NL00000'
    session_id = 'ses-202112071'
    mriqc_outdir_root = root_dir / 'derivatives/mriqc'

    run_mriqc_on_data(
            rawdata_dir,
            subject_id,
            session_id,
            mriqc_outdir_root,
            bsub=True)


def test_remove_DSTP_from_json():
    root_dir = Path('/data/predict/data_from_nda_dev/MRI_ROOT')
    rawdata_dir = root_dir / 'rawdata'
    subject_id = 'sub-AD00001'
    session_id = 'ses-202109061'

    root_dir = Path('/data/predict/phantom_human_pilot')
    rawdata_dir = root_dir / 'rawdata'
    subject_id = 'sub-PrescientAdelaideSkyra'
    session_id = 'ses-humanpilot'

    remove_DataSetTrailingPadding_from_json_files(
            rawdata_dir, subject_id, session_id)


def test_after_removing_DSTP_from_json():
    root_dir = Path('/data/predict/data_from_nda_dev/MRI_ROOT')
    rawdata_dir = root_dir / 'rawdata'
    subject_id = 'sub-AD00001'
    session_id = 'ses-202109061'
    mriqc_outdir_root = root_dir / 'derivatives/mriqc'

    remove_DataSetTrailingPadding_from_json_files(
            rawdata_dir, subject_id, session_id)

    run_mriqc_on_data(
            rawdata_dir,
            subject_id,
            session_id,
            mriqc_outdir_root,
            bsub=True)



def test_calgary_GA_oct():
    root_dir = Path('/data/predict/phantom_data/kcho/GE_experiment/MRI_root')
    rawdata_dir = root_dir / 'rawdata'
    subject_id = 'sub-Calgary'
    session_id = 'ses-Oct'
    mriqc_outdir_root = root_dir / 'derivatives/mriqc'

    run_mriqc_on_data(
            rawdata_dir,
            subject_id,
            session_id,
            mriqc_outdir_root,
            bsub=True)

    subject_id = 'sub-GA'
    session_id = 'ses-Oct'

    run_mriqc_on_data(
            rawdata_dir,
            subject_id,
            session_id,
            mriqc_outdir_root,
            bsub=True)

