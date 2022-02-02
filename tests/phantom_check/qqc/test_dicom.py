from phantom_check.qqc.json import jsons_from_bids_to_df
from phantom_check.dicom_files import get_dicom_files_walk
from phantom_check.qqc.dicom import check_num_of_series, check_order_of_series
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


def test_cehck_num_order_of_series():
    df_full_std = jsons_from_bids_to_df(standard_dir).drop_duplicates()
    df_full_std.sort_values('series_num', inplace=True)

    df_full_input_file = Path('.df_full_input_csv')
    if df_full_input_file.is_file():
        df_full_input = pd.read_csv(df_full_input_file, index_col=0)
    else:
        df_full_input = get_dicom_files_walk(raw_dicom_dir, True)
        df_full_input.to_csv(df_full_input_file)

    num_check_df = check_num_of_series(df_full_input, df_full_std)
    order_check_df = check_order_of_series(df_full_input, df_full_std)

    print()
    print(num_check_df)
    print(order_check_df)
