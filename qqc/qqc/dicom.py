import os
import re
import pydicom
import pandas as pd
from pathlib import Path
from typing import Tuple
from qqc.dicom_files import get_diff_in_csa_for_all_measures


def is_enhanced(dicom_root: Path) -> Tuple[bool, str]:
    '''checks if the dicom_root has enhnaced XA30 dicom'''
    for root, dirs, files in os.walk(dicom_root):
        for file in files:
            d = pydicom.read_file(Path(root) / file)

            # TODO: update with more pythonic lines to extract 0002, 0002 tag
            line_search = re.search(r'\(0002, 0002\).*(UI.*)', str(d))
            if line_search:
                search = re.search('enhanced', line_search.group(1), re.IGNORECASE)
                if search:
                    return (True, line_search.group(1))
                else:
                    return (False, line_search.group(1))


def compare_enhanced_to_std(input_dir: str,
                            standard_dir: str,
                            qc_out_dir: Path) -> None:
    enhanced_comparison_log = qc_out_dir / 'enhanced_check.csv'

    input_dir = Path(input_dir)
    input_subject = input_dir.parent.name.split('sub-')[1]
    input_session = input_dir.name
    input_dicom_dir = input_dir.parent.parent.parent / 'sourcedata' / \
            input_subject / input_session

    standard_dir = Path(standard_dir)
    standard_subject = standard_dir.parent.name.split('sub-')[1]
    standard_session = standard_dir.name
    standard_dicom_dir = standard_dir.parent.parent.parent / 'sourcedata' / \
            standard_subject / standard_session

    if input_dicom_dir.is_dir():
        input_enhanced = is_enhanced(input_dicom_dir)
    else:
        input_enhanced = ('Input dicom not detected', '')

    if standard_dicom_dir.is_dir():
        std_enhanced = is_enhanced(standard_dicom_dir)
    else:
        std_enhanced = ('Standard dicom not detected', '')

    df = pd.DataFrame({
        'Input data': [input_enhanced[0], input_enhanced[1]],
        'Standard data': [std_enhanced[0], std_enhanced[1]]})
    df.index = ['Enhanced', 'Value']
    df.loc['Enhanced', 'check'] = df.loc['Enhanced'].all()
    df['check'] = df['check'].map({True: 'Pass', False: 'Fail'})
                        
    df.to_csv(enhanced_comparison_log)


def check_image_fov_pos_ori_csa(csa_df_loc: pd.DataFrame,
                                standard_dir: Path) -> None:
    # TODO
    csa_df = pd.read_csv(csa_df_loc)
    std_session = standard_dir.name
    std_subject = standard_dir.parent.name
    standard_dir_qc_dir = standard_dir.parent.parent.parent / 'derivatives' / \
            'quick_qc' / std_subject / std_session 

    standard_csa_df = pd.read_csv(standard_dir_qc_dir / '99_csa_headers.csv')
    # standard_csa_df['modality'] = standard_csa_df['Unnamed: 0']

    for df in csa_df, standard_csa_df:
        df['modality'] = df['Unnamed: 0'].str.extract('\d+_(\S+)')
        modalities_seen = []
        for index, row in df.iterrows():
            if 'distortion' in row.modality.lower():
                if 'dmri_b0_ap' in modalities_seen:
                    df.loc[index, 'distortion'] = 'post_dmri'

                elif 't1w_mpr' in modalities_seen:
                    df.loc[index, 'distortion'] = 'post_struct'

                else:
                    df.loc[index, 'distortion'] = 'pre_struct'

            modalities_seen.append(row.modality.lower())

    df_merge = pd.merge(
            csa_df, standard_csa_df,
            suffixes=('_input', '_std'),
            on=['modality', 'distortion'], how='left')

    columns_to_select = [x for x in df_merge.columns if
            'asSlice[0].sPosition' in x]
    csa_qc_df = df_merge[['modality', 'distortion'] + columns_to_select]
            

def save_csa(df_full: pd.DataFrame,
             qc_out_dir: Path,
             standard_dir: Path) -> None:
    csa_diff_df, csa_common_df = get_diff_in_csa_for_all_measures(
            df_full, get_same=True)
    csa_df = pd.concat([csa_diff_df, csa_common_df],
                    sort=False).sort_index().T
    csa_df['series_num'] = csa_df.index.str.extract('(\d+)').astype(int).values
    qc_out_dir.mkdir(exist_ok=True)
    csa_df.sort_values(by='series_num').drop(
            'series_num', axis=1).to_csv(qc_out_dir / '99_csa_headers.csv')


def check_num_of_series(df_full_input: pd.DataFrame,
                        df_full_std: pd.DataFrame) -> pd.DataFrame:
    '''Check the number of series in the input dicom series against template

    Key arguments:
        df_full_input: get_dicom_files_walk output of raw dicom directory
        df_full_std: json_from_bids_to_df output of the standard bids directory

    Returns:
        number of series in pd.DataFrame
    '''
    if 'series_uid' in df_full_input.columns:
        cols_to_use = ['series_num', 'series_desc', 'series_uid']
        count_df = df_full_input[cols_to_use].drop_duplicates().groupby(
            ['series_desc']).count().drop('series_num', axis=1)
    else:
        cols_to_use = ['series_num', 'series_desc']
        count_df = df_full_input[cols_to_use].drop_duplicates().groupby(
            ['series_desc']).count()

    count_df.columns = ['series_num']

    count_target_df = df_full_std.groupby('series_desc').count()[
            ['series_num']]
    count_target_df.columns = ['target_count']

    count_df_all = pd.merge(count_df, count_target_df,
                            left_index=True, right_index=True, how='outer')

    count_df_all['series_num'].fillna(0, inplace=True)
    count_df_all['target_count'].fillna(0, inplace=True)

    count_df_all['count_diff'] = \
            count_df_all['series_num'] - count_df_all['target_count']

    def return_diff_to_show(num: int) -> str:
        if num == 0:
            return 'Pass'
        elif num < 0:
            return 'Fail'
        else:
            return 'Extra scans'

    count_df_all['diff'] = count_df_all['count_diff'].apply(lambda x:
            return_diff_to_show(x))

    # summary row at the top
    count_df_all_summary = count_df_all.iloc[[0]].copy()
    count_df_all_summary.index = ['Summary']
    count_df_all_summary['series_num'] = ''
    count_df_all_summary['target_count'] = ''
    count_df_all_summary['count_diff'] = ''
    count_df_all_summary['diff'] = 'Fail' if \
            (count_df_all['diff'] == 'Fail').any() else 'Pass'

    count_df_all = pd.concat([count_df_all_summary,
                              count_df_all])

    return count_df_all


def check_order_of_series(df_full_input: pd.DataFrame,
                          df_full_std: pd.DataFrame) -> pd.DataFrame:
    '''Check the order of series in the input dicom series against template

    Key arguments:
        df_full_input: get_dicom_files_walk output of raw dicom directory
        df_full_std: json_from_bids_to_df output of the standard bids directory

    Returns:
        number of series in pd.DataFrame
    '''
    # TODO: see if this function can be used in the csa extraction
    series_num_df = df_full_input[
            ['series_num', 'series_desc']].drop_duplicates()
    series_num_df.columns = ['series_num', 'series_order']
    series_num_df = series_num_df[
            ~series_num_df.series_order.str.contains('phoenix')]
    series_num_target_df = df_full_std[['series_num', 'series_desc']]
    series_num_target_df.columns = ['series_num', 'series_order_target']
    series_num_target_df = series_num_target_df[
            ~series_num_target_df.series_order_target.str.contains('phoenix')]

    series_order_df_all = pd.merge(
            series_num_target_df, series_num_df,
            on='series_num', how='outer').sort_values(by='series_num')

    # drop FA & PHOENIX
    series_order_df_all = series_order_df_all[
            ~series_order_df_all['series_order_target'].str.contains(
                'fa', na=False)]
    series_order_df_all = series_order_df_all[
            ~series_order_df_all['series_order_target'].str.contains(
                'phoenix', na=False)]
    series_order_df_all = series_order_df_all[
            ~series_order_df_all['series_order'].str.contains(
                'fa', na=False)]
    series_order_df_all = series_order_df_all[
            ~series_order_df_all['series_order'].str.contains(
                'phoenix', na=False)]

    # squeeze
    series_order_df_all['series_num_target'] = series_order_df_all[
            'series_num']
    series_order_df_all = pd.concat([
        series_order_df_all[
            ['series_num_target', 'series_order_target']
            ].dropna().reset_index(drop=True),
        series_order_df_all[
            ['series_num', 'series_order']].dropna().reset_index(drop=True),
        ], axis=1)

    series_order_df_all['order_diff'] = series_order_df_all['series_order'] \
            != series_order_df_all['series_order_target']
    series_order_df_all['order_diff'] = series_order_df_all['order_diff'].map(
            {True: 'Fail', False: 'Pass'})

    # summary row at the top
    series_order_summary = series_order_df_all.iloc[[0]].copy()
    series_order_summary.iloc[0] = ''
    series_order_summary.index = ['Summary']
    series_order_summary['series_order_target'] = ''
    series_order_summary['series_order'] = ''
    series_order_summary['order_diff'] = 'Fail' if \
            (series_order_df_all['order_diff'] == 'Fail').any() else 'Pass'

    series_order_df_all = pd.concat([series_order_summary,
                                     series_order_df_all])
    series_order_df_all = series_order_df_all[
            ['series_num', 'series_order_target', 'series_order',
             'series_num_target', 'order_diff']]
    return series_order_df_all


def check_num_order_of_series(df_full_input: pd.DataFrame,
                              df_full_std: pd.DataFrame,
                              qc_out_dir: Path) -> None:
    '''Check number and order of series, and saveas output as csv

    Key Arguments:
        df_full_input: get_dicom_files_walk output of raw dicom directory
        df_full_std: json_from_bids_to_df output of the standard bids directory
        qc_out_dir: output qc directory, Path.

    '''
    num_check_df = check_num_of_series(df_full_input, df_full_std)
    order_check_df = check_order_of_series(df_full_input, df_full_std)

    order_check_df.to_csv(qc_out_dir / '01_scan_order.csv')
    num_check_df.to_csv(qc_out_dir / '02_series_count.csv')

