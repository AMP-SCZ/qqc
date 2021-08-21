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
                             print_shared: bool = False):
    '''Iteratively compare between MR protocol json files and print outputs'''
    dicts = []
    for i in json_files:
        with open(i, 'r') as f:
            single_dict = json.load(f)
            single_dict = dict((x,y) for x, y in single_dict.items()
                    if x in ['ImageOrientationPatientDICOM', 'ShimSetting'])
            dicts.append(single_dict)

    df_all = pd.DataFrame()
    for json_file, dict_for_file in zip(json_files, dicts):
        df_tmp = pd.DataFrame.from_dict(
                dict((x, str(y)) for x, y in dict_for_file.items()),
                orient='index',
                columns=[f'{json_file}'])
        df_all = pd.concat([df_all, df_tmp], axis=1, sort=False)

    df_all['digits'] = df_all[f'{json_file}'].str.extract('(\d+$)')
    df_all = df_all.sort_values('digits', ascending=True)
    df_all = df_all.drop('digits', axis=1).T
    
    df_all_diff = pd.DataFrame()
    df_all_shared = pd.DataFrame()
    for col in df_all.columns:
        if len(df_all[col].unique()) == 1:
            df_all_diff = df_all.drop(col, axis=1)
        else:
            df_all_diff[f'{col}_unique_rank'] = df_all[col].rank()
            df_all_shared = df_all.drop(col, axis=1)

    if print_diff:
        print_diff_shared('Jsons show differences', df_all_diff)

    if print_shared:
        print_diff_shared(
                'Items in the table below are consistent across jsons',
                df_all_shared)

    return (df_all_diff, df_all_shared)

def json_check(json_files: List[str],
               print_diff: bool = True,
               print_shared: bool = False):
    '''Iteratively compare between MR protocol json files and print outputs'''
    dicts = []
    for i in json_files:
        with open(i, 'r') as f:
            dicts.append(json.load(f))

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
                columns=[f'{name_1} (vs {name_2})'])

        df_shared = pd.DataFrame.from_dict(
                dict((x, str(y)) for x, y in shared_items.items()),
                orient='index',
                columns=[f'{name_1} (vs {name_2})'])

        df_all_diff = pd.concat([df_all_diff, df_diff], axis=1, sort=True)
        df_all_shared = pd.concat([df_all_shared, df_shared], axis=1, sort=True)

    if print_diff:
        print_diff_shared('Different items', df_all_diff)

    if print_shared:
        print_diff_shared('The same items included in both each comparison',
                          df_all_shared)

    return (df_all_diff, df_all_shared)


def compare_bval_files(bval_files: str):
    '''Compare two more more bval files'''
    print('Comparing bvals')
    bval_arrays = []
    for bval_file in bval_files:
        print('-', bval_file)
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
        print('\tThe given bvals are different - proceeding to checking number '
              'of volume in each shell')
    else:
        print(f'\tThe {len(bval_files)} bval arrays are exactly the same.')
        all_unique = np.unique(bval_arrays[0], return_counts=True)
        print(f'\t\tshells: {all_unique[0]} ({len(all_unique[0])} shells)')
        print(f'\t\tvolumes in each shell: {all_unique[1]} '
              f'({all_unique[1].sum()} directions)')
        return

    # shells
    same_shell_num = True
    for bval_array in bval_arrays:
        if not (np.unique(bval_array) ==
                np.unique(np.array(bval_arrays))).all():
            print(f'\tNumber of shells differs between bval files')
            same_shell_num = False

    if same_shell_num:
        print('\tThey have the same number of shells')

    # number of volumes in shells
    same_vol_num = True
    for b_shell in np.unique(np.array(bval_arrays)):
        vol_counts = []
        for bval_array in bval_arrays:
            unique_count = np.unique(bval_array, return_counts=True)
            index = np.where(unique_count[0] == b_shell)[0]
            vol_counts.append(unique_count[1][index])

        if not vol_counts.count(vol_counts[0]) == len(vol_counts):
            print(f'\tNumber of {b_shell} differs between bval files')
            same_vol_num = False

    if same_shell_num:
        print('\tThey have the same volume in each shell')


