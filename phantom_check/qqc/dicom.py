import pandas as pd
from pathlib import Path
from phantom_check.dicom_files import get_diff_in_csa_for_all_measures


def save_csa(df_full: pd.DataFrame, qc_out_dir: Path) -> None:
    csa_diff_df, csa_common_df = get_diff_in_csa_for_all_measures(
            df_full, get_same=True)
    csa_df = pd.concat([csa_diff_df, csa_common_df],
                    sort=False).sort_index().T
    csa_df['series_num'] = csa_df.index.str.extract('(\d+)').astype(int).values
    csa_df.sort_values(by='series_num').drop(
            'series_num', axis=1).to_csv(qc_out_dir / 'csa_headers.csv')


def check_num_order_of_series(df_full: pd.DataFrame,
                              qc_out_dir: Path,
                              skyra: bool = False) -> None:
    '''Check number and order of series

    Key Arguments:
        df_full: pandas dataframe of all dicoms, pd.DataFrame.
        qc_out_dir: output qc directory, Path.

    '''
    # series number count
    count_df = df_full[['series_num', 'series_desc', 'series_uid']
            ].drop_duplicates().groupby(
                    ['series_desc']
                    ).count().drop('series_num', axis=1)
    count_df.columns = ['series_num']

    if skyra:
        count_target_df = pd.DataFrame({
            'AAHScout': [1],
            'AAHScout': 1,
            'AAHScout_MPR_cor': 1,
            'AAHScout_MPR_sag': 1,
            'AAHScout_MPR_tra': 1,
            'DistortionMap_AP': 3,
            'DistortionMap_PA': 3,
            'Localizer': 1,
            'Localizer_aligned': 1,
            'T1w_MPR': 2,
            'T2w_SPC': 2,
            'dMRI_b0_AP': 2,
            'dMRI_b0_AP_SBRef': 2,
            'dMRI_dir126_PA': 1,
            'dMRI_dir126_PA_SBRef': 1,
            'rfMRI_REST_AP': 2,
            'rfMRI_REST_AP_SBRef': 2,
            'rfMRI_REST_PA': 2,
            'rfMRI_REST_PA_SBRef': 2}, index=['target_count']).T

    else:
        count_target_df = pd.DataFrame({
            'AAHScout': [1],
            'AAHScout': 1,
            'AAHScout_MPR_cor': 1,
            'AAHScout_MPR_sag': 1,
            'AAHScout_MPR_tra': 1,
            'DistortionMap_AP': 3,
            'DistortionMap_PA': 3,
            'Localizer': 1,
            'Localizer_aligned': 1,
            'T1w_MPR': 2,
            'T2w_SPC': 2,
            'dMRI_b0_AP': 2,
            'dMRI_b0_AP_SBRef': 2,
            'dMRI_dir176_PA': 1,
            'dMRI_dir176_PA_SBRef': 1,
            'rfMRI_REST_AP': 2,
            'rfMRI_REST_AP_SBRef': 2,
            'rfMRI_REST_PA': 2,
            'rfMRI_REST_PA_SBRef': 2}, index=['target_count']).T


    count_df_all = pd.merge(count_df, count_target_df,
                            left_index=True, right_index=True, how='outer')

    count_df_all['count_diff'] = \
            count_df_all['series_num'] - count_df_all['target_count']
    count_df_all['diff'] = count_df_all['count_diff'] != 0
    count_df_all['diff'] = count_df_all['diff'].map(
            {True: 'Fail', False: 'Pass'})
    count_df_all.to_csv(qc_out_dir / 'series_count.csv')

    # with open(qc_out_dir / 'series_count.txt', 'w') as series_count_file:
        # if not (count_df_all['diff'] == 'Fail').any():
            # series_count_file.write('Number of series are consistent\n')

        # for index, row in count_df_all[
                # count_df_all['diff']=='Fail'].iterrows():
            # plural_c = '' if row.series_num == 1 else 's'
            # if row['count_diff'] > 0:
                # plural = '' if row['count_diff'] == 1 else 's'
                # line_to_write = \
                    # f'{index} has extra scan{plural}:\n' \
                    # f'{index} has {row.series_num} scan{plural_c} ' \
                    # f'(should have {row.target_count})\n'
            # else:
                # plural = '' if row['count_diff'] == -1 else 's'
                # line_to_write = \
                    # f'{index} has missing scan{plural}:\n' \
                    # f'{index} has {row.series_num} scan{plural_c} ' \
                    # f'(should have {row.target_count})\n'
            # print(line_to_write)
            # series_count_file.write(line_to_write)

    # series order
    series_num_df = df_full[['series_num', 'series_desc']].drop_duplicates()
    series_num_df.columns = ['series_num', 'series_order']

    if skyra:
        series_num_target_df = pd.DataFrame({
            1:['Localizer'],
            2:'AAHScout',
            3:'AAHScout_MPR_sag',
            4:'AAHScout_MPR_cor',
            5:'AAHScout_MPR_tra',
            6:'Localizer_aligned',
            7:'DistortionMap_AP',
            8:'DistortionMap_PA',
            9:'T1w_MPR',
            10:'T1w_MPR',
            11:'T2w_SPC',
            12:'T2w_SPC',
            13:'DistortionMap_AP',
            14:'DistortionMap_PA',
            15:'rfMRI_REST_AP_SBRef',
            16:'rfMRI_REST_AP',
            17:'rfMRI_REST_PA_SBRef',
            18:'rfMRI_REST_PA',
            19:'dMRI_b0_AP_SBRef',
            20:'dMRI_b0_AP',
            21:'dMRI_dir126_PA_SBRef',
            22:'dMRI_dir126_PA',
            23:'dMRI_b0_AP_SBRef',
            24:'dMRI_b0_AP',
            25:'DistortionMap_AP',
            26:'DistortionMap_PA',
            27:'rfMRI_REST_AP_SBRef',
            28:'rfMRI_REST_AP',
            29:'rfMRI_REST_PA_SBRef',
            30:'rfMRI_REST_PA'}, index=['series_desc']).T.reset_index()
    else:
        series_num_target_df = pd.DataFrame({
            1:['Localizer'],
            2:'AAHScout',
            3:'AAHScout_MPR_sag',
            4:'AAHScout_MPR_cor',
            5:'AAHScout_MPR_tra',
            6:'Localizer_aligned',
            7:'DistortionMap_AP',
            8:'DistortionMap_PA',
            9:'T1w_MPR',
            10:'T1w_MPR',
            11:'T2w_SPC',
            12:'T2w_SPC',
            13:'DistortionMap_AP',
            14:'DistortionMap_PA',
            15:'rfMRI_REST_AP_SBRef',
            16:'rfMRI_REST_AP',
            17:'rfMRI_REST_PA_SBRef',
            18:'rfMRI_REST_PA',
            19:'dMRI_b0_AP_SBRef',
            20:'dMRI_b0_AP',
            21:'dMRI_dir176_PA_SBRef',
            22:'dMRI_dir176_PA',
            23:'dMRI_b0_AP_SBRef',
            24:'dMRI_b0_AP',
            25:'DistortionMap_AP',
            26:'DistortionMap_PA',
            27:'rfMRI_REST_AP_SBRef',
            28:'rfMRI_REST_AP',
            29:'rfMRI_REST_PA_SBRef',
            30:'rfMRI_REST_PA'}, index=['series_desc']).T.reset_index()

    series_num_target_df.columns = ['series_num', 'series_order_target']

    series_order_df_all = pd.merge(
            series_num_target_df, series_num_df,
            on='series_num', how='outer').sort_values(by='series_num')
    series_order_df_all.set_index('series_num', inplace=True)

    series_order_df_all['order_diff'] = series_order_df_all['series_order'] \
            != series_order_df_all['series_order_target']
    series_order_df_all['order_diff'] = series_order_df_all['order_diff'].map(
            {True: 'Fail', False: 'Pass'})

    print(series_order_df_all)
    series_order_df_all.to_csv(qc_out_dir / 'scan_order.csv')

    # with open(qc_out_dir / 'scan_order.txt', 'w') as scan_order_file:
        # if not (series_order_df_all['order_diff']=='Fail').any():
            # scan_order_file.write('Scan orders are consistent\n')

        # for index, row in series_order_df_all[
                # series_order_df_all['order_diff'] == 'Fail'].iterrows():
            # line_to_write = \
                # f'Series number {index} is {row.series_order} - should be ' \
                # f'{row.series_order_target}\n'
            # print(line_to_write)
            # scan_order_file.write(line_to_write)


