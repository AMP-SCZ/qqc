from phantom_check.qqc.qqc_summary import qqc_summary, qqc_summary_for_dpdash
from pathlib import Path


def test_qqc_summary():

    root_dir = Path('/data/predict/kcho/flow_test/MRI_ROOT')
    qqc_out_dir = root_dir / 'derivatives/quick_qc/sub-SF11111/ses-202201261'

    root_dir = Path('/data/predict/kcho/flow_test/MRI_ROOT')
    qqc_out_dir = root_dir / 'derivatives/quick_qc/sub-NL00000/ses-202112071'

    qqc_summary(qqc_out_dir)


def test_qqc_summary_dpdash():

    root_dir = Path('/data/predict/kcho/flow_test/MRI_ROOT')
    qqc_out_dir = root_dir / 'derivatives/quick_qc/sub-SF11111/ses-202201261'

    # qqc_summary_for_dpdash(qqc_out_dir)

    qqc_out_dir = root_dir / 'derivatives/quick_qc/sub-NL00000/ses-202112071'
    qqc_summary_for_dpdash(qqc_out_dir)

    qqc_out_dir = root_dir / 'derivatives/quick_qc/sub-BM00016/ses-202111171'
    qqc_summary_for_dpdash(qqc_out_dir)
