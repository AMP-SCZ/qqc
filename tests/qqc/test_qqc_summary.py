from pathlib import Path
import re
import pandas as pd
# from qqc.qqc.qqc_summary import qqc_summary_detailed
from qqc.qqc.qqc_summary import get_summary_table_from_json_to_std


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
            dicom_conv_check:
        # clean up the name of each QC output
        title = re.sub(r'\d+\w{0,1}_', '', df_loc.name).split('.csv')[0]
        title = re.sub(r'_', ' ', title)
        title = re.sub(r' log', '', title)
        title = title[0].upper() + title[1:]

        if df_loc.is_file():
            df_tmp = pd.read_csv(df_loc)

            # convert to integer for visibility
            digit_columns = df_tmp.select_dtypes(include='number').columns
            for col in digit_columns:
                df_tmp[col] = pd.to_numeric(
                        df_tmp[col], errors='ignore').astype('Int64').apply(
                                lambda x: '' if pd.isna(x) else x)

            # if Unnamed: 0 is null, drop the row
            if 'Unnamed: 0' in df_tmp.columns:
                df_tmp.drop(df_tmp[df_tmp['Unnamed: 0'].isnull()].index,
                        inplace=True)

            # 'Summary' rows to be empty

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

        if title == 'Scan order':
            print(df_tmp)

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


def test_qqc_summary_detailed():
    qqc_ss_dir = Path(
            '/data/predict1/data_from_nda/MRI_ROOT/derivatives/quick_qc/'
            'sub-CA13329/ses-202309221')

    df, json_comp_summary_df, other_dfs, titles = \
            qqc_summary_detailed(qqc_ss_dir)

    print(df)
