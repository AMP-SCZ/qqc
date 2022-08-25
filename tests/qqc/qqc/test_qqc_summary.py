from qqc.qqc.qqc_summary import qqc_summary, qqc_summary_for_dpdash
from qqc.qqc.qqc_summary import create_dpdash_settings
from pathlib import Path
import json
import pandas as pd
import re


def test_qqc_summary():

    root_dir = Path('/data/predict/kcho/flow_test/MRI_ROOT')
    qqc_out_dir = root_dir / 'derivatives/quick_qc/sub-SF11111/ses-202201261'

    root_dir = Path('/data/predict/kcho/flow_test/MRI_ROOT')
    qqc_out_dir = root_dir / 'derivatives/quick_qc/sub-NL00000/ses-202112071'

    root_dir = Path('/data/predict/data_from_nda/MRI_ROOT')
    qqc_out_dir = root_dir / 'derivatives/quick_qc/sub-OR00697/ses-202208151'
    df = qqc_summary(qqc_out_dir)
    print()
    print(df)



def test_qqc_summary_dpdash():

    root_dir = Path('/data/predict/kcho/flow_test/MRI_ROOT')
    qqc_out_dir = root_dir / 'derivatives/quick_qc/sub-SF11111/ses-202201261'

    # qqc_summary_for_dpdash(qqc_out_dir)

    # qqc_out_dir = root_dir / 'derivatives/quick_qc/sub-NL00000/ses-202112071'
    # qqc_summary_for_dpdash(qqc_out_dir)

    import pandas as pd
    pd.set_option('max_columns', 50)
    qqc_out_dir = root_dir / 'derivatives/quick_qc/sub-BM00016/ses-202111171'
    qqc_summary_for_dpdash(qqc_out_dir)

    qqc_out_dir = root_dir / 'derivatives/quick_qc/sub-SF11111/ses-202201261'
    qqc_summary_for_dpdash(qqc_out_dir)


def test_the_new_qqc_summary_for_dpdash():
    root_dir = Path('/data/predict/data_from_nda/MRI_ROOT')
    # qqc_out_dir = root_dir / 'derivatives/quick_qc/sub-YA01508/ses-202206231'
    qqc_out_dir = root_dir / 'derivatives/quick_qc/sub-OR00697/ses-202208151'
    qqc_summary_for_dpdash(qqc_out_dir)


def test_creat_dpdash_settings():
    root_dir = Path('/data/predict/data_from_nda/MRI_ROOT')
    qqc_out_dir = root_dir / 'derivatives/quick_qc/sub-OR00697/ses-202208151'
    qqc_summary_df = qqc_summary(qqc_out_dir)
    # Pass -> 1, Fail -> 0
    def relabel(val):
        if pd.isna(val):
            return val

        if val == 'Pass':
            return 1
        elif val == 'Fail':
            return 0
        elif val == 'Warning':
            return 2

        elif type(val) == float:
            return round(val, 2)
        else:
            return int(val)

    # replace 'Pass' to 1, 'Fail' to 0
    qqc_summary_df[qqc_summary_df.columns[0]] = qqc_summary_df[
            qqc_summary_df.columns[0]].apply(relabel)

    # columns required by DPDash
    header_df = pd.DataFrame({'day': [1],
                              'reftime': '',
                              'timeofday': '',
                              'weekday': ''}).T
    header_df.columns = qqc_summary_df.columns
    qqc_summary_df = pd.concat([header_df, qqc_summary_df]).T

    # DPDash requires day to start from 1
    qqc_summary_df['day'] = 1

    # remove scan order
    qqc_summary_df.drop('Scan order', axis=1, inplace=True)

    # ignore shim settings

    # remove spaces from column names
    qqc_summary_df.columns = [re.sub(' ', '_', x) for x in
                              qqc_summary_df.columns]

    mriqc_pretty = create_dpdash_settings(qqc_summary_df)
    with open('test_mriqc_pretty.json', 'w') as fp:
        json.dump(mriqc_pretty, fp, indent=2)
