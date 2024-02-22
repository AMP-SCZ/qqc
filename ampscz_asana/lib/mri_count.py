import os
import pandas as pd
from pathlib import Path
import logging
import re
from typing import List
from ampscz_asana.lib.server_scanner import get_all_mri_zip, get_all_eeg_zip, \
        get_most_recent_file, get_all_subjects_with_consent, \
        get_site_network_dict
from qqc.utils.dpdash import get_summary_included_ids
from typing import List

logger = logging.getLogger(__name__)


def count_and_make_it_available_for_dpdash(
        phoenix_paths: List[Path],
        mriflow_csv: Path,
        dpdash_outpath: Path,
        mriqc_dir: Path,
        modality: str = 'mri',
        sync_to_forms_id: bool = True,
        test: bool = False) -> None:
    """
    Counts the number of zip files corresponding to the given modality and
    their matching information from the mriflow_csv table. Adds QC measures
    from mriqc_dir to the zip_df. Creates a CSV file with the zip_df data
    and a pivot table for DPdash. Optionally syncs the data to forms-qc
    summary based on the sync_to_forms_id flag.

    Args:
        phoenix_paths (List[Path]): List of paths to the Phoenix directories.
        mriflow_csv (Path): Path to the mriflow_csv table.
        dpdash_outpath (Path): Path to the output directory for DPdash files.
        mriqc_dir (Path): Path to the directory containing MRI QC measures.
        modality (str, optional): Modality of the data. Defaults to 'mri'.
        sync_to_forms_id (bool, optional): Flag to sync data to forms-qc summary.
            Defaults to True.

    Returns:
        None
    """
    # create df of all zip files corresponding to the modality and their
    # matching information from the mriflow_csv table
    logger.info('Running get_mri_zip_df')
    zip_df = get_mri_zip_df(phoenix_paths, mriflow_csv, modality)

    # exclude cases to ignore
    ignore_path_list_txt = '/data/predict1/data_from_nda/MRI_ROOT/' \
                           'data_to_ignore.txt'
    ignore_df = pd.read_csv(ignore_path_list_txt, names=['zip_path'])
    zip_df = zip_df[~zip_df.zip_path.isin(ignore_df)]
    zip_df.to_csv(dpdash_outpath / f'{modality}_tmp_db.csv')

    if modality == 'mri':
        logger.info('Additional info will be added to zip_df')
        # For MRI, DPACC saves final QC measures for each session to the
        # mriqc_dir everyday. This QC information is added to zip_df
        mriqc_value_loc = get_most_recent_file(mriqc_dir)
        zip_df = add_qc_measures(zip_df, mriqc_value_loc)
        # get_mriqc_value_df_pivot_for_subject(zip_df, mriqc_dir)

        get_mriqc_value_df_pivot_for_subject(zip_df, dpdash_outpath,
                                             sync_to_forms_id, mriflow_csv)

    zip_df.to_csv(dpdash_outpath / f'{modality}_zip_db.csv')
    zip_df_pivot = get_mri_zip_df_pivot_for_subject(zip_df,
                                                    modality=modality)

    # only include subjects in forms-qc summary
    forms_summary_ids = get_summary_included_ids()
    # index is the AMP-SCZ ID
    if sync_to_forms_id:
        zip_df_pivot = zip_df_pivot[zip_df_pivot.index.isin(forms_summary_ids)]

    create_dpdash_zip_df_pivot(zip_df_pivot, dpdash_outpath,
                               modality, sync_to_forms_id, mriflow_csv)


def get_mri_zip_df(
        phoenix_paths: List[Path] = [
            Path('/data/predict1/data_from_nda/Pronet/PHOENIX'),
            Path('/data/predict1/data_from_nda/Prescient/PHOENIX')],
        mriflow_csv: Path =
            Path('/data/predict1/data_from_nda/MRI_ROOT/flow_check/'
                 'mri_data_flow.csv'),
        modality: str = 'mri',
        test: bool = False) -> pd.DataFrame:
    """
    Builds a database of existing MRI zip files.

    Args:
        phoenix_paths (List[Path]): List of Phoenix root paths.
        mriflow_csv (Path): Path to the MRI data flow CSV file.
        modality (str): Modality of the data ('mri' or 'eeg').

    Returns:
        pd.DataFrame: DataFrame containing information about the MRI zip files.
    """
    logger.debug('building database of existing MRI zip files')

    # MRI data flow info estimates timepoint based on the scan dates and the
    # run sheet files names. The csv is created by qqc/scripts/mriflow_check.py
    mri_flow_df = pd.read_csv(mriflow_csv, index_col=0)
    mri_flow_df = mri_flow_df[['subject', 'entry_date', 'run_sheet_num']]
    def quick_rename(x):
        if x == 'subject':
            return 'subject_id'
        elif x == 'entry_date':
            return 'scan_date_str'
        elif x == 'run_sheet_num':
            return 'timepoint'
        else:
            return x
    mri_flow_df.columns = [quick_rename(x) for x in mri_flow_df.columns]

    # select only sessions with information in the run sheet
    mri_flow_df.dropna(how='any', inplace=True)

    # initiate df with the existing zip files
    mri_zip_files = []
    for phoenix_root in phoenix_paths:
        if modality == 'mri':
            mri_zip_files += get_all_mri_zip(phoenix_root, test=test)
        elif modality == 'eeg':
            mri_zip_files += get_all_eeg_zip(phoenix_root)

    mri_zip_df = pd.DataFrame({'zip_path': mri_zip_files})
    mri_zip_df['network'] = mri_zip_df.zip_path.apply(str).str.contains(
        'Prescient').map({True: 'Prescient', False: 'Pronet'})
    get_sub_from_path = lambda x: x.parent.parent.name
    get_ses_from_path = lambda x: re.search(r'\d{4}_\d{1,2}_\d{1,2}_(\d+)',
            x.name).group(1) if re.search(r'\d{4}_\d{1,2}_\d{1,2}_(\d+)',
            x.name) else None
    mri_zip_df['subject_id'] = mri_zip_df.zip_path.apply(get_sub_from_path)
    mri_zip_df.to_csv('test.csv')
    mri_zip_df['session_num'] = mri_zip_df.zip_path.apply(get_ses_from_path
            )

    # ignore MRI files that does not follow SOP
    mri_zip_df = mri_zip_df[~mri_zip_df.session_num.isnull()]
    mri_zip_df['session_num'] = mri_zip_df['session_num'].astype('int64')
    mri_zip_df['file_name'] = mri_zip_df.zip_path.apply(lambda x: x.name)
    mri_zip_df['scan_date'] = mri_zip_df.file_name.str.extract(
        r'(\d{4}_\d{1,2}_\d{1,2})')
    mri_zip_df['scan_date_str'] = mri_zip_df['scan_date'].str.replace('_', '-')
    mri_zip_df['scan_date'] = pd.to_datetime(
        mri_zip_df.scan_date, format='%Y-%m-%d', errors='ignore').astype(str)

    # merge mri_flow_df information to include timepoint
    mri_zip_df['zip_path'] = mri_zip_df['zip_path'].apply(str)
    mri_zip_df = pd.merge(mri_zip_df,
                          mri_flow_df,
                          on=['subject_id', 'scan_date_str'],
                          how='left')

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
        # mri_zip_df[['subject_id', 'timepoint', 'network',
                    # 'session_num', 'session_id_raw']].drop_duplicates(),
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
    # mri_zip_df_pivot = mri_zip_df_pivot.loc[all_subjects]

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
    # eeg_zip_df_pivot = eeg_zip_df_pivot.loc[all_subjects]

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
        modality: str = 'mri',
        sync_to_forms_id: bool = False,
        mriflow_csv: Path = False) -> None:
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

    # match to dataflow table
    if sync_to_forms_id:
        import sys
        forms_summary_ids = get_summary_included_ids()
        ses_missing_in_mricount = [x for x in forms_summary_ids if x not in
                                   zip_df_pivot.subject_id.tolist()]
        zip_df_pivot_tmp = pd.DataFrame()
        for missing_subj in ses_missing_in_mricount:
            zip_df_pivot_tmp_tmp = pd.DataFrame({
                'subject_id': [missing_subj],
                f'baseline_followup_{modality}': '0',
                f'followup_followup_{modality}': '0'})
            zip_df_pivot_tmp = pd.concat([zip_df_pivot_tmp,
                                          zip_df_pivot_tmp_tmp])

        zip_df_pivot = pd.concat([
           zip_df_pivot,
           zip_df_pivot_tmp], ignore_index=True)
        # forms_summary_ids = get_summary_included_ids()
        # zip_df_pivot = zip_df_pivot[
                # zip_df_pivot.subject_id.isin(forms_summary_ids)]

        zip_df_pivot['day'] = range(1, len(zip_df_pivot)+1)
        # logger.warning(f'check the following cases: {ses_missing_in_mricount}')
        # sys.exit()

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
                    mriqc_value_loc: Path,
                    test: bool = False) -> pd.DataFrame:
    '''
    Adds MRI quality control measures to the input DataFrame.

    Args:
        mri_zip_df (pd.DataFrame): The DataFrame containing the MRI data.
        mriqc_value_loc (Path): The location of the MRIQC values file.

    Returns:
        pd.DataFrame: The updated DataFrame with MRIQC values added.
    '''
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
    mriqc_value_df['session_num'] = mriqc_value_df.session_id.str[-1].\
            astype('int')
    mri_zip_df['session_num'] = mri_zip_df.session_num.astype('int')


    mriqc_value_df['date'] = pd.to_datetime(mriqc_value_df['date_str'],
                                            format='%Y%m%d',
                                            errors='coerce')

    # mriqc_value_df = mriqc_value_df[~mriqc_value_df['date'].isna()]
    mriqc_value_df['scan_date_str'] = mriqc_value_df['date'].dt.strftime(
            '%Y-%m-%d')

    if test:
        print(mriqc_value_loc)
        return mriqc_value_df
    # include timepoint that is extracted from runsheets and included in the
    # mri_zip_df
    # actual extraction: get_run_sheet_df in ampscz_asana.lib.qc
    # csv creation: dpacc_count.py in qqc/scripts

    mriqc_value_df = pd.merge(
            mri_zip_df,
            mriqc_value_df,
            on=['subject_id', 'scan_date_str', 'session_num'],
            how='left')

    logger.debug('Number of subject in mriqc db after merge: '
                 f'{len(mriqc_value_df)}')

    # codify 'mriqc_val'
    mriqc_value_df['mriqc_int'] = mriqc_value_df['mriqc_val'].str.strip().map(
        {'Unusable': 0,
         'Partial': 1,
         'Pass': 2,
         'Pending': 3})

    return mriqc_value_df


def get_mriqc_value_df_pivot_for_subject(
        mriqc_value_df: pd.DataFrame,
        outpath: Path,
        sync_to_forms_id: bool = True,
        mriflow_csv: Path = False) -> pd.DataFrame:

    mriqc_value_df['mriqc_int'].fillna(3, inplace=True)

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

    mriqc_value_df_pivot = mriqc_value_df_pivot.reset_index()

    mriqc_value_df_pivot['day'] = 1
    mriqc_value_df_pivot['reftime'] = ''
    mriqc_value_df_pivot['timeofday'] = ''
    mriqc_value_df_pivot['weekday'] = ''

    mriqc_value_df_pivot = mriqc_value_df_pivot[[
        'day', 'reftime', 'timeofday', 'weekday', 'network',
        'timepoint', 'subject_id', 'mriqc_int']]

    # remove existing csv files
    logger.info(f'removing existing csv files in {outpath}')
    for csv_files in outpath.glob('*mriqcval-day*csv'):
        os.remove(csv_files)

    # add missing information from dataflow dataframe
    if sync_to_forms_id:
        mriflow_df = pd.read_csv(next(
            mriflow_csv.parent.glob('combined-AMP*.csv')))
        ses_in_mriqc = [(x.subject_id, x.timepoint) for index, x in
                        mriqc_value_df_pivot.iterrows()]
        ses_in_dataflow = [(x.subject_id, x.timepoint) for index, x in
                           mriflow_df.iterrows()]
        ses_missing_in_mriqc = [x for x in ses_in_dataflow
                                if x not in ses_in_mriqc]
        ses_missing_in_dataflow = [x for x in ses_in_mriqc
                                   if x not in ses_in_dataflow]
        logger.warning(f'check the following cases: {ses_missing_in_dataflow}')

        site_to_network_dict = pd.concat([
            mriflow_df['subject_id'].str[:2],
            mriflow_df['network']], axis=1
            ).drop_duplicates().set_index(
                'subject_id')['network'].to_dict()
        df_tmp = pd.DataFrame()
        for subject_id, timepoint in ses_missing_in_mriqc:
            dataflow_row = mriflow_df.set_index([
                'subject_id', 'timepoint']).loc[(subject_id, timepoint)]
            missing_info = dataflow_row['missing_info']
            site = subject_id[:2]
            network = site_to_network_dict[site]
            # 99 -> no data transferred to DPACC yet
            # 100 -> labelled as missing in database
            if missing_info == 1:
                mriqc_int = 100
            else:
                mriqc_int = 99
            df_tmp_tmp = pd.DataFrame({
                'subject_id': [subject_id],
                'timepoint': timepoint,
                'network': network,
                'mriqc_int': mriqc_int
            })
            df_tmp = pd.concat([df_tmp, df_tmp_tmp], ignore_index=True)
                                        
        mriqc_value_df_pivot = pd.concat([
            mriqc_value_df_pivot,
            df_tmp], ignore_index=True)

        logger.info('Removing any cases not included in the formsqc')
        forms_summary_ids = get_summary_included_ids()
        mriqc_value_df_pivot = mriqc_value_df_pivot[
                mriqc_value_df_pivot.subject_id.isin(forms_summary_ids)]

        mriqc_value_df_pivot['day'] = range(1, len(mriqc_value_df_pivot)+1)

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


def merge_zip_db_and_runsheet_db(zip_df_loc: Path,
                                 run_sheet_df_loc: Path,
                                 output_merged_zip: Path) -> None:
    """
    Merge zip database with the runsheet database.

    Args:
        zip_df_loc (Path): The file path of the zip database.
        run_sheet_df_loc (Path): The file path of the runsheet database.
        output_merged_zip (Path): The file path to save merged zip database.

    Returns:
        None
    """
    zip_df = pd.read_csv(zip_df_loc, index_col=0)

    def zip_df_rename(col: str) -> str:
        if col == 'subject_id':
            return 'subject'

        if col == 'scan_date_str':
            return 'entry_date'

        return col

    zip_df.columns = [zip_df_rename(x) for x in zip_df.columns]
    runsheet_df = pd.read_csv(run_sheet_df_loc, index_col=0)

    # outer merge on subject, entry_date, network, and session_num
    all_df = pd.merge(zip_df,
                      runsheet_df,
                      on=['subject', 'entry_date', 'network', 'session_num'],
                      how='outer')

    all_df.to_csv(output_merged_zip)


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


