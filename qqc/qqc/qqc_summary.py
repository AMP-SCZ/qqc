import pandas as pd
from pathlib import Path
import re
import os
from typing import Tuple, Union
import json
import numpy as np
import seaborn as sns


def get_summary_table_from_json_to_std(json_comp: Union[str, Path],
                                       colname: str = 'Series'):
    '''Summarize json comparison csv to be included in summary report

    Key arguments:
        json_comp: Path of a json comparison csv file, str or Path.
        colname: Name of the column in the summary table
    '''
    json_comp_df = pd.read_csv(json_comp)
    json_comp_df['series_num'] = json_comp_df.series_num.astype('Int64')
    json_comp_df.sort_values(by='series_num', inplace=True)

    json_comp_summary_df = pd.DataFrame(columns=[colname])
    gb = json_comp_df.groupby(['series_num', 'series_desc'], dropna=False)
    for (series_num, series_desc), table_upper in gb:

        # skip unmatched series
        if table_upper['input'].isnull().any() or \
                table_upper['std'].isnull().any():
            continue

        table_upper = table_upper[[
            'series_num', 'series_desc', 'index']].drop_duplicates()
        index = table_upper[table_upper['index'] != 'no_diff'].index

        val = ', '.join(table_upper.loc[index]['index'].unique())
        val_num = len(table_upper.loc[index]['index'])

        json_comp_summary_df.loc[series_num, 'Series'] = series_desc
        json_comp_summary_df.loc[series_num, 'Number of issues'] = int(val_num)
        json_comp_summary_df.loc[series_num, 'Issue in'] = val

    json_comp_summary_df = json_comp_summary_df.reset_index().set_index(
        'Series')
    if (json_comp_summary_df['Issue in'] == '').all():
        pass_fail = 'Pass'
    else:
        pass_fail = 'Fail'
    df_tmp = pd.DataFrame({'Issue in': [pass_fail]})
    df_tmp.index = ['Summary']

    json_comp_summary_df = pd.concat([df_tmp, json_comp_summary_df])
    json_comp_summary_df.columns = [
        'Issue in', 'Series Num', 'Number of issues']

    for i in ['Series Num', 'Number of issues']:
        json_comp_summary_df[i] = json_comp_summary_df[i].astype('Int64') \
                .astype(str).str.replace('<NA>', '')

    return json_comp_summary_df[['Series Num', 'Number of issues', 'Issue in']]


def qqc_summary_detailed(qqc_ss_dir: Path) -> pd.DataFrame:
    '''Summarize quick QC output into a single CSV file

    Key Arguments:
        qqc_ss_dir: quick QC location of the session data

    Returns:
        pd.DataFrame of quick QC summary
    '''
    # set up QC output file locations
    scan_order = qqc_ss_dir / '01_scan_order.csv'
    scan_count = qqc_ss_dir / '02_series_count.csv'
    volume_shape = qqc_ss_dir / '03_volume_slice_number_comparison_log.csv'
    json_comp = qqc_ss_dir / '04_json_comparison_log.csv'
    anat_orient = qqc_ss_dir / '05a_image_orientation_in_anat.csv'
    non_anat_orident = qqc_ss_dir / '05b_image_orientation_in_others.csv'
    shim_settings = qqc_ss_dir / '05c_shim_settings.csv'
    bval = qqc_ss_dir / '06_bval_comparison_log.csv'
    bit_check = qqc_ss_dir / 'bit_check.csv'
    enhanced_check = qqc_ss_dir / 'enhanced_check.csv'
    dicom_conv_check = qqc_ss_dir / 'dicom_count.csv'
    smoothness_check = qqc_ss_dir / 'smoothness_check.csv'

    # get subject info
    session_name = qqc_ss_dir.name
    subject_name = qqc_ss_dir.parent.name

    # summarize each QC summaries
    colname = f'{subject_name}/{session_name} QC'
    colname_2 = 'Issue in'
    df = pd.DataFrame(columns=[colname])

    other_dfs = []
    titles = []
    for df_loc in scan_count, scan_order, volume_shape, anat_orient, \
            non_anat_orident, shim_settings, bval, bit_check, enhanced_check, \
            dicom_conv_check, smoothness_check:
        # clean up the name of each QC output
        title = re.sub(r'\d+\w{0,1}_', '', df_loc.name).split('.csv')[0]
        title = re.sub(r'_', ' ', title)
        title = re.sub(r' log', '', title)
        title = title[0].upper() + title[1:]

        if df_loc.is_file():
            df_tmp = pd.read_csv(df_loc)
            if 'smoothness' not in title.lower():
                # convert to integer for visibility
                digit_columns = df_tmp.select_dtypes(include='number').columns
                for col in digit_columns:
                    df_tmp[col] = pd.to_numeric(
                            df_tmp[col], errors='ignore').astype(
                                    'Int64').apply(lambda x: ''
                                            if pd.isna(x) else x)

            # if Unnamed: 0 is null, drop the row
            if 'Unnamed: 0' in df_tmp.columns:
                df_tmp.drop(df_tmp[df_tmp['Unnamed: 0'].isnull()].index,
                        inplace=True)

        else:
            df_tmp = pd.DataFrame()
            
        other_dfs.append(df_tmp)
        titles.append(title)

        rename_all_pass = lambda x: 'Pass' if x == 'All Pass' else x
        if df_loc.is_file():
            df.loc[title, colname] = rename_all_pass(df_tmp.iloc[0][-1])
        else:
            df.loc[title, colname] = 'Fail'

        if df.loc[title, colname] == 'Fail':
            if 'volume_slice' in df_loc.name:
                try:
                    df.loc[title, colname_2] = ', '.join(df_tmp[df_tmp[df_tmp.columns[-1]]=='Fail'].series_desc.dropna().unique())
                except:
                    print(df)
            else:
                pass

    # json comparison QC - add lines of difference
    json_comp_df = pd.read_csv(json_comp)
    other_dfs.append(json_comp_df)
    titles.append('MRI protocol comparison')
    # json_comp_df['num'] = json_comp_df.input_json.str.split(
            # '.json').str[0].str[-1]

    json_comp_summary_df = get_summary_table_from_json_to_std(json_comp)

    # df_2 = pd.DataFrame(columns=[colname])
    # if len(json_comp_df) == 0:
        # df_2.loc['Protocol comparison to standard', colname] = 'Pass'
    # else:
        # gb = json_comp_df.groupby(['series_desc', 'series_num'])
        # for (series_desc, series_num), table_upper in gb:
            # try:
                # for loop_num, (num, table) in enumerate(
                        # table_upper.groupby('num')):

                    # diff_items = table['index'].tolist()

                    # if loop_num > 0:
                        # df_2.loc[f'{series_desc} {loop_num}', colname] = \
                                # f'{len(table)}'
                        # df_2.loc[f'{series_desc} {loop_num}', colname_2] = \
                                # ', '.join(diff_items)
                    # else:
                        # df_2.loc[f'{series_desc}', colname] = \
                                # f'{len(table)}'
                        # df_2.loc[f'{series_desc}', colname_2] = \
                                # ', '.join(diff_items)
            # except:
                # pass
    # json_comp_df.drop('num', axis=1, inplace=True)

    return df, json_comp_summary_df, other_dfs, titles


def get_motion_tmp(dwipreproc_dir: Path) -> Tuple:
    if (dwipreproc_dir / 'eddy_out.eddy_restricted_movement_rms').is_file():
        arr = np.loadtxt(dwipreproc_dir /
                'eddy_out.eddy_restricted_movement_rms')
        avg_motions = arr.mean(axis=0)

        outlier_file = dwipreproc_dir / 'eddy_out.eddy_outlier_map'
        outliers_n = np.loadtxt(outlier_file, skiprows=1).sum()
        return (avg_motions[0], avg_motions[1], outliers_n)
    else:
        return pd.NA, pd.NA, pd.NA


def get_motion_fMRI(fmriprep: Path) -> Tuple:
    df = pd.DataFrame()
    if fmriprep.is_dir():
        fmriprep_tsvs = list(fmriprep.glob('*tsv'))
        if len(fmriprep_tsvs) == 0:
            return df

        for tsv_file in fmriprep_tsvs:
            encoding_dir = tsv_file.name.split('-rest_dir-')[1][:2]
            run_number = tsv_file.name.split('_run-')[1][0]
            df_tmp = pd.read_csv(tsv_file, sep='\t')[
                    ['dvars', 'framewise_displacement']].mean().T

            df_tmp['encoding_dir'] = encoding_dir
            df_tmp['run_number'] = run_number

            df = pd.concat([df, df_tmp], axis=1)

        df = df.T.reset_index(drop=True)
        df.set_index(['encoding_dir', 'run_number'], inplace=True)

    return df


def get_anat_qc(mriqc_anat_dir: Path) -> Tuple:
    df = pd.DataFrame(columns=['modality'])
    if mriqc_anat_dir.is_dir():
        for json_f in mriqc_anat_dir.glob('*_T*w.json'):
            if 'nonnorm' in json_f.name:
                continue

            with open(json_f, 'r') as fp:
                data = json.load(fp)

            df_tmp = pd.DataFrame({
                'modality': [json_f.name.split('_')[-1][:3]],
                'cjv': data['cjv'],
                'cnr': data['cnr']})
            df = pd.concat([df, df_tmp])

        df.set_index(['modality'], inplace=True)
    return df


def qqc_summary(qqc_ss_dir: Path) -> pd.DataFrame:
    '''Summarize quick QC output into a single CSV file

    Key Arguments:
        qqc_ss_dir: quick QC location of the session data

    Returns:
        pd.DataFrame of quick QC summary
    '''
    # set up QC output file locations
    scan_order = qqc_ss_dir / '01_scan_order.csv'
    scan_count = qqc_ss_dir / '02_series_count.csv'
    volume_shape = qqc_ss_dir / '03_volume_slice_number_comparison_log.csv'
    json_comp = qqc_ss_dir / '04_json_comparison_log.csv'
    anat_orient = qqc_ss_dir / '05a_image_orientation_in_anat.csv'
    non_anat_orident = qqc_ss_dir / '05b_image_orientation_in_others.csv'
    shim_settings = qqc_ss_dir / '05c_shim_settings.csv'
    bval = qqc_ss_dir / '06_bval_comparison_log.csv'

    # get subject info
    session_name = qqc_ss_dir.name
    subject_name = qqc_ss_dir.parent.name

    derivatives_root = qqc_ss_dir.parent.parent.parent
    dwipreproc_dir = derivatives_root / 'dwipreproc' / \
            subject_name / session_name
    mriqc_dir = derivatives_root / 'mriqc' / \
            subject_name / session_name / 'anat'
    fmriprep_dir = derivatives_root / 'fmriprep' / \
            subject_name / session_name / 'func'

    abs_motion, rel_motion, outliers_n = get_motion_tmp(dwipreproc_dir)
    fMRI_motion_df = get_motion_fMRI(fmriprep_dir)
    mriqc_df = get_anat_qc(mriqc_dir)

    # summarize each QC summaries
    series = pd.Series(name=f'{subject_name}/{session_name} QC',
                       dtype=pd.StringDtype())
    for df_loc in scan_count, scan_order, volume_shape, anat_orient, \
            non_anat_orident, shim_settings, bval:
        # clean up the name of each QC output
        title = re.sub(r'\d+\w{0,1}_', '', df_loc.name).split('.csv')[0]
        title = re.sub(r'_', ' ', title)
        title = re.sub(r' log', '', title)
        title = title[0].upper() + title[1:]

        rename_all_pass = lambda x: 'Pass' if x == 'All Pass' else x
        if df_loc.is_file():
            df = pd.read_csv(df_loc)

            if 'shim' in title.lower():
                shim_label = lambda x: 'Pass' if x == 'Pass' else 'Warning'
                series[title] = shim_label(df.iloc[0][-1])
            else:
                series[title] = rename_all_pass(df.iloc[0][-1])

        else:
            series[title] = 'Fail'


    # json comparison QC - add lines of difference
    json_comp_df = pd.read_csv(json_comp)
    json_comp_df['num'] = json_comp_df.input_json.str.split(
            '.json').str[0].str[-1]

    list_of_diff_nums = []
    series['Protocol comparison to standard'] = 'Fail'

    if len(json_comp_df) == 0:
        series['Protocol comparison to standard'] = 'Pass'
    else:
        gb = json_comp_df.groupby(['series_desc', 'series_num'], dropna=False)
        for (series_desc, series_num), table_upper in gb:
            gb2 = table_upper.groupby('num', dropna=False)
            for loop_num, (num, table) in enumerate(gb2, 1):
                # skip any series which is not included in the standard scan
                if table['standard_json'].str.contains('missing').any():
                    continue

                if table['input'].str.contains('missing').any():
                    diff_num = np.nan
                else:
                    diff_num = len(table)
                list_of_diff_nums.append(diff_num)

                if len(table_upper['num'].unique()) > 1:
                    name = f'Different fields in {series_desc} ({loop_num})'
                else:
                    name = f'Different fields in {series_desc}'

                series[name] = diff_num

    if any(np.isnan(list_of_diff_nums)):
        series['Protocol comparison to standard'] = 'Fail'
    elif any([x > 0 for x in list_of_diff_nums]):
        series['Protocol comparison to standard'] = 'Fail'
    else:
        series['Protocol comparison to standard'] = 'Pass'
    series.drop('Protocol comparison to standard', inplace=True)

    # motion
    series['Absolute_dwi_motion'] = abs_motion
    series['Relative_dwi_motion'] = rel_motion
    series['Outliers_dwi'] = outliers_n

    # fmri motion
    for encoding_dir in 'PA', 'AP':
        for run_num in '1', '2':
            try:
                series[f'DVARS_fMRI_{encoding_dir}_{run_num}'] = \
                        fMRI_motion_df.loc[(encoding_dir, run_num), 'dvars']
            except:
                pass

    for encoding_dir in 'PA', 'AP':
        for run_num in '1', '2':
            try:
                series[f'Framewise_displacement_fMRI_{encoding_dir} {run_num}'] = \
                        fMRI_motion_df.loc[(encoding_dir, run_num), 'framewise_displacement']
            except:
                pass
    # mriqc
    for modality in 'T1w', 'T2w':
        try:
            series[f'CNR_{modality}'] = mriqc_df.loc[modality, 'cnr']
        except:
            pass

    for modality in 'T1w', 'T2w':
        try:
            series[f'CJV_{modality}'] = mriqc_df.loc[modality, 'cjv']
        except:
            pass

    df_all = pd.DataFrame(series)
    new_order = [x for x in df_all.index if not x.startswith('Diff')] + \
            [x for x in df_all.index if x.startswith('Diff')]
    df_all = df_all.loc[new_order]

    df_all.to_csv(qqc_ss_dir / '00_qc_summary.csv')
    return df_all


def extract_consent_date(subject_name: str, phoenix_dir: Path):
    '''Extract consent date of the subject under a phoenix dir'''
    site = subject_name[:2]
    metadata_paths = phoenix_dir.glob(
            f'GENERAL/*{site}/*{site}_metadata.csv')

    for metadata_path in metadata_paths:
        df_tmp = pd.read_csv(metadata_path)[['Subject ID', 'Consent']]
        if subject_name in df_tmp['Subject ID'].to_list():
            consent_date = df_tmp[
                    df_tmp['Subject ID'] == subject_name].iloc[0]['Consent']
            return consent_date

    raise ValueError(f'No matching AMPSCZ-ID ({subject_name}) in metadata')


def get_load_days_from_consent(qqc_subject_dir: Path):
    '''Extract consent date from the PHOENIX metadata csv'''
    nda_root_dir = qqc_subject_dir.parent.parent.parent.parent
    subject_name = qqc_subject_dir.name.split('-')[1]
    phoenix_paths = nda_root_dir.glob('*/PHOENIX')
    for phoenix_path in phoenix_paths:
        try:
            consent_date = extract_consent_date(subject_name, phoenix_path)
            return consent_date
        except ValueError:
            pass

    raise ValueError(
            f'No matching AMPSCZ-ID ({subject_name}) under {nda_root_dir}')


def refresh_qqc_summary_for_subject(qqc_subject_dir: Path) -> None:
    '''Save QQC summary for DPDash for subject with multiple sessions'''
    session_paths = [x for x in qqc_subject_dir.glob('ses-20*') if x.is_dir()]

    if len(session_paths) == 0:
        return

    subject_name = qqc_subject_dir.name.split('-')[1]
    site = subject_name[:2]

    # get consent date
    consent_date = get_load_days_from_consent(qqc_subject_dir)

    # most_recent_session
    most_recent_session = pd.to_datetime('2000-01-01')
    for session_path in session_paths:
        session_date = pd.to_datetime(session_path.name.split('-')[1][:-1])
        if most_recent_session < session_date:
            most_recent_session = session_date

    # days from consent for most recent scan
    days_from_consent = most_recent_session - pd.to_datetime(consent_date)
    days_from_consent = days_from_consent.days

    # delete previous csv file
    previous_qqc_dpdash_csvs = qqc_subject_dir.glob(
            f'{site}-{subject_name}-mriqc-day1to*.csv')

    for i in previous_qqc_dpdash_csvs:
        os.remove(i)

    df_to_return = []
    for session_path in session_paths:
        df_tmp = qqc_summary_for_dpdash(session_path, days_from_consent)
        df_to_return.append(df_tmp)

    return df_to_return


def qqc_summary_for_dpdash(qqc_ss_dir: Path, dayto: int) -> None:
    '''Save QQC session summary for DPDash'''
    # get subject info
    session_name = qqc_ss_dir.name.split('-')[1]
    subject_name = qqc_ss_dir.parent.name.split('-')[1]
    site = subject_name[:2]

    # get consent date
    consent_date = get_load_days_from_consent(qqc_ss_dir.parent)
    session_date = pd.to_datetime(session_name[:-1])
    days_from_consent = session_date - pd.to_datetime(consent_date)
    days_from_consent = days_from_consent.days

    # get QQC summary for the session
    qqc_summary_df = qqc_summary(qqc_ss_dir)

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
    header_df = pd.DataFrame({'day': [days_from_consent],
                              'reftime': '',
                              'timeofday': '',
                              'weekday': ''}).T
    header_df.columns = qqc_summary_df.columns
    qqc_summary_df = pd.concat([header_df, qqc_summary_df]).T

    # DPDash requires day to start from 1
    # qqc_summary_df['day'] = 1

    # remove scan order
    qqc_summary_df.drop('Scan order', axis=1, inplace=True)

    # ignore shim settings

    # remove spaces from column names
    qqc_summary_df.columns = [re.sub(' ', '_', x) for x in
                              qqc_summary_df.columns]

    # create dpdash settings - update here later TODO
    mriqc_pretty = create_dpdash_settings(qqc_summary_df)
    with open('/data/predict1/data_from_nda/MRI_ROOT/mriqc_pretty.json', 'w') as fp:
        json.dump(mriqc_pretty, fp, indent=2)

    # Save individual dpdash settings
    # Session name has to be included as a column in the csv file for DPDash.
    # Also, the file name has to follow XX-AMPSCZID-mriqc-day1toX.csv pattern.
    qqc_summary_df['subject_id'] = subject_name
    qqc_summary_df['session_id'] = session_name

    qqc_summary_df = qqc_summary_add_forms(qqc_summary_df, qqc_ss_dir)

    out_file = qqc_ss_dir.parent / \
            f'{site}-{subject_name}-mriqc-day1to{dayto}.csv'

    if out_file.is_file():
        qqc_summary_df_exist = pd.read_csv(out_file)
        if session_name in qqc_summary_df_exist.session_id.astype(
                str).to_list():
            return qqc_summary_df
    else:
        qqc_summary_df_exist = pd.DataFrame()

    # qqc_summary_df['session'] = session_name
    pd.concat([qqc_summary_df_exist,
               qqc_summary_df]).to_csv(out_file, index=False)

    return qqc_summary_df


def qqc_summary_add_forms(qqc_summary_df: Path, qqc_ss_dir) -> None:
    '''Adds forms data to the QQC csv file TODO: clearn up'''
    # get subject info
    session_name = qqc_summary_df.iloc[0]['session_id']
    subject_name = qqc_summary_df.iloc[0]['subject_id']
    scan_date = pd.to_datetime(
            session_name[:4] + '-' +
            session_name[4:6]  + '-' +
            session_name[6:8])
    site = subject_name[:2]

    # set formsqc location
    if '_dev' in str(qqc_ss_dir):
        forms_qc_path = Path('/data/predict1/data_from_nda_dev/formqc')
    else:
        forms_qc_path = Path('/data/predict1/data_from_nda/formqc')
        
    # get forms qc df
    matching_csvs = list(forms_qc_path.glob(
        f'*-{subject_name}-form_mri_run_sheet-day1to*.csv'))

    if len(matching_csvs) == 0:
        print('No maching MRI run sheet table')
        return qqc_summary_df
    elif len(matching_csvs) > 1:
        print(matching_csvs)
        print('More than one matching MRI run sheet table')
        return qqc_summary_df
    
    df = pd.read_csv(matching_csvs[0])
    cols_to_extract = \
        ['subjectid'] + \
        [x for x in df.columns if 'chrmri_session_' in x] + \
        ['chrmri_scanner'] + \
        [x for x in df.columns if '_qc' in x]
    df_to_add = df[cols_to_extract]

    # get the correct db for the session
    df_to_add['date_in_form'] = \
            df_to_add['chrmri_session_year'].astype(str) + '-' + \
            df_to_add['chrmri_session_month'].astype(str) + '-' + \
            df_to_add['chrmri_session_day'].astype(str)

    df_to_add['date_in_form'] = pd.to_datetime(df_to_add['date_in_form'])
    df_to_add['date_diff'] = (df_to_add['date_in_form'] - scan_date).abs()

    try:
        df_to_select = df_to_add.loc[[df_to_add.date_diff.idxmin()]]
    except:
        print('No data')
        return qqc_summary_df

    df_merged = pd.merge(qqc_summary_df, df_to_select,
            left_on ='subject_id',
            right_on ='subjectid')

    return df_merged


def create_dpdash_settings(qqc_summary_df) -> dict:
    '''Create dictionary for dpdash config

    Key Arguments:
        qqc_summary_df: qqc_summary df initiated by qqc_summary_for_dpdash

    Return:
        a dictionary with dpdash configuration
    '''

    def update_default_dict(**kwargs):
        default_dict = {
            '_id': 0,
            'analysis': 'mriqc',
            'color': ['#fbb4ae', '#b3cde3', '#ccebc5', '#decbe4'],
            'label': 'a',
            'range': [0, 1],
            'text': True,
            'variable': 'a'}

        for key, value in kwargs.items():
            default_dict[key] = value

        return default_dict

    mriqc_pretty = {}
    mriqc_pretty['name'] = 'mriqc'
    mriqc_pretty['config'] = []

    # subject head
    mriqc_pretty['config'].append(
        update_default_dict(category='subject-id',
                            label='subject_id',
                            range=[0, '1'],
                            variable='subject_id'))

    mriqc_pretty['config'].append(
        update_default_dict(category='subject-id',
                            label='session_id',
                            range=[0, '1'],
                            variable='session_id'))

    # mri-form
    for varname, var in {
        'MRI Scanner (Prisma=1)': 'chrmri_scanner',
        'Distortion map AP 1 Quality Check (good=1)': 'chrmri_dmap_qc',
        'Distortion map PA 2 Quality Check (good=1)': 'chrmri_dmpa_qc',
        'T1w MPR Quality Check (good=1)': 'chrmri_t1_qc',
        'T2w SPC Quality Check (good=1)': 'chrmri_t2_qc',
        'Distortion map AP 2 Quality Check (good=1)': 'chrmri_dmap_qc_2',
        'Distortion map PA 2 Quality Check (good=1)': 'chrmri_dmpa_qc_2',
        'rsfMRI rest AP 1 Quality Check (good=1)': 'chrmri_rfmriap_qc',
        'rsfMRI rest PA 1 Quality Check (good=1)': 'chrmri_rfmripa_qc',
        'dMRI b0 AP Quality Check (good=1)': 'chrmri_dmri_b0_qc',
        'dMRI b0 AP Quality Check (good=1)': 'chrmri_dmri_b0_qc_2',
        'dMRI dir 176 PA Quality Check (good=1)': 'chrmri_dmri176_qc',
        'dMRI dir 126 PA Quality Check (good=1)': 'chrmri_dmri126_qc',
        'Distortion map AP 3 Quality Check (good=1)': 'chrmri_dmap_qc_3',
        'Distortion map PA 3 Quality Check (good=1)': 'chrmri_dmpa_qc_3',
        'rsfMRI rest AP 2 Quality Check (good=1)': 'chrmri_rfmriap2_qc',
        'rsfMRI rest PA 2 Quality Check (good=1)': 'chrmri_rfmripa2_qc'
        }.items():
        mriqc_pretty['config'].append(
            update_default_dict(
                category='mri',
                label=varname,
                color=sns.xkcd_palette(['pale red', 'green']).as_hex(),
                variable=var))

    # For each columns
    for param_name in [x for x in qqc_summary_df.columns if x not in
            ['day', 'reftime', 'timeofday', 'weekday']]:
        if param_name.startswith('Different'):  # protocol diff count
            mriqc_pretty['config'].append(update_default_dict(
                category='AAHScout',
                label=re.sub('_', ' ', param_name),
                range=[0, 100],
                color=sns.color_palette("Reds", 8).as_hex(),
                variable=param_name))

        # diffusion
        elif 'Relative_dwi_motion' in param_name:
            mriqc_pretty['config'].append(update_default_dict(
                category='diffusion',
                label=re.sub('_', ' ', param_name),
                range=[0, 1],
                color=sns.color_palette("RdYlGn_r", 8).as_hex(),
                variable=param_name))
        elif 'Absolute_dwi_motion' in param_name:
            mriqc_pretty['config'].append(update_default_dict(
                category='diffusion',
                label=re.sub('_', ' ', param_name),
                range=[0, 2],
                color=sns.color_palette("RdYlGn_r", 8).as_hex(),
                variable=param_name))
        elif 'Outliers_dwi' in param_name:
            mriqc_pretty['config'].append(update_default_dict(
                category='diffusion',
                label=re.sub('_', ' ', param_name),
                range=[0, 300],
                color=sns.color_palette("RdYlGn_r", 8).as_hex(),
                variable=param_name))

        # mriqc
        elif 'CJV' in param_name:
            mriqc_pretty['config'].append(update_default_dict(
                category='struct',
                label=re.sub('_', ' ', param_name) + ' (lower better)',
                range=[0, 1.5],
                color=sns.color_palette("Blues", 8).as_hex(),
                variable=param_name))

        elif 'CNR' in param_name:
            mriqc_pretty['config'].append(update_default_dict(
                category='struct',
                label=re.sub('_', ' ', param_name) + ' (higher better)',
                range=[0, 4.5],
                color=sns.color_palette("Blues_r", 8).as_hex(),
                variable=param_name))

        # fMRIPrep
        elif 'DVARS' in param_name:
            mriqc_pretty['config'].append(update_default_dict(
                category='fmri',
                label=re.sub('_', ' ', param_name),
                range=[0, 150],
                color=sns.color_palette("Oranges", 8).as_hex(),
                variable=param_name))

        elif 'Framewise' in param_name:
            mriqc_pretty['config'].append(update_default_dict(
                category='fmri',
                label=re.sub('_', ' ', param_name),
                range=[0, 1],
                color=sns.color_palette("Oranges", 8).as_hex(),
                variable=param_name))

        # shim settings
        elif 'Shim' in param_name:
            mriqc_pretty['config'].append(update_default_dict(
                category='Parameters',
                label=re.sub('_', ' ', param_name),
                range=[0, 3],
                color=sns.xkcd_palette(['black', 'pale red', 'green', 'denim blue']
                    ).as_hex(),
                variable=param_name))

        else:
            mriqc_pretty['config'].append(update_default_dict(
                category='Parameters',
                label=re.sub('_', ' ', param_name),
                color=sns.xkcd_palette(['pale red', 'green']).as_hex(),
                variable=param_name))

            mriqc_pretty['config'].append(update_default_dict(
                category='Parameters',
                label=re.sub('_', ' ', param_name),
                color=sns.xkcd_palette(['pale red', 'green']).as_hex(),
                variable=param_name))

    return mriqc_pretty

