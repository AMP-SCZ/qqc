from ampscz_asana.lib.server_scanner import get_all_mri_zip, \
        get_most_recent_file
import pandas as pd
from pathlib import Path


def test_load():
    phoenix_root = Path('/data/predict1/data_from_nda/Pronet/PHOENIX')
    zip_files = get_all_mri_zip(phoenix_root, test=True)
    print(zip_files)
    pass


def test_mri_count():
    mriqc_dir = Path('/data/predict1/data_from_nda/MRI_ROOT/derivatives/google_qc')
    mriqc_value_loc = get_most_recent_file(mriqc_dir)
    mriqc_value_df = pd.read_csv(mriqc_value_loc, index_col=0)

    mriqc_value_df.columns = ['session_id_raw', 'mriqc_val']
    mriqc_value_df['mriqc_val'] = mriqc_value_df['mriqc_val'].str.strip()
    mriqc_value_df['mriqc_val'] = mriqc_value_df['mriqc_val'].fillna('Pending')

    ses_id_split = mriqc_value_df.session_id_raw.str.split('/')
    mriqc_value_df['subject_id'] = ses_id_split.str[0].str.split('-').str[1]
    mriqc_value_df['session_id'] = ses_id_split.str[1].str.split('-').str[1]
    mriqc_value_df['date_str'] = mriqc_value_df.session_id.str[:-1]
    mriqc_value_df['date'] = pd.to_datetime(mriqc_value_df['date_str'],
                                            format='%Y%m%d',
                                            errors='coerce')

    # mriqc_value_df = mriqc_value_df[~mriqc_value_df['date'].isna()]
    mriqc_value_df['scan_date_str'] = mriqc_value_df['date'].dt.strftime(
            '%Y-%m-%d', errors='ignore')

    # include timepoint
    mriqc_value_df = pd.merge(mriqc_value_df,
                              mri_zip_df[['subject_id', 'scan_date_str', 'timepoint']],
                              on=['subject_id', 'scan_date_str'],
                              how='left')


    # remove no marked up data
    # mriqc_value_df['mriqc_val'] = mriqc_value_df['mriqc_val'].fillna('Pending')
    mriqc_value_df = mriqc_value_df[~mriqc_value_df['mriqc_val'].isna()]
    # for mriqc_value_df
    mriqc_value_df['mriqc_int'] = mriqc_value_df['mriqc_val'].str.strip().map(
        {'Unusable': 0,
        'Partial': 1,
        'Pass': 2,
        'Pending': 3}
    )

    outpath = Path('/data/predict1/data_from_nda/MRI_ROOT/eeg_mri_count')

    mri_subject_dfs = pd.DataFrame()
    for subject, table in mriqc_value_df.groupby('subject_id'):
        site = subject[:2]
        table = table[~table.timepoint.isna()]
        if len(table) > 0:    
            table= table[['subject_id', 'timepoint', 'mriqc_int']]
            table = table.drop_duplicates()

            table_pivot = pd.pivot_table(table,
                                         index=['subject_id', 'timepoint'],
                                         values=['mriqc_int'],
                                         aggfunc=lambda x: str(x.iloc[0])).reset_index()
            # table_pivot.columns
            table_pivot.columns = ['subject_id', 'timepoint', 'mriqc_int']
            table_pivot['day'] = 1
            table_pivot['reftime'] = ''
            table_pivot['timeofday'] = ''
            table_pivot['weekday'] = ''

            table_pivot = table_pivot[['day', 'reftime', 'timeofday', 'weekday', 'subject_id', 'timepoint', 'mriqc_int']]
            mri_subject_dfs = pd.concat([mri_subject_dfs, table_pivot])
            
            table_pivot.to_csv(outpath / f'{site}-{subject}-mriqcval-day1to{len(table_pivot)}.csv')
