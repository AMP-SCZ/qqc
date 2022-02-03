from pathlib import Path
from phantom_check.qqc.mriqc import run_mriqc_on_data


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



