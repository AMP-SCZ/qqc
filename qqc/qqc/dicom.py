import pandas as pd
from pathlib import Path
from qqc.dicom_files import get_diff_in_csa_for_all_measures


def save_csa(df_full: pd.DataFrame, qc_out_dir: Path) -> None:
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
    count_df = df_full_input[['series_num', 'series_desc', 'series_uid']
            ].drop_duplicates().groupby(
                    ['series_desc']
                    ).count().drop('series_num', axis=1)
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
    series_order_df_all.set_index('series_num', inplace=True)

    series_order_df_all['order_diff'] = series_order_df_all['series_order'] \
            != series_order_df_all['series_order_target']
    series_order_df_all['order_diff'] = series_order_df_all['order_diff'].map(
            {True: 'Fail', False: 'Pass'})

    # summary row at the top
    series_order_summary = series_order_df_all.iloc[[0]].copy()
    series_order_summary.index = ['Summary']
    series_order_summary['series_order_target'] = ''
    series_order_summary['series_order'] = ''
    series_order_summary['order_diff'] = 'Fail' if \
            (series_order_df_all['order_diff'] == 'Fail').any() else 'Pass'

    series_order_df_all = pd.concat([series_order_summary,
                                     series_order_df_all])

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

