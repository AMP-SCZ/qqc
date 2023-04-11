import os
import pandas as pd
from pathlib import Path
import logging
import re
from typing import List
from ampscz_asana.lib.server_scanner import get_all_mri_zip, get_all_eeg_zip, \
        get_most_recent_file, get_all_subjects_with_consent, \
        get_site_network_dict

logger = logging.getLogger(__name__)


def count_and_make_it_available_for_dpdash(phoenix_paths: List[Path],
                                           mriflow_csv: Path,
                                           dpdash_outpath: Path,
                                           modality: str = 'mri') -> None:
    zip_df = get_mri_zip_df(phoenix_paths, mriflow_csv, modality)
    zip_df_pivot = get_mri_zip_df_pivot_for_subject(zip_df,
                                                    phoenix_paths,
                                                    modality)
    create_dpdash_zip_df_pivot(zip_df_pivot, dpdash_outpath, modality)


def get_mri_zip_df(
        phoenix_paths: List[Path] = [
            Path('/data/predict1/data_from_nda/Pronet/PHOENIX'),
            Path('/data/predict1/data_from_nda/Prescient/PHOENIX')],
        mriflow_csv: Path =
            Path('/data/predict1/data_from_nda/MRI_ROOT/flow_check/'
                 'mri_data_flow.csv'),
        modality: str = 'mri') -> pd.DataFrame:
    logger.debug('building database of existing MRI zip files')
    # data locations
    data_root = Path('/data/predict1/data_from_nda')

    # MRI data flow info estimates timepoint based on the scan dates and the
    # run sheet files names. The csv is created by qqc/scripts/mriflow_check.py
    mri_flow_df = pd.read_csv(mriflow_csv, index_col=0)
    mri_flow_df = mri_flow_df[['expected_mri_path', 'run_sheet_num']]
    mri_flow_df.columns = ['zip_path', 'timepoint']

    # initiate df with the existing zip files
    mri_zip_files = []
    for phoenix_root in phoenix_paths:
        if modality == 'mri':
            mri_zip_files += get_all_mri_zip(phoenix_root)
        elif modality == 'eeg':
            mri_zip_files += get_all_eeg_zip(phoenix_root)

    mri_zip_df = pd.DataFrame({'zip_path': mri_zip_files})
    mri_zip_df['network'] = mri_zip_df.zip_path.apply(str).str.contains(
        'Prescient').map({True: 'Prescient', False: 'Pronet'})
    get_sub_from_path = lambda x: x.parent.parent.name
    get_ses_from_path = lambda x: re.search(r'\d{4}_\d{1,2}_\d{1,2}_(\d)',
            x.name).group(1) if re.search(r'\d{4}_\d{1,2}_\d{1,2}_(\d)',
            x.name) else None
    mri_zip_df['subject_id'] = mri_zip_df.zip_path.apply(get_sub_from_path)
    mri_zip_df['session_num'] = mri_zip_df.zip_path.apply(get_ses_from_path)
    mri_zip_df['file_name'] = mri_zip_df.zip_path.apply(lambda x: x.name)
    mri_zip_df['scan_date'] = mri_zip_df.file_name.str.extract(
        r'(\d{4}_\d{1,2}_\d{1,2})')
    mri_zip_df['scan_date_str'] = mri_zip_df['scan_date'].str.replace('_', '-')
    mri_zip_df['scan_date'] = pd.to_datetime(
        mri_zip_df.scan_date, format='%Y-%m-%d', errors='ignore').astype(str)

    # merge mri_flow_df information to include timepoint
    mri_zip_df['zip_path'] = mri_zip_df['zip_path'].apply(str)
    mri_zip_df = pd.merge(mri_zip_df, mri_flow_df, on='zip_path', how='left')

    logger.debug(mri_zip_df)
    logger.debug(mri_zip_df[mri_zip_df.timepoint.isnull()])

    return mri_zip_df


def get_mri_zip_df_pivot_for_subject(
        mri_zip_df: pd.DataFrame,
        phoenix_paths: List[Path] = [
            Path('/data/predict1/data_from_nda/Pronet/PHOENIX'),
            Path('/data/predict1/data_from_nda/Prescient/PHOENIX')],
        modality: str = 'mri') -> pd.DataFrame:
    '''Pivot longitudinal mri_zip_df table for each subject'''
    logger.debug('Pivot mri_zip_df for each subject')

    # pivot table for subject_id and timepoint for counting MRI data
    mri_zip_df_pivot = pd.pivot_table(
        mri_zip_df[['subject_id', 'timepoint', 'network']].drop_duplicates(),
        index=['subject_id', 'network'],
        columns='timepoint',
        aggfunc=len).fillna(False)

    # clean up pivot table
    # 1 for baseline, 2 for 2 month follow up MRI
    mri_zip_df_pivot = mri_zip_df_pivot[[1, 2]]
    mri_zip_df_pivot[1] = pd.Categorical(mri_zip_df_pivot[1],
                                         categories=[0, 1],
                                         ordered=True)
    mri_zip_df_pivot[2] = pd.Categorical(mri_zip_df_pivot[2],
                                         categories=[0, 1],
                                         ordered=True)
    if modality == 'mri':
        mri_zip_df_pivot.columns = ['baseline_mri', 'followup_mri']
    elif modality == 'eeg':
        mri_zip_df_pivot.columns = ['baseline_eeg', 'followup_eeg']
    else:
        mri_zip_df_pivot.columns = ['baseline_mri', 'followup_mri']
    mri_zip_df_pivot = mri_zip_df_pivot.reset_index().set_index('subject_id')

    # include the subject included in the metadata into the pivot table
    all_subjects = []
    for phoenix_root in phoenix_paths:
        all_subjects += get_all_subjects_with_consent(phoenix_root)

    site_net_dict = get_site_network_dict(phoenix_paths)
    logger.debug(site_net_dict)
    for subject in all_subjects:
        if subject not in mri_zip_df_pivot.index.tolist():
            network = site_net_dict[subject[:2]]
            if modality == 'mri':
                mri_zip_df_pivot.loc[subject] = pd.Series({'network': network,
                                                           'baseline_mri':0,
                                                           'followup_mri': 0})
            elif modality == 'eeg':
                mri_zip_df_pivot.loc[subject] = pd.Series({'network': network,
                                                           'baseline_eeg':0,
                                                           'followup_eeg': 0})
            else:
                mri_zip_df_pivot.loc[subject] = pd.Series({'network': network,
                                                           'baseline_mri':0,
                                                           'followup_mri': 0})

    # restrict to subjects within metadata
    mri_zip_df_pivot = mri_zip_df_pivot.loc[all_subjects]

    return mri_zip_df_pivot


def get_eeg_zip_df_pivot_for_subject(
        eeg_zip_df: pd.DataFrame,
        phoenix_paths: List[Path] = [
            Path('/data/predict1/data_from_nda/Pronet/PHOENIX'),
            Path('/data/predict1/data_from_nda/Prescient/PHOENIX')]
        ) -> pd.DataFrame:
    '''Pivot longitudinal eeg_zip_df table for each subject'''
    logger.debug('Pivot eeg_zip_df for each subject')

    # pivot table for subject_id and timepoint for counting eeg data
    eeg_zip_df_pivot = pd.pivot_table(
        eeg_zip_df[['subject_id', 'timepoint', 'network']].drop_duplicates(),
        index=['subject_id', 'network'],
        columns='timepoint',
        aggfunc=len).fillna(False)

    # clean up pivot table
    # 1 for baseline, 2 for 2 month follow up eeg
    eeg_zip_df_pivot = eeg_zip_df_pivot[[1, 2]]
    eeg_zip_df_pivot[1] = pd.Categorical(eeg_zip_df_pivot[1],
                                         categories=[0, 1],
                                         ordered=True)
    eeg_zip_df_pivot[2] = pd.Categorical(eeg_zip_df_pivot[2],
                                         categories=[0, 1],
                                         ordered=True)
    eeg_zip_df_pivot.columns = ['baseline_eeg', 'followup_eeg']
    eeg_zip_df_pivot = eeg_zip_df_pivot.reset_index().set_index('subject_id')

    # include the subject included in the metadata into the pivot table
    all_subjects = []
    for phoenix_root in phoenix_paths:
        all_subjects += get_all_subjects_with_consent(phoenix_root)

    site_net_dict = get_site_network_dict(phoenix_paths)
    logger.debug(site_net_dict)
    for subject in all_subjects:
        if subject not in eeg_zip_df_pivot.index.tolist():
            network = site_net_dict[subject[:2]]
            eeg_zip_df_pivot.loc[subject] = pd.Series({'network': network,
                                                       'baseline_eeg':0,
                                                       'followup_eeg': 0})

    # restrict to subjects within metadata
    eeg_zip_df_pivot = eeg_zip_df_pivot.loc[all_subjects]

    return eeg_zip_df_pivot


def create_dpdash_mri_zip_df_pivot(mri_zip_df_pivot: pd.DataFrame,
        outpath: Path =
        Path('/data/predict1/data_from_nda/MRI_ROOT/eeg_mri_count')) -> None:
    '''Reformat and save mri_zip_df_pivot'''
    logger.debug('Reformat mri_zip_df_pivot for DPDash and save csv files')

    # create dpdash loadable table
    mri_zip_df_pivot = mri_zip_df_pivot.reset_index()
    mri_zip_df_pivot['day'] = 1
    mri_zip_df_pivot['reftime'] = ''
    mri_zip_df_pivot['timeofday'] = ''
    mri_zip_df_pivot['weekday'] = ''
    mri_zip_df_pivot = mri_zip_df_pivot[[
        'day', 'reftime', 'timeofday', 'weekday', 'network',
        'baseline_mri', 'followup_mri', 'subject_id']]

    # codify baseline and follow up MRI
    mri_zip_df_pivot['baseline_followup_mri'] = (
        mri_zip_df_pivot['baseline_mri'].astype(str) +
        mri_zip_df_pivot['followup_mri'].astype(str)
        ).map({'00': 0, '10': 1, '01': 2, '11': 3})

    # flush out
    for i in outpath.glob('*-mricount-day1to*csv'):
        os.remove(i)

    # all combined
    filename = f'combined-AMPSCZ-mricount-day1to{len(mri_zip_df_pivot)}.csv'
    mri_zip_df_pivot['day'] = range(1, len(mri_zip_df_pivot)+1)
    mri_zip_df_pivot.to_csv(outpath / filename, index=False)

    # for each network
    for network, table in mri_zip_df_pivot.groupby('network'):
        filename = f'combined-{network.upper()}-' \
                   f'mricount-day1to{len(table)}.csv'
        table['day'] = range(1, len(table)+1)
        table.to_csv(outpath / filename, index=False)

    # for each site
    mri_zip_df_pivot.drop('network', axis=1, inplace=True)
    mri_zip_df_pivot['site'] = mri_zip_df_pivot['subject_id'].str[:2]
    for site, table in mri_zip_df_pivot.groupby('site'):
        filename = f'combined-{site}-mricount-day1to{len(table)}.csv'
        table['day'] = range(1, len(table)+1)
        table.to_csv(outpath / filename, index=False)

    mri_zip_df_pivot.drop('site', axis=1, inplace=True)
    # for each subject
    for index, row in mri_zip_df_pivot.iterrows():
        subject = row['subject_id']
        site = subject[:2]
        outfile_path = outpath / f'{site}-{subject}-mricount-day1to1.csv'
        mri_zip_df_pivot.loc[[index]].to_csv(outfile_path, index=False)

    logger.debug('Reformat mri_zip_df_pivot for DPDash and save csv files')


def create_dpdash_zip_df_pivot(
        zip_df_pivot: pd.DataFrame,
        outpath: Path = '/data/predict1/data_from_nda/MRI_ROOT/eeg_mri_count',
        modality: str = 'mri') -> None:
    '''Reformat and save eeg_zip_df_pivot'''
    logger.debug('Reformat eeg_zip_df_pivot for DPDash and save csv files')
    outpath = Path(outpath)

    if modality not in ['eeg', 'mri']:
        logger.debug(f'{modality} is not supported by the function')
        return

    # create dpdash loadable table
    zip_df_pivot = zip_df_pivot.reset_index()
    zip_df_pivot['day'] = 1
    zip_df_pivot['reftime'] = ''
    zip_df_pivot['timeofday'] = ''
    zip_df_pivot['weekday'] = ''
    zip_df_pivot = zip_df_pivot[[
        'day', 'reftime', 'timeofday', 'weekday', 'network',
        f'baseline_{modality}',
        f'followup_{modality}',
        'subject_id']]

    # codify baseline and follow up eeg
    zip_df_pivot[f'baseline_followup_{modality}'] = (
        zip_df_pivot[f'baseline_{modality}'].astype(str) +
        zip_df_pivot[f'followup_{modality}'].astype(str)
        ).map({'00': 0, '10': 1, '01': 2, '11': 3})

    # flush out
    for i in outpath.glob(f'*-{modality}count-day1to*csv'):
        os.remove(i)

    # all combined
    filename = f'combined-AMPSCZ-{modality}count-day1to{len(zip_df_pivot)}.csv'
    zip_df_pivot['day'] = range(1, len(zip_df_pivot)+1)
    zip_df_pivot.to_csv(outpath / filename, index=False)

    # for each network
    for network, table in zip_df_pivot.groupby('network'):
        filename = f'combined-{network.upper()}-' \
                   f'{modality}count-day1to{len(table)}.csv'
        table['day'] = range(1, len(table)+1)
        table.to_csv(outpath / filename, index=False)

    # for each site
    zip_df_pivot.drop('network', axis=1, inplace=True)
    zip_df_pivot['site'] = zip_df_pivot['subject_id'].str[:2]
    for site, table in zip_df_pivot.groupby('site'):
        filename = f'combined-{site}-{modality}count-day1to{len(table)}.csv'
        table['day'] = range(1, len(table)+1)
        table.to_csv(outpath / filename, index=False)

    zip_df_pivot.drop('site', axis=1, inplace=True)
    # for each subject
    for index, row in zip_df_pivot.iterrows():
        subject = row['subject_id']
        site = subject[:2]
        outfile_path = outpath / \
                f'{site}-{subject}-{modality}count-day1to1.csv'
        zip_df_pivot.loc[[index]].to_csv(outfile_path, index=False)

    logger.debug('Reformat zip_df_pivot for DPDash and save csv files')


def add_qc_measures(mri_zip_df: pd.DataFrame,
                    mriqc_value_loc: Path) -> pd.DataFrame:
    '''To zip file.debug df, add mriqc_value from google drive'''
    mriqc_value_df = pd.read_csv(mriqc_value_loc, index_col=0)
    logger.debug(f'Number of subject in mriqc db: {len(mriqc_value_df)}')

    mriqc_value_df.columns = ['session_id_raw', 'mriqc_val']
    mriqc_value_df['mriqc_val'] = mriqc_value_df['mriqc_val'].str.strip()

    # change empty 'mriqc_val' to pending
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
            '%Y-%m-%d')

    # include timepoint
    mriqc_value_df = pd.merge(
            mriqc_value_df,
            mri_zip_df[['subject_id', 'scan_date_str',
                        'timepoint', 'network']],
            on=['subject_id', 'scan_date_str'],
            how='right')

    logger.debug('Number of subject in mriqc db after merge: '
                 f'{len(mriqc_value_df)}')
    logger.debug('mriqc_value_df')
    logger.debug(mriqc_value_df)

    # codify 'mriqc_val'
    mriqc_value_df['mriqc_int'] = mriqc_value_df['mriqc_val'].str.strip().map(
        {'Unusable': 0, 'Partial': 1, 'Pass': 2, 'Pending': 3})

    return mriqc_value_df


def get_mriqc_value_df_pivot_for_subject(mriqc_value_df: pd.DataFrame,
                                         outpath: Path) -> pd.DataFrame:
    # pd.set_option('display.max_rows', 5000)
    drop_dup_mriqc_value_df = mriqc_value_df[
            ['subject_id', 'timepoint', 'mriqc_int', 'network']
            ].drop_duplicates()

    logger.debug('Number of subject in mriqc db after drop_dup: '
                 f'{len(drop_dup_mriqc_value_df)}')

    mriqc_value_df_pivot = pd.pivot_table(
        drop_dup_mriqc_value_df,
        index=['subject_id', 'timepoint', 'network'],
        values='mriqc_int')
    logger.debug('Number of subject in mriqc db after pivot: '
                 f'{len(mriqc_value_df_pivot)}')
    logger.debug(mriqc_value_df_pivot)

    mriqc_value_df_pivot = mriqc_value_df_pivot.reset_index()

    mriqc_value_df_pivot['day'] = 1
    mriqc_value_df_pivot['reftime'] = ''
    mriqc_value_df_pivot['timeofday'] = ''
    mriqc_value_df_pivot['weekday'] = ''

    mriqc_value_df_pivot = mriqc_value_df_pivot[[
        'day', 'reftime', 'timeofday', 'weekday', 'network',
        'timepoint', 'subject_id', 'mriqc_int']]

    logger.debug('mriqc_value_df_pivot')
    logger.debug(mriqc_value_df_pivot)

    # remove existing csv files
    for csv_files in outpath.glob('*mriqcval-day*csv'):
        os.remove(csv_files)

    # all combined
    filename = f'combined-AMPSCZ-mriqcval-day1to{len(mriqc_value_df_pivot)}.csv'
    mriqc_value_df_pivot['day'] = range(1, len(mriqc_value_df_pivot)+1)
    mriqc_value_df_pivot.to_csv(outpath / filename, index=False)

    # for each network
    for network, table in mriqc_value_df_pivot.groupby('network'):
        filename = f'combined-{network.upper()}-' \
                   f'mriqcval-day1to{len(table)}.csv'
        table['day'] = range(1, len(table)+1)
        table.to_csv(outpath / filename, index=False)

    # for each site
    mriqc_value_df_pivot.drop('network', axis=1, inplace=True)
    mriqc_value_df_pivot['site'] = mriqc_value_df_pivot['subject_id'].str[:2]
    for site, table in mriqc_value_df_pivot.groupby('site'):
        filename = f'combined-{site}-mriqcval-day1to{len(table)}.csv'
        table['day'] = range(1, len(table)+1)
        table.to_csv(outpath / filename, index=False)

    mriqc_value_df_pivot.drop('site', axis=1, inplace=True)

    # for each subject
    for subject, table in mriqc_value_df_pivot.groupby('subject_id'):
        site = subject[:2]
        outfile_path = outpath / \
                f'{site}-{subject}-mriqcval-day1to{len(table)}.csv'
        table.to_csv(outfile_path, index=False)

    logger.debug('Reformat mriqc_value_df_pivot for DPDash and save csv files')



def note_used():
    for index, row in mri_zip_df[mri_zip_df.timepoint.isnull()].iterrows():
        logger.debug(f"{row['subject_id']}/{row['scan_date']}")
        other_files = list(Path(row['zip_path']).parent.glob('*.zip'))
        for file in other_files:
            logger.debug(f'\t{file.name}')


if __name__ == '__main__':
    zip_df = get_mri_zip_df()
    no_timepoint = zip_df[zip_df['timepoint'].isnull()]
    print(zip_df)
    print(no_timepoint)
