import pandas as pd
from pathlib import Path
import re
import json


def qqc_summary_detailed(qqc_out_dir: Path) -> pd.DataFrame:
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
    colname = f'{subject_name}/{session_name} QC'
    colname_2 = 'Issue in'
    df = pd.DataFrame(columns=[colname])

    other_dfs = []
    titles = []
    for df_loc in scan_count, scan_order, volume_shape, anat_orient, \
            non_anat_orident, shim_settings, bval:
        # clean up the name of each QC output
        title = re.sub(r'\d+\w{0,1}_', '', df_loc.name).split('.csv')[0]
        title = re.sub(r'_', ' ', title)
        title = re.sub(r' log', '', title)
        title = title[0].upper() + title[1:]

        df_tmp = pd.read_csv(df_loc)
        other_dfs.append(df_tmp)
        titles.append(title)

        rename_all_pass = lambda x: 'Pass' if x == 'All Pass' else x
        df.loc[title, colname] = rename_all_pass(df_tmp.iloc[0][-1])

        if df.loc[title, colname] == 'Fail':
            if 'volume_slice' in df_loc.name:
                df.loc[title, colname_2] = ', '.join(df_tmp[df_tmp[df_tmp.columns[-1]]=='Fail'].series_desc.dropna().unique())
            # elif 'series_count' in df_loc.name:
                # print(df_tmp)
                # df.loc[title, colname_2] = ', '.join(df_tmp[df_tmp[df_tmp.columns[-1]]=='Fail'].series_num.dropna().unique())
            # elif 'scan_order' in df_loc.name:
                # df.loc[title, colname_2] = ', '.join(df_tmp[df_tmp[df_tmp.columns[-1]]=='Fail'].series_order.dropna().unique())
            else:
                pass

    # json comparison QC - add lines of difference
    json_comp_df = pd.read_csv(json_comp)
    other_dfs.append(json_comp_df)
    titles.append('MRI protocol comparison')
    json_comp_df['num'] = json_comp_df.input_json.str.split(
            '.json').str[0].str[-1]

    df_2 = pd.DataFrame(columns=[colname])
    if len(json_comp_df) == 0:
        df_2.loc['Protocol comparison to standard', colname] = 'Pass'
    else:
        gb = json_comp_df.groupby(['series_desc', 'series_num'])
        for (series_desc, series_num), table_upper in gb:
            for loop_num, (num, table) in enumerate(
                    table_upper.groupby('num')):

                diff_items = table['index'].tolist()

                if loop_num > 0:
                    df_2.loc[f'{series_desc} {loop_num}', colname] = \
                            f'{len(table)}'
                    df_2.loc[f'{series_desc} {loop_num}', colname_2] = \
                            ', '.join(diff_items)
                else:
                    df_2.loc[f'{series_desc}', colname] = \
                            f'{len(table)}'
                    df_2.loc[f'{series_desc}', colname_2] = \
                            ', '.join(diff_items)
    json_comp_df.drop('num', axis=1, inplace=True)

    return df, df_2, other_dfs, titles

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
    series = pd.Series(name=f'{subject_name}/{session_name} QC',
                       dtype=pd.StringDtype()) 
    for df_loc in scan_count, scan_order, volume_shape, anat_orient, \
            non_anat_orident, shim_settings, bval:
        # clean up the name of each QC output
        title = re.sub(r'\d+\w{0,1}_', '', df_loc.name).split('.csv')[0]
        title = re.sub(r'_', ' ', title)
        title = re.sub(r' log', '', title)
        title = title[0].upper() + title[1:]

        df = pd.read_csv(df_loc)

        rename_all_pass = lambda x: 'Pass' if x == 'All Pass' else x
        series[title] = rename_all_pass(df.iloc[0][-1])

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
                    diff_num = 99
                else:
                    diff_num = len(table)
                list_of_diff_nums.append(diff_num)

                if len(table_upper['num'].unique()) > 1:
                    name = f'Different fields in {series_desc} ({loop_num})'
                else:
                    name = f'Different fields in {series_desc}'

                series[name] = diff_num

    if any([x > 0 for x in list_of_diff_nums]):
        series['Protocol comparison to standard'] = 'Fail'
    else:
        series['Protocol comparison to standard'] = 'Pass'

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

    # Pass -> 1, Fail -> 0
    def relabel(val):
        if val == 'Pass':
            return 1
        elif val == 'Fail':
            return 0
        else:
            return int(val)

    qqc_summary_df[qqc_summary_df.columns[0]] = qqc_summary_df[
            qqc_summary_df.columns[0]].apply(relabel)

    header_df = pd.DataFrame({'day': [1],
                              'reftime': '',
                              'timeofday': '',
                              'weekday': ''}).T

    header_df.columns = qqc_summary_df.columns
    qqc_summary_df = pd.concat([header_df, qqc_summary_df]).T

    # remove spaces from column names
    qqc_summary_df.columns = [re.sub(' ', '_', x) for x in
                              qqc_summary_df.columns]

    # create dpdash settings
    mriqc_pretty = create_dpdash_settings(qqc_summary_df)
    with open('mriqc_pretty.json', 'w') as fp:
        json.dump(mriqc_pretty, fp, indent=2)

    out_file = qqc_out_dir / \
            f'{site}-{subject_name}_{session_name}-mriqc-day1to1.csv'
    qqc_summary_df.to_csv(out_file, index=False)



def create_dpdash_settings(qqc_summary_df) -> dict:
    '''Create dictionary for dpdash config'''

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
        update_default_dict(
            category='subject-id',
            label='subject_id',
            range=[0, '1'],
            variable='subject_id'))

    mriqc_pretty['config'].append(
        update_default_dict(
            category='subject-id',
            label='session_id',
            range=[0, '1'],
            variable='session_id'))

    # parameters
    for param_name in [x for x in qqc_summary_df.columns
            if re.search('[A-Z]', x[0])]:
        if param_name.startswith('Different'):  # protocol diff count
            mriqc_pretty['config'].append(
                update_default_dict(
                    category='AAHScout',
                    label=re.sub('_', ' ', param_name),
                    range=[0, 99],
                    variable=param_name))
        else:  # summary
            mriqc_pretty['config'].append(
                update_default_dict(
                    category='Parameters',
                    label=re.sub('_', ' ', param_name),
                    color=['#f7fcb9', '#addd8e', '#31a354'],
                    variable=param_name))

    return mriqc_pretty

