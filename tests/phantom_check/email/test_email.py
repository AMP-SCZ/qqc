from phantom_check.email import send_out_qqc_results, send
from pathlib import Path
import pandas as pd
pd.set_option('max_rows', 5000)


def test_send_out_qqc_results():
    root_dir = Path('/data/predict/kcho/flow_test/MRI_ROOT')
    qqc_out_dir = root_dir / 'derivatives/quick_qc/sub-NL00000/ses-202112071'
    
    # send_out_qqc_results(qqc_out_dir, test=True)
    send_out_qqc_results(qqc_out_dir)

    # send(['kevincho@bwh.harvard.edu'], 'kc244@research.partners.org', 'ha', 'ho')
