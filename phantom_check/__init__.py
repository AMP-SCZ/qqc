from phantom_check.utils.visualize import print_diff_shared
from phantom_check.utils.files import get_jsons_from_dicom_dirs

import itertools
import numpy as np
import pandas as pd
import json
from typing import List
from pathlib import Path
import sys


def json_check_for_a_session(json_files: List[str],
                             print_diff: bool = True,
                             print_shared: bool = False,
                             **kwargs):
    '''Iteratively compare between MR protocol json files and print outputs'''

    specific_field = kwargs.get('specific_field', '')

    dicts = []
    basename_seriesnum_dict = {}
    basename_seriesname_dict = {}
    for i in json_files:
        with open(i, 'r') as f:
            single_dict = json.load(f)
            basename_seriesnum_dict[Path(i).name] = single_dict['SeriesNumber']
            basename_seriesname_dict[Path(i).name] = \
                    single_dict['SeriesDescription']
            single_dict = dict((x, y) for x, y in single_dict.items()
                               if x in [specific_field])
            dicts.append(single_dict)

    df_all = pd.DataFrame()
    for json_file, dict_for_file in zip(json_files, dicts):
        df_tmp = pd.DataFrame.from_dict(
                dict((x, str(y)) for x, y in dict_for_file.items()),
                orient='index',
                columns=[f'{json_file}'])
        df_all = pd.concat([df_all, df_tmp], axis=1, sort=False)
        df_all.columns = [Path(x).name for x in df_all.columns]

    df_all = df_all.T
    df_all['series_number'] = df_all.index.map(
            basename_seriesnum_dict).astype(int)
    df_all['series_name'] = df_all.index.map(basename_seriesname_dict)
    df_all.sort_values(by='series_number', inplace=True)
    df_all = df_all.reset_index().set_index(
            ['series_number', 'series_name', 'index'])

    df_all_diff = df_all.copy()
    df_all_shared = df_all.copy()
    for col in df_all.columns:
        if len(df_all[col].unique()) == 1:
            df_all_diff = df_all_diff.drop(col, axis=1)
        else:
            df_all_shared = df_all_shared.drop(col, axis=1)

    for col in df_all_diff.columns:
        df_all_diff[f'{col}_unique_rank'] = df_all[col].rank()
        # df_all_diff = df_all_diff.sort_values(f'{col}_unique_rank')

    if print_diff:
        print_diff_shared(
                'Json files from the same scan session show differences',
                df_all_diff)

    if print_shared:
        print_diff_shared(
                'Items in the table below are consistent across json files',
                df_all_shared)

    return (df_all_diff, df_all_shared)


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
            'InstitutionAddress', 'InstitutionName',
            'InstitutionalDepartmentName', 'ManufacturersModelName',
            'SliceTiming',
            'ProcedureStepDescription', 'StationName', 'global', 'TxRefAmp',
            'dcmmeta_affine', 'WipMemBlock', 'DeviceSerialNumber',
            'SAR', 'time']

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


def compare_bval_files(bval_files: str, out_log: str):
    '''Compare two more more bval files'''

    out_log = Path(out_log)
    fp = open(out_log, 'a')
    fp.write('-'*80 + '\n')
    fp.write('Comparing bvals\n')
    # make bval_files a list of absolute paths
    bval_files = [Path(x).absolute() for x in bval_files]

    bval_arrays = []
    for bval_file in bval_files:
        fp.write(f'- {bval_file}\n')
        bval_arrays.append(np.round(np.loadtxt(bval_file), -2))

    # exactly same bval files
    same_array = True
    for a, b in itertools.combinations(bval_arrays, 2):
        if np.array_equal(a, b):
            pass
        else:
            same_array = False
            break

    if not same_array:
        fp.write(
            '\tThe given bvals are different - proceeding to checking number '
            'of volume in each shell\n')
        for file_name, bval_array in zip(bval_files, bval_arrays):
            all_unique = np.unique(bval_array, return_counts=True)
            fp.write(f'\t*{file_name}\n')
            fp.write(
                f'\t\tshells: {all_unique[0]} ({len(all_unique[0])} shells)\n')
            fp.write(f'\t\tvolumes in each shell: {all_unique[1]} '
                     f'({all_unique[1].sum()} directions)\n')
    else:
        fp.write(
            f'\tThe {len(bval_files)} bval arrays are exactly the same.\n')
        all_unique = np.unique(bval_arrays[0], return_counts=True)
        fp.write(
            f'\t\tshells: {all_unique[0]} ({len(all_unique[0])} shells)\n')
        fp.write(f'\t\tvolumes in each shell: {all_unique[1]} '
                 f'({all_unique[1].sum()} directions)\n')
        return

    # shells
    same_shell_num = True
    bval_arrays_all = np.concatenate([x for x in bval_arrays])
    for bval_array in bval_arrays:
        if not np.array_equal(np.unique(bval_array),
                              np.unique(bval_arrays_all)):
            fp.write(
                f'\tNumber of shells differs between bval files\n')
            same_shell_num = False

    if same_shell_num:
        fp.write('\tThey have the same number of shells\n')

    # number of volumes in shells
    same_vol_num = True
    for b_shell in np.unique(bval_arrays_all):
        vol_counts = []
        for bval_array in bval_arrays:
            unique_count = np.unique(bval_array, return_counts=True)
            index = np.where(unique_count[0] == b_shell)[0]
            vol_counts.append(unique_count[1][index])

        if not vol_counts.count(vol_counts[0]) == len(vol_counts):
            fp.write(f'\tNumber of {b_shell} differs between bval files\n')
            same_vol_num = False

    if same_shell_num:
        fp.write('\tThey have the same volume in each shell\n')
    fp.close()


