import pandas as pd
from pathlib import Path
import re


def qqc_summary(qqc_out_dir: Path) -> pd.DataFrame:
    '''Summarize quick QC output into a single CSV file

    Key Arguments:
        qqc_out_dir: quick QC location of the session data

    Returns:
        pd.DataFrame of quick QC summary
    '''
    # set up QC output file locations
    scan_order = qqc_out_dir / '01_scan_order.csv'
    scan_count = qqc_out_dir / '02_series_count.csv'
    volume_shape = qqc_out_dir / '03_volume_slice_number_comparison_log.csv'
    json_comp = qqc_out_dir / '04_json_comparison_log.csv'
    anat_orient = qqc_out_dir / '05a_image_orientation_in_anat.csv'
    non_anat_orident = qqc_out_dir / '05b_image_orientation_in_others.csv'
    shim_settings = qqc_out_dir / '05c_shim_settings.csv'
    bval = qqc_out_dir / '06_bval_comparison_log.csv'

    # get subject info
    session_name = qqc_out_dir.name
    subject_name = qqc_out_dir.parent.name

    # summarize each QC summaries
    series = pd.Series(name=f'{subject_name}/{session_name} QC')
    for df_loc in scan_count, scan_order, volume_shape, anat_orient, \
            non_anat_orident, shim_settings, bval:
        # clean up the name of each QC output
        title = re.sub('\d+\w{0,1}_', '', df_loc.name).split('.csv')[0]
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
    return df_all


def qqc_summary_for_dpdash(qqc_out_dir: Path) -> None:
    '''Save quick QC output summary for DPDash'''
    # get subject info
    session_name = qqc_out_dir.name.split('-')[1]
    subject_name = qqc_out_dir.parent.name.split('-')[1]
    site = subject_name[:2]

    qqc_summary_df = qqc_summary(qqc_out_dir)
    def relabel(val):
        if val == 'Pass':
            return 1
        elif val == 'Fail':
            return 0
        else:
            return val
        
    qqc_summary_df[qqc_summary_df.columns[0]] = qqc_summary_df[
            qqc_summary_df.columns[0]].apply(relabel)
    print(qqc_summary_df)

    header_df = pd.DataFrame({
        'day': [1],
        'reftime': '',
        'timeofday': '',
        'weekday': ''}).T

    header_df.columns = qqc_summary_df.columns
    qqc_summary_df = pd.concat([header_df, qqc_summary_df]).T

    qqc_summary_df.to_csv(qqc_out_dir / f'{site}-{subject_name}-{session_name}-mriqc-day1to1.csv', index=False)



