from pathlib import Path
from phantom_check.qqc.dwipreproc import run_quick_dwi_preproc_on_data


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



