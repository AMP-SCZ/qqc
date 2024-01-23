from qqc.email import send_out_qqc_results, send_error
from pathlib import Path
import pandas as pd


def test_send_qqc():
    qc_out_dir = Path('/data/predict1/data_from_nda/MRI_ROOT/derivatives/quick_qc/sub-YA01508/ses-202206231')
    qc_out_dir = Path('/data/predict1/data_from_nda/MRI_ROOT/rawdata/sub-ME21922/ses-202209021')
    qc_out_dir = Path('/data/predict1/data_from_nda/MRI_ROOT/derivatives/quick_qc/sub-ME21922/ses-202209021')
    qc_out_dir = Path('/data/predict1/data_from_nda/MRI_ROOT/derivatives/quick_qc/sub-ME97666/ses-202212202')
    standard_dir = qc_out_dir
    run_sheet_df = pd.DataFrame()
    send_out_qqc_results(qc_out_dir, standard_dir,
                         run_sheet_df, [])
