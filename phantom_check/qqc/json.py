import itertools
import numpy as np
import pandas as pd
import re
import os
import json
from pathlib import Path
from typing import List, Tuple
import logging

from phantom_check.qqc.nifti import compare_volume_to_standard_all_nifti
from phantom_check.utils.files import get_all_files_walk
from phantom_check.utils.names import get_naming_parts_bids
from phantom_check.utils.visualize import print_diff_shared

logger = logging.getLogger(__name__)


def jsons_from_bids_to_df(session_dir: Path) -> pd.DataFrame:
    '''Read all json files from session_dir and return protocol name as df

    Key Argument:
        session_dir: root of session directory in BIDS format, Path.

    Returns:
        pd.DataFrame

    Notes:
        series_num, series_desc and norm (bool of 'NORM' in ImageType) are 
        included inthe pd.DataFrame as columns.
    '''
    df = pd.DataFrame()

    json_paths_input = get_all_files_walk(session_dir, 'json')
    for num, file in enumerate(json_paths_input):
        with open(file, 'r') as json_file:
            data = json.load(json_file)
            series_num = data['SeriesNumber']
            series_desc = data['SeriesDescription']
            norm = 'NORM' in data['ImageType']
            df.loc[num, 'series_num'] = series_num
            df.loc[num, 'series_desc'] = series_desc
            df.loc[num, 'norm'] = norm

    if num == 0:
        logger.warn('There is no JSON files under the nifti directory')

    return df


def json_check_for_a_session(json_files: List[str],
                             print_diff: bool = True,
                             print_shared: bool = False,
                             **kwargs) -> Tuple[pd.DataFrame]:
    '''Iteratively compare between MR protocol json files and print outputs


    Key Arguments:
        json_files: list of json file paths, list of str.
        print_diff: if True, prints the series with different information.
        print_diff: if True, prints the series with different information.
        **kwargs:
            - specified_field: allow the function to focus on a specific field.
                               eg) 'ShimSetting' or
                                   'ImageOrientationPatientDICOM'

    Returns:
        Tuple of pd.DataFrames. 
            - df_all
            - df_all_diff
            - df_all_shared
    '''

    specific_field = kwargs.get('specific_field', '')

    dicts = []
    bn_snum_dict = {}
    bn_sname_dict = {}

    # collect information from all json files
    for i in json_files:
        with open(i, 'r') as f:
            single_dict = json.load(f)
        bn_snum_dict[Path(i).name] = single_dict['SeriesNumber']
        bn_sname_dict[Path(i).name] = single_dict['SeriesDescription']
        single_dict = dict((x, y) for x, y in single_dict.items()
                           if x in [specific_field])
        dicts.append(single_dict)

    # convert collected information into pandas dataframe
    df_all = pd.DataFrame()
    for json_file, dict_for_file in zip(json_files, dicts):
        df_tmp = pd.DataFrame.from_dict(
            dict((x, str(y)) for x, y in dict_for_file.items()),
            orient='index',
            columns=[f'{json_file}'])
        df_all = pd.concat([df_all, df_tmp], axis=1, sort=False)
        df_all.columns = [Path(x).name for x in df_all.columns]

    # clean up collected information in the dataframe
    df_all = df_all.T
    df_all['series_number'] = df_all.index.map(bn_snum_dict).astype(int)
    df_all['series_name'] = df_all.index.map(bn_sname_dict)
    df_all.sort_values(by='series_number', inplace=True)
    df_all = df_all.reset_index().set_index(['series_number',
                                             'series_name',
                                             'index'])

    # filter out differences between series
    df_all_diff = df_all.copy()
    df_all_shared = df_all.copy()
    for col in df_all.columns:
        if len(df_all[col].unique()) == 1:
            df_all_diff = df_all_diff.drop(col, axis=1)
        else:
            df_all_shared = df_all_shared.drop(col, axis=1)

    all_cols = []
    for col in df_all_diff.columns:
        if col not in all_cols:
            all_cols.append(col) 
        df_all_diff[f'{col}_unique_rank'] = df_all[col].rank()

    for col in df_all_shared.columns:
        if col not in all_cols:
            all_cols.append(col) 
        df_all_shared[f'{col}_unique_rank'] = df_all[col].rank()

    for col in all_cols:
        df_all[f'{col}_unique_rank'] = df_all[col].rank()

    if print_diff:
        print_diff_shared(
                'Json files from the same scan session show differences',
                df_all_diff)

    if print_shared:
        print_diff_shared(
                'Items in the table below are consistent across json files',
                df_all_shared)

    return (df_all, df_all_diff, df_all_shared)


def summarize_into_file(fp: 'openfile',
                        df_all_diff: pd.DataFrame,
                        df_all_shared: pd.DataFrame,
                        title: str) -> None:
    '''Write summary of df_all_df into open file fp'''
    fp.write(f'Checking {title}'+ '\n')
    fp.write('='*80 + '\n')
    if df_all_diff.empty:
        fp.write(f'{title} are consistent' + '\n')
        fp.write('(Items in the table below are consistent across json '
                 'files)\n')
        fp.write(df_all_shared.to_string() + '\n')
    else:
        fp.write(df_all_diff.to_string() + '\n')
    fp.write('='*80 + '\n\n\n')


def json_check(json_files: List[str],
               print_diff: bool = True,
               print_shared: bool = False,
               **kwargs):
    '''Iteratively compare between MR protocol json files and print outputs'''
    dicts = []
    for i in json_files:
        with open(i, 'r') as f:
            single_dict = json.load(f)
            dicts.append(single_dict)

    names = itertools.combinations(json_files, 2)
    sets = itertools.combinations(dicts, 2)

    df_all_diff = pd.DataFrame()
    df_all_shared = pd.DataFrame()
    for (name_1, name_2), (first_dict, second_dict) in zip(names, sets):

        diff_items = {k: first_dict[k] for k in first_dict
                      if k in second_dict and first_dict[k] != second_dict[k]}
        shared_items = {k: first_dict[k] for k in first_dict
                        if k in second_dict and
                        first_dict[k] == second_dict[k]}

        df_diff = pd.DataFrame.from_dict(
                dict((x, str(y)) for x, y in diff_items.items()),
                orient='index',
                columns=[f'{Path(name_1).name} (vs {Path(name_2).name})'])

        df_shared = pd.DataFrame.from_dict(
                dict((x, str(y)) for x, y in shared_items.items()),
                orient='index',
                columns=[f'{Path(name_1).name} (vs {Path(name_2).name})'])

        df_all_diff = pd.concat([df_all_diff, df_diff], axis=1, sort=True)
        df_all_shared = pd.concat([df_all_shared, df_shared], axis=1, sort=True)

    # drop unnecessary indices
    for df_tmp in df_all_diff, df_all_shared:
        to_drop_list = [
            'AcquisitionTime', 'ImageOrientationPatientDicom',
            'ImageOrientationPatientDICOM',
            'SliceTiming',
            'global', 'TxRefAmp',
            'dcmmeta_affine', 'WipMemBlock',
            'SAR', 'time',
            'ShimSetting']

        # Include to detect different machine
        # 'InstitutionAddress', 'InstitutionName',
        # 'InstitutionalDepartmentName', 'ManufacturersModelName',
        # 'ProcedureStepDescription', 'StationName', 
        # 'DeviceSerialNumber'
        for i in to_drop_list:
            try:
                df_tmp.drop(i, inplace=True)
            except:
                pass


    if print_diff:
        print_diff_shared('Different items', df_all_diff)

    if print_shared:
        print_diff_shared('The same items included in both each comparison',
                          df_all_shared)

    return (df_all_diff, df_all_shared)


def get_all_json_information_quick(data_dir):
    json_paths = get_all_files_walk(data_dir, 'json')
    df_path_order = sort_json_paths_with_series_number(json_paths)
    json_paths = df_path_order.sort_values(by='series_number'
            ).filepath.tolist()

    json_df = pd.DataFrame()
    for json_path_input in json_paths:
        _, __, json_suffix_input = \
                get_naming_parts_bids(json_path_input.name)

        with open(json_path_input, 'r') as json_file:
            data = json.load(json_file)

            image_type = str(data['ImageType'])
            series_num = data['SeriesNumber']
            series_desc = data['SeriesDescription']

        json_df_tmp = pd.DataFrame({
            'json_path': [json_path_input],
            'json_suffix': json_suffix_input,
            'image_type': image_type,
            'series_num': series_num,
            'series_desc': series_desc})

        json_df_tmp['run_num'] = json_df_tmp['json_suffix'].str.extract(
                'run-(\d+)')
        json_df_tmp['num_num'] = json_df_tmp['json_suffix'].str.extract(
                'num-(\d+)')
        json_df_tmp['scout_num'] = json_df_tmp['json_path'].apply(
                lambda x: x.name).str.split('.').str[0].str[-1]

        json_df = pd.concat([json_df, json_df_tmp], sort=False)

    json_df = json_df.reset_index().drop('index', axis=1)

    # adding distortion_map_before
    distortion_index = json_df[
            json_df.series_desc.str.contains(
                'distortion', flags=re.IGNORECASE)].index
    for index, row in json_df.loc[distortion_index].iterrows():
        range_of_index = range(index, json_df.index[-1])
        for _, matching_row in json_df.loc[list(range_of_index)].iterrows():
            if 'distortion' not in matching_row.series_desc.lower():
                json_df.loc[index, 'distortion_map_before'] = \
                        matching_row.series_desc
                break

    return json_df


def find_matching_files_between_BIDS_sessions(
        input_dir: str, standard_dir: str) -> pd.DataFrame:
    '''Find matching files between two BIDS sessions and return pd.DataFrame

    Key Arguments:
        input_dir: input BIDS session root, str.
        standard_dir: standard BIDS session root, str.

    Returns:
        

    '''
    pd.set_option('max_columns', 50)
    json_df_input = get_all_json_information_quick(input_dir)
    json_df_std = get_all_json_information_quick(standard_dir)

    if 'distortion_map_before' in json_df_input.columns:
        json_df_all = pd.merge(
            json_df_input, json_df_std,
            how='left',
            on=['series_desc', 'image_type', 'run_num',
                'num_num', 'scout_num', 'distortion_map_before'],
            suffixes=['_input', '_std'])
    else:
        json_df_all = pd.merge(
            json_df_input, json_df_std,
            how='left',
            on=['series_desc', 'image_type', 'run_num',
                'num_num', 'scout_num'],
            suffixes=['_input', '_std'])

    for index, row in json_df_all.iterrows():
        # When there is extra distortion map, the number in front of run_num
        # does not match to that of standard distortion maps. So, distortion
        # maps do not get matched properly. Iterate non-matched distortion maps
        if pd.isnull(row.json_path_std) and \
                'distort' in row.series_desc.lower():
            # get dataframe of standard distortion maps in the same position
            # eg.) distortion maps before T1w_MPR or rfMRI_REST
            df_tmp = json_df_std[
                (json_df_std.series_desc == row.series_desc) &
                (json_df_std.distortion_map_before == \
                        row.distortion_map_before)]

            # find the standard distortion map with most close series number
            diff_in_series_num = 100
            for df_tmp_index, r2 in df_tmp.iterrows():
                diff = row.series_num_input - r2.series_num
                if np.absolute(diff) < diff_in_series_num:
                    json_df_all.loc[index, 'json_path_std'] = r2.json_path
                    json_df_all.loc[index, 'json_suffix_std'] = r2.json_suffix
                    json_df_all.loc[index, 'series_num_std'] = r2.series_num
                    diff_in_series_num = diff

        # if there is any distortion map mismatched because of unmatching
        # "distortion_map_before" information, due to missing series that 
        # should have followed the distortion map, match them manually here
        if pd.isnull(row.json_path_std) and \
                'distort' in row.series_desc.lower():
            # get dataframe of standard distortion maps in the same position
            # eg.) distortion maps before T1w_MPR or rfMRI_REST
            df_tmp = json_df_std[
                (json_df_std.series_desc == row.series_desc) &
                (json_df_std.run_num == row.run_num) &
                (json_df_std.scout_num == row.scout_num)]

            # find the standard distortion map with most close series number
            diff_in_series_num = 100
            for df_tmp_index, r2 in df_tmp.iterrows():
                diff = row.series_num_input - r2.series_num
                if np.absolute(diff) < diff_in_series_num:
                    json_df_all.loc[index, 'json_path_std'] = r2.json_path
                    json_df_all.loc[index, 'json_suffix_std'] = r2.json_suffix
                    json_df_all.loc[index, 'series_num_std'] = r2.series_num
                    diff_in_series_num = diff


        # scout
        if pd.isnull(row.json_path_std) and \
                'aahscout' in row.series_desc.lower():
            # get dataframe of standard distortion maps in the same position
            # eg.) distortion maps before T1w_MPR or rfMRI_REST
            series_tmp = json_df_std[
                (json_df_std.series_desc == row.series_desc)].iloc[0]

            json_df_all.loc[index, 'json_path_std'] = series_tmp.json_path
            json_df_all.loc[index, 'json_suffix_std'] = series_tmp.json_suffix
            json_df_all.loc[index, 'series_num_std'] = series_tmp.series_num
        
        elif pd.isnull(row.json_path_std) and \
                'scout' in row.series_desc.lower():
            # get dataframe of standard distortion maps in the same position
            # eg.) distortion maps before T1w_MPR or rfMRI_REST
            series_tmp = json_df_std[
                (json_df_std.series_desc.str.lower() == row.series_desc.lower()) &
                (json_df_std.num_num == row.num_num)].iloc[0]

            json_df_all.loc[index, 'json_path_std'] = series_tmp.json_path
            json_df_all.loc[index, 'json_suffix_std'] = series_tmp.json_suffix
            json_df_all.loc[index, 'series_num_std'] = series_tmp.series_num

        # localizers
        elif pd.isnull(row.json_path_std) and \
            'localizer' in row.series_desc.lower():
            series_tmp = json_df_std[
                (json_df_std.series_desc.str.lower() == row.series_desc.lower()) &
                (json_df_std.scout_num == row.scout_num)].iloc[0]

            json_df_all.loc[index, 'json_path_std'] = series_tmp.json_path
            json_df_all.loc[index, 'json_suffix_std'] = series_tmp.json_suffix
            json_df_all.loc[index, 'series_num_std'] = series_tmp.series_num

        # other maps with different series number
        # else:
            # series_tmp = json_df_std[
                # (json_df_std.series_desc == row.series_desc) &
                # (json_df_std.image_type == row.image_type)
                # ].iloc[0]
            # json_df_all.loc[index, 'json_path_std'] = series_tmp.json_path
            # json_df_all.loc[index, 'json_suffix_std'] = series_tmp.json_suffix
            # json_df_all.loc[index, 'series_num_std'] = series_tmp.series_num


    # standard series not included in the input series
    for num, (index, row) in enumerate(json_df_std[
            ~json_df_std.json_suffix.isin(json_df_all.json_suffix_std)
                ].iterrows(), 1):
        new_index = json_df_all.index[-1] + num
        for var in ['image_type', 'series_desc', 'series_num', 'run_num',
                    'num_num', 'scout_num', 'distortion_map_before']:
            json_df_all.loc[new_index, var] = row[var]

        for var in ['json_path', 'json_suffix', 'series_num']:
            json_df_all.loc[new_index, f'{var}_std'] = row[var]

    json_df_all.sort_values(['series_num_input', 'run_num', 'scout_num'],
                            inplace=True)

    return json_df_all


def compare_bval_files(bval_files: List[str]):
    '''Compare two more more bval files

    Key arguments:
        bval_files: matching bvalue file path strings, list of str.
        out_log: output log file
    '''
    # make bval_files a list of absolute paths
    bval_files = [Path(x).absolute() for x in bval_files]

    bval_arrays = []  # list of arrays

    # dataframe approach
    bval_df = pd.DataFrame(index=['bval', 'shells'])
    for var, bval_file in zip(['input', 'std'],
                              [bval_files[0], bval_files[1]]):
        bval_df.loc['bval', var] = bval_file.name
        bval_array = np.round(np.loadtxt(bval_file), -2)
        # bval_df.loc['bval_arr', var] = np.array2string(bval_array)
        bval_df.loc['shells', var] = np.array2string(np.unique(bval_array))

        for b_shell in np.unique(bval_array):
            shell, shell_count = np.unique(bval_array, return_counts=True)
            index = np.where(shell == b_shell)[0]
            shell_dir = shell_count[index]
            bval_df.loc[f'shell_{b_shell}_dirs', var] = shell_dir[0]


    bval_df['check'] = bval_df.eq(bval_df.iloc[:, 0], axis=0).all(1)
    bval_df.loc['bval', 'check'] = 'Pass' if \
            (bval_df.iloc[1:]['check'] == True).all() else 'False'

    return bval_df


def within_phantom_qc(session_dir: Path, qc_out_dir: Path) -> None:
    '''Compare headers of serieses from the scan

    Compare ShimSettings across different serieses,
    ImageOrientationPatientDICOM across anatomical scans, and
    ImageOrientationPatientDICOM across the rest of scans. It load information
    from all json files exist under the session_dir.

    Key Arguments:
        session_dir: root of the nifti directory for the session, Path
        qc_out_dir: qc_out_dir under BIDS derivatives, Path

    Returns:
        None

    Notes:
    '''
    json_paths_input = get_all_files_walk(session_dir, 'json')

    non_ignore_json_paths_input = [x for x in json_paths_input
                                 if (x.parent.name != 'ignore')]

    non_anat_json_paths_input = [x for x in json_paths_input
                                 if (x.parent.name != 'anat') and 
                                    (x.parent.name != 'ignore')]

    anat_json_paths_input = [x for x in json_paths_input
                             if x.parent.name == 'anat']

    # fp = open(qc_out_dir / 'within_phantom_qc.txt', 'w')
    for json_input, specific_field, title, letter in zip(
            [non_ignore_json_paths_input,
             non_anat_json_paths_input, anat_json_paths_input],
            ['ShimSetting',
             'ImageOrientationPatientDICOM',
             'ImageOrientationPatientDICOM'],
            ['shim settings',
             'image orientation in others',
             'image orientation in anat'],
            ['c', 'b', 'a']):
        df_all, df_all_diff, df_all_shared = json_check_for_a_session(
            json_input,
            print_diff=False, print_shared=False,
            specific_field=specific_field)

        csv_suffix = re.sub('[ ]+', '_', title)

        # label summary
        summary_df = df_all.iloc[[0]].copy()
        summary_df.index = pd.MultiIndex.from_tuples(
                [('Summary', '', '')],
                names=['series_number', 'series_name', 'index'])
        for col in summary_df.columns:
            if col.endswith('unique_rank'):
                summary_df[col] = 'Pass' if len(df_all[col].unique()) == 1 \
                        else 'Fail'
            else:
                summary_df[col] = ''
        df_all = pd.concat([summary_df, df_all])

        df_all.to_csv(qc_out_dir / f'05{letter}_{csv_suffix}.csv')


def compare_data_to_standard(input_dir: str, standard_dir: str,
                             qc_out_dir: Path, partial_rescan: bool) -> None:

    for func in compare_data_to_standard_all_jsons_new, \
                compare_data_to_standard_all_bvals, \
                compare_volume_to_standard_all_nifti:
        func(input_dir, standard_dir, qc_out_dir, partial_rescan)


def sort_json_paths_with_series_number(json_paths_input: List[Path]) -> list:
    df = pd.DataFrame({
        'filepath': json_paths_input,
        'json': [json.load(open(x)) for x in json_paths_input]})
    df['series_number'] = df['json'].apply(lambda x: x['SeriesNumber'])
    df['series_name'] = df['json'].apply(lambda x: x['SeriesDescription'])
    df['series_number'] = df['series_number'].astype(int)
    df.drop('json', axis=1, inplace=True)

    return df


def json_check_new(json_files: list, diff_only=True) -> pd.DataFrame:
    '''Compare list of json files and return dataframe

    Key Arguments:
        json_files: list of json files, list of Path.
        diff_only: return different values only
    '''
    to_drop_list = [
        'AcquisitionTime', 'ImageOrientationPatientDicom',
        'ImageOrientationPatientDICOM',
        'SliceTiming',
        'global', 'TxRefAmp',
        'dcmmeta_affine', 'WipMemBlock',
        'SAR', 'time',
        'ShimSetting', 'SeriesNumber']

    dicts = []
    cols = []
    series_desc_list = []
    for i in json_files:
        cols.append(i.name)
        with open(i, 'r') as f:
            single_dict = json.load(f)
            dicts.append(single_dict)

    df_tmp = pd.DataFrame(dicts).T

    for i in to_drop_list:
        if i in df_tmp.index:
            df_tmp.drop(i, inplace=True)

    df_tmp.columns = cols

    if diff_only:
        df_tmp = df_tmp[(df_tmp[cols[0]] != df_tmp[cols[1]])]

    return df_tmp


def compare_data_to_standard_all_jsons_new(input_dir: str,
                                           standard_dir: str,
                                           qc_out_dir: Path,
                                           partial_rescan: bool):

    json_df_all = find_matching_files_between_BIDS_sessions(input_dir,
                                                            standard_dir)
    json_df_all.to_csv(qc_out_dir / '99_input2std_matching_table.csv')

    df_diff = pd.DataFrame()
    # for each set of matching json files
    for _, row in json_df_all.iterrows():
        if row.json_path_input is 'missing' or pd.isnull(row.json_path_input):
            df_row = pd.DataFrame({
                'series_desc': [row.series_desc],
                'series_num': row['series_num_input'],
                'input_json': row['json_path_input'],
                'standard_json': row['json_path_std'].name})
        elif row.json_path_std is 'missing' or pd.isnull(row.json_path_std):
            df_row = pd.DataFrame({
                'series_desc': [row.series_desc],
                'series_num': row['series_num_input'],
                'input_json': row['json_path_input'],
                'standard_json': 'missing'})
        else:
            df_row = json_check_new([Path(row.json_path_input),
                                     Path(row.json_path_std)])
            df_row.columns = ['input', 'std']
            df_row['series_desc'] = row['series_desc']
            df_row['series_num'] = row['series_num_input']
            df_row['input_json'] = row['json_path_input'].name
            df_row['standard_json'] = row['json_path_std'].name

        # missing from input
        if df_row['series_num'].isnull().all():
            df_row['input'] = 'missing'

        df_row = df_row.reset_index().set_index(
            ['series_desc', 'series_num', 'input_json',
             'standard_json', 'index'])

        if len(df_row) == 0:
            df_row.loc[(row['series_desc'],
                        row['series_num_input'],
                        row['json_path_input'].name,
                        row['json_path_std'].name,
                        'no_diff'), 'input'] = 'No difference'
            df_row.loc[(row['series_desc'],
                        row['series_num_input'],
                        row['json_path_input'].name,
                        row['json_path_std'].name,
                        'no_diff'), 'std'] = 'No difference'


        df_diff = pd.concat([df_diff, df_row], axis=0)

    df_diff.to_csv(qc_out_dir / '04_json_comparison_log.csv')


def compare_data_to_standard_all_jsons(input_dir: str,
                                       standard_dir: str,
                                       qc_out_dir: Path,
                                       partial_rescan: bool):
    json_paths_input = get_all_files_walk(input_dir, 'json')
    json_paths_std = get_all_files_walk(standard_dir, 'json')

    df_path_order = sort_json_paths_with_series_number(json_paths_input)
    json_paths_input = df_path_order.sort_values(
            by='series_number').filepath.tolist()

    name_dict = df_path_order.set_index('filepath')['series_name'].to_dict()
    num_dict = df_path_order.set_index('filepath')['series_number']

    fp = open(qc_out_dir / 'json_comparison_log.txt', 'w')
    for json_path_input in json_paths_input:
        series_name = name_dict[json_path_input]
        series_number = num_dict[json_path_input]
        _, _, json_suffix_input = \
                get_naming_parts_bids(json_path_input.name)

        with open(json_path_input, 'r') as json_file:
            data = json.load(json_file)

            image_type = data['ImageType']
            series_num = data['SeriesNumber']
            series_desc = data['SeriesDescription']


        for json_path_std in json_paths_std:
            _, _, json_suffix_std = \
                    get_naming_parts_bids(json_path_std.name)

            with open(json_path_std, 'r') as json_file:
                data = json.load(json_file)
                std_image_type = data['ImageType']
                std_series_num = data['SeriesNumber']
                std_series_desc = data['SeriesDescription']

            if (series_desc == std_series_desc) & \
                    (image_type == std_image_type):
                # make sure the number of localizer and scout files are
                # the same
                if ('localizer' in series_desc.lower()) or \
                        ('scout' in series_desc.lower()):
                    if json_path_input.name[-6] != json_path_std.name[-6]:
                        continue

                fp.write(f'Comparing {series_number} {series_name}\n')
                fp.write(f'- {json_path_input}\n')
                fp.write(f'- {json_path_std}\n')
                df_all_diff, df_all_shared = json_check(
                        [json_path_input, json_path_std], False)

                if partial_rescan:
                    fp.write("* partial rescan - ignoring numbers "
                             "following acq- and num-")
                    if 'SeriesDescription' in df_all_diff.index:
                        continue

                if len(df_all_diff) > 0:
                    dfAsString = df_all_diff.to_string()

                    fp.write(dfAsString + '\n')
                else:
                    fp.write('*No difference\n')
                fp.write('='*80)
                fp.write('\n\n\n\n')
    fp.close()


def compare_data_to_standard_all_bvals(input_dir: str,
                                       standard_dir: str,
                                       qc_out_dir: Path,
                                       partial_rescan: bool):
    bval_paths_input = get_all_files_walk(input_dir, 'bval')
    bval_paths_std = get_all_files_walk(standard_dir, 'bval')

    bval_df = pd.DataFrame()
    for bval_path_input in bval_paths_input:
        _, _, bval_suffix_input = get_naming_parts_bids(bval_path_input.name)

        for bval_path_std in bval_paths_std:
            _, _, bval_suffix_std = get_naming_parts_bids(bval_path_std.name)
            if bval_suffix_input == bval_suffix_std:
                bval_df_tmp = compare_bval_files(
                        [bval_path_input, bval_path_std])
                bval_df_tmp['suffix'] = bval_suffix_input
                bval_df = pd.concat([bval_df, bval_df_tmp.reset_index().set_index(['suffix', 'index'])])

    if 'Fail' in bval_df['check']:
        bval_df = pd.concat([pd.DataFrame({'check': ['Fail'],
                                           'suffix': 'Summary',
                                           'index': ''}).set_index(
                                               ['suffix', 'index']),
                             bval_df])
    else:
        bval_df = pd.concat([pd.DataFrame({'check': ['All Pass'],
                                           'suffix': 'Summary',
                                           'index': ''}).set_index(
                                               ['suffix', 'index']),
                             bval_df])

    bval_df[['input', 'std', 'check']].to_csv(
            qc_out_dir / '06_bval_comparison_log.csv')

