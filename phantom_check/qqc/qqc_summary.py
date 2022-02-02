import pandas as pd
from pathlib import Path
import re


def qqc_summary(qqc_out_dir: Path) -> None:
    '''Summarize quick QC output into a single CSV file'''
    # set up QC output file locations
    scan_order = qqc_out_dir / '01_scan_order.csv'
    scan_count = qqc_out_dir / '02_series_count.csv'
    volume_shape = qqc_out_dir / '03_volume_slice_number_comparison_log.csv'
    json_comp = qqc_out_dir / '04_json_comparison_log.csv'
    anat_orient = qqc_out_dir / \
            '05_json_check_image_orientation_in_anat.csv'
    non_anat_orident = qqc_out_dir / \
            '05_json_check_image_orientation_in_' \
            'dMRI_fMRI_and_distortionMaps.csv'
    shim_settings = qqc_out_dir / \
            '05_json_check_shim_settings_in_' \
            'anat_dMRI_fMRI_and_distortionMaps.csv'
    bval = qqc_out_dir / '06_bval_comparison_log.csv'

    # summarize each QC summaries
    series = pd.Series(name='QC')
    for df_loc in scan_count, scan_order, volume_shape, anat_orient, \
            non_anat_orident, shim_settings, bval:
        # clean up the name of each QC output
        title = df_loc.name[3:].split('.csv')[0]
        title = re.sub(r'_', ' ', title)
        title = re.sub(r' log', '', title)
        title = title[0].upper() + title[1:]

        df = pd.read_csv(df_loc)

        rename_all_pass = lambda x: 'Pass' if x == 'All Pass' else x
        series[title] = rename_all_pass(df.iloc[0][-1])

    # json comparison QC - add lines of difference
    json_comp_df = pd.read_csv(json_comp)
    json_comp_df['num'] = json_comp_df.input_json.str.split('.json').str[0].str[-1]

    if len(json_comp_df) == 0:
        series['Protocol comparison to standard'] = 'Pass'
    else:
        gb = json_comp_df.groupby(['series_desc', 'series_num'])
        for (series_desc, series_num), table_upper in gb:
            for loop_num, (num, table) in enumerate(
                    table_upper.groupby('num')):
                if loop_num > 0:
                    series[f'Diff proc fields in {series_desc} {loop_num}'] = \
                            f'{len(table)}'
                else:
                    series[f'Different field in {series_desc}'] = \
                            f'{len(table)}'

    df_all = pd.DataFrame(series)
    df_all.to_csv(qqc_out_dir / '00_qc_summary.csv')
