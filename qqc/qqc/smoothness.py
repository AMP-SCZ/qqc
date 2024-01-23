import logging
import numpy as np
import pandas as pd
from pathlib import Path
from qqc.qqc.nifti import get_smoothness_all_nifti
from qqc.utils.files import get_subject_session_from_input_dir
logger = logging.getLogger(__name__)


def get_smoothness_ampscz(mri_root: Path = Path('/data/predict1/data_from_nda/MRI_ROOT'),
                          out_filename: Path = Path('/data/predict1/data_from_nda/MRI_ROOT/smoothness_ampscz.csv'),
                          force: bool = False) -> pd.DataFrame:
    qqc_root = mri_root / 'derivatives/quick_qc'
    rawdata_root = mri_root / 'rawdata'
    smoothness_csvs = qqc_root.glob('sub-*/ses-*/smoothness.csv')
    out_filename = 'smoothness_all.csv'

    if Path(out_filename).is_file() and force == False:
        smoothness_df = pd.read_csv(out_filename, index_col=0)
    else:
        smoothness_df = pd.DataFrame()
        for smoothness_csv in smoothness_csvs:
            df_tmp = pd.read_csv(smoothness_csv)
            df_tmp['subject'] = smoothness_csv.parent.parent.name
            df_tmp['session'] = smoothness_csv.parent.name
            smoothness_df = pd.concat([smoothness_df, df_tmp], ignore_index=True)
        smoothness_df.to_csv(out_filename)

    return smoothness_df


def simplify_smoothness_df(smoothness_df,
                           combined_only: bool = True,
                           remove_unexpected: bool = True,
                           site: str = None) -> pd.DataFrame:
    if combined_only:
        smoothness_df = smoothness_df[smoothness_df['var'] == 'combined']

    smoothness_df['site'] = smoothness_df.subject.str.split('-').str[1].str[:2]
    smoothness_df['modality'] = smoothness_df.nifti_file.str.extract('_(\w+).nii.gz')

    # remove unexpected files
    smoothness_df = smoothness_df[~smoothness_df.modality.isnull()]

    if remove_unexpected:
        for remove_str in ['heudiconv', 'fa']:
            smoothness_df = smoothness_df[~smoothness_df.modality.str.contains(remove_str)]

    # update diffusion
    smoothness_df['modality_orig'] = smoothness_df.modality.copy()
    update_dwi = lambda x: 'dwi' if 'dwi' in x else x
    smoothness_df['modality'] = smoothness_df.modality.apply(update_dwi)
    smoothness_df['modality_diff'] = smoothness_df.nifti_file.str.extract('acq-(\S+)_dir')
    diff_index = smoothness_df[smoothness_df.modality == 'dwi'].index
    smoothness_df.loc[diff_index, 'modality_orig'] = smoothness_df.loc[diff_index, 'modality'] + '_' + smoothness_df.loc[diff_index, 'modality_diff']

    # site selection
    if site is not None:
        smoothness_df = smoothness_df[smoothness_df.site == site]
    return smoothness_df


def summary_smoothness_table_for_a_session(
        subject, session,
        mri_root: Path = '/data/predict1/data_from_nda/MRI_ROOT'):
    '''Wrangle the table to highlight the session'''
    site = subject[:2]

    # get master table
    df_all = get_smoothness_ampscz(force=True)
    df_all = df_all.reset_index(drop=True)

    # clean up the master table
    df_all = df_all[df_all['var'] == 'combined']
    df_all['filename'] = df_all.nifti_file.copy()
    df_all['run_num'] = df_all.nifti_file.str.extract('run-(\d)')
    df_all['dir'] = df_all.nifti_file.str.extract('dir-(\w{2})')
    df_all['b-shell'] = df_all['b-shell'].fillna('x')

    # configure table for the site
    df_site = simplify_smoothness_df(df_all, site=site)
    df_site['level'] = 'site'

    # configure table for the study
    df_study = simplify_smoothness_df(df_all)
    df_study['level'] = 'study'

    # configure table for the sesion
    df_ses = df_all[
        (df_all.subject == f'sub-{subject}') &
        (df_all.session == f'ses-{session}')]
    print(df_ses)
    print(df_site)
    if len(df_ses) == 0:
        logger.info('No smoothness.csv file. Calculating smoothness...')
        nifti_session_dir = Path(mri_root) / 'rawdata' / \
                f'sub-{subject}' / f'ses-{session}'
        df_ses = get_smoothness_all_nifti(nifti_session_dir)
        df_ses = df_ses[df_ses['var'] == 'combined']
        df_ses['subject'] = f'sub-{subject}'
        df_ses['session'] = f'ses-{session}'
        df_ses['filename'] = df_ses.nifti_file.copy()
        df_ses['run_num'] = df_ses.nifti_file.str.extract('run-(\d)')
        df_ses['dir'] = df_ses.nifti_file.str.extract('dir-(\w{2})')
        df_ses['b-shell'] = df_ses['b-shell'].fillna('x')
    else:  # remove session data from site and study df
        df_ses = simplify_smoothness_df(df_ses)
        df_site.drop(df_ses.index, inplace=True)
        df_study.drop(df_ses.index, inplace=True)
    df_ses = simplify_smoothness_df(df_ses)
    df_ses['level'] = f'{subject}/{session}'

    # match filenames to be based on the session data
    map_dict = df_ses.set_index(
            ['modality', 'modality_orig', 'b-shell', 'run_num', 'dir']
            ).nifti_file.to_dict()
    df_site['filename'] = df_site.apply(lambda x: map_dict.get(
        (x['modality'], x['modality_orig'], x['b-shell'],
         x['run_num'], x['dir'])),
        axis=1)
    df_study['filename'] = df_study.apply(lambda x: map_dict.get(
        (x['modality'], x['modality_orig'], x['b-shell'],
         x['run_num'], x['dir'])),
        axis=1)
    
    # merge session, site, and study tables
    all_df = pd.concat([df_ses, df_site, df_study], ignore_index=True)

    # only select modality included in df_ses
    all_df = all_df[all_df['modality'].isin(df_ses.modality.unique())]

    # remove sub-modalities
    all_df = all_df[~all_df['modality'].str.contains('epi')]
    all_df = all_df[~all_df['modality'].str.contains('sbref')]

    all_df = all_df[~all_df.filename.isna()]
    all_df['filename'] = all_df.filename.str.split('.nii.gz').str[0]
    all_df['name'] = all_df['filename'].str.split('_').str[-1] + ' ' + all_df['filename'].str.split('_').str[-3] + ' ' + all_df['filename'].str.split('_').str[-2]

    # diffusion into different shells
    dwi_index = all_df[all_df['name'].str.contains('dwi')].index
    dwi_df = all_df.loc[dwi_index]
    dwi_df['b-shell'] = dwi_df['b-shell'].astype('int').astype(str)
    dwi_df['name'] = dwi_df['name'] + ' (b=' + dwi_df['b-shell'] + ')'
    all_df.loc[dwi_index] = dwi_df

    return all_df


def highlight_smoothness_deviations(
        rawdata_dir, dev_multiplier: float = 2) -> pd.DataFrame:
    subject, session = get_subject_session_from_input_dir(rawdata_dir)
    all_df = summary_smoothness_table_for_a_session(subject, session)
    all_df_melt = all_df.melt(
            id_vars=['name', 'subject', 'session',
                     'level', 'site', 'modality'],
            var_name='metric',
            value_name='value', value_vars=['FWHM', 'ACF'])

    df_site = all_df_melt.groupby('level').get_group('site')
    df_study = all_df_melt.groupby('level').get_group('study')
    df_ses = all_df_melt.groupby('level').get_group(f'{subject}/{session}')

    check_colnames = []
    for level_str, table in zip(['site', 'study'], [df_site, df_study]):
        check_colname = f'smoothness compared to {level_str}'
        for index, row in df_ses.iterrows():
            var = row['metric']
            table.to_csv('test.csv')
            try:
                df_tmp = table.groupby(['name', 'metric']).get_group(
                        (row['name'], var))
            except KeyError:
                # get table by modality
                df_tmp = table.groupby(['modality', 'metric']).get_group(
                        (row['modality'], var))

            mean = df_tmp['value'].mean()
            df_ses.loc[index, f"{level_str} mean"] = np.round(mean, 3)
            std = df_tmp['value'].std()
            df_ses.loc[index, f"{level_str} std"] = np.round(std, 3)
            threshold = mean + (std * dev_multiplier)

            if row['value'] < threshold:
                df_ses.loc[index, check_colname] = 'Pass'
            else:
                df_ses.loc[index, check_colname] = 'Warning'
        check_colnames.append(check_colname)

    col_order = df_ses.columns
    if (df_ses[check_colnames[0]] == 'Pass').all() and \
            (df_ses[check_colnames[1]] == 'Pass').all():
        pass_fail = 'Pass'
    else:
        pass_fail = 'Fail'

    # 'smoothness compared to study' is the last column in df_ses
    df_summary_df = pd.DataFrame({
        'name': ['Summary'],
        'smoothness compared to study': pass_fail})

    df_ses = pd.concat([df_summary_df, df_ses], ignore_index=True)
    df_ses = df_ses[col_order]
    df_ses.drop(['subject', 'session', 'modality'],
                axis=1, inplace=True)

    return df_ses

