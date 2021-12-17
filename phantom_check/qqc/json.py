import itertools
import numpy as np
import pandas as pd
import re
import os
import json
from pathlib import Path
from typing import List
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
            'SliceTiming',
            'global', 'TxRefAmp',
            'dcmmeta_affine', 'WipMemBlock',
            'SAR', 'time']

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




def within_phantom_qc(session_dir: Path, qc_out_dir: Path):
    '''Compare headers of serieses from the scan

    Compare ShimSettings across different series json files of a scan.

    Key Arguments:
        session_dir: root of the nifti directory for the session, Path
        qc_out_dir: qc_out_dir under BIDS derivatives, Path

    Returns:
        None

    Notes:
    '''
    json_paths_input = get_all_files_walk(session_dir, 'json')

    with open(qc_out_dir / 'within_phantom_qc.txt', 'w') as fp:
        fp.write('Checking shim settings'+ '\n')
        fp.write('='*80 + '\n')
        df_all_diff, df_all_shared = json_check_for_a_session(
                json_paths_input,
                print_diff=False, print_shared=False,
                specific_field='ShimSetting')

        if df_all_diff.empty:
            fp.write('Seem settings are consistent' + '\n')
            fp.write('(Items in the table below are consistent across json '
                     'files)\n')
            fp.write(df_all_shared.to_string() + '\n')
        else:
            fp.write(df_all_diff.to_string() + '\n')
        fp.write('='*80 + '\n\n\n')


        fp.write('Checking image orientation in dMRI, fMRI and '
                 'distortionMaps'+ '\n')
        fp.write('='*80 + '\n')
        non_anat_json_paths_input = [x for x in json_paths_input
                                      if x.parent.name != 'anat']
        df_all_diff, df_all_shared = json_check_for_a_session(
                non_anat_json_paths_input,
                print_diff=False, print_shared=False,
                specific_field='ImageOrientationPatientDICOM')
        if df_all_diff.empty:
            fp.write('Image Orientations are consistent' + '\n')
            fp.write('(Items in the table below are consistent across json '
                     'files)\n')
            fp.write(df_all_shared.to_string() + '\n')
        else:
            fp.write(df_all_diff.to_string() + '\n')
        fp.write('='*80 + '\n\n\n')

        # anat
        fp.write('Checking image orientation in anat'+ '\n')
        fp.write('='*80 + '\n')
        anat_json_paths_input = [x for x in json_paths_input
                                  if x.parent.name == 'anat']
        df_all_diff, df_all_shared = json_check_for_a_session(
                anat_json_paths_input,
                print_diff=False, print_shared=False,
                specific_field='ImageOrientationPatientDICOM')
        if df_all_diff.empty:
            fp.write('Image Orientations are consistent' + '\n')
            fp.write('(Items in the table below are consistent across json '
                     'files)\n')
            fp.write(df_all_shared.to_string() + '\n')
        else:
            fp.write(df_all_diff.to_string() + '\n')
        fp.write('='*80 + '\n\n\n')


def compare_data_to_standard(input_dir: str, standard_dir: str,
                             qc_out_dir: Path, partial_rescan: bool) -> None:

    for func in compare_data_to_standard_all_jsons, \
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
    with open(qc_out_dir / 'json_comparison_log.txt', 'w') as fp:
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


def compare_data_to_standard_all_bvals(input_dir: str,
                                       standard_dir: str,
                                       qc_out_dir: Path,
                                       partial_rescan: bool):
    bval_paths_input = get_all_files_walk(input_dir, 'bval')
    bval_paths_std = get_all_files_walk(standard_dir, 'bval')

    bval_comparison_log = qc_out_dir / 'bval_comparison_log.txt'
    if bval_comparison_log.is_file():
        os.remove(qc_out_dir / 'bval_comparison_log.txt')

    for bval_path_input in bval_paths_input:
        _, _, bval_suffix_input = get_naming_parts_bids(bval_path_input.name)

        for bval_path_std in bval_paths_std:
            _, _, bval_suffix_std = get_naming_parts_bids(bval_path_std.name)
            if bval_suffix_input == bval_suffix_std:
                compare_bval_files([bval_path_input, bval_path_std],
                                    bval_comparison_log)


def compare_data_to_standard_lazy(input_dir: str,
                                  standard_dir: str,
                                  qc_out_dir: Path,
                                  partial_rescan: bool):
    '''pass'''
    weighted_scans_std = Path(standard_dir).glob(
            'dwi/*acq-[1234567890]*.json')
    weighted_scans_input = Path(input_dir).glob(
            'dwi/*acq-[1234567890]*.json')

    with open(qc_out_dir / 'json_comparison_log.txt', 'a') as fp:
        for weighted_scan_std in weighted_scans_std:
            modality_std = weighted_scan_std.name.split('_')[-1]
            for weighted_scan_input in weighted_scans_input:
                modality_input = weighted_scan_input.name.split('_')[-1]
                if modality_std == modality_input:
                    fp.write(f'Comparing diffusion weighted image for skyra '
                              'to that of Prisma\n')
                    fp.write(f'- {weighted_scan_input}\n')
                    fp.write(f'- {weighted_scan_std}\n')
                    df_all_diff, df_all_shared = json_check(
                            [weighted_scan_input, weighted_scan_std], False)
                    if len(df_all_diff) > 0:
                        dfAsString = df_all_diff.to_string()

                        fp.write(dfAsString + '\n')
                    else:
                        fp.write('*No difference\n')
                    fp.write('='*80)
                    fp.write('\n\n\n\n')

    
    bvals_std = Path(standard_dir).glob(
            'dwi/*acq-[1234567890]*.bval')
    bvals_input = Path(input_dir).glob(
            'dwi/*acq-[1234567890]*.bval')
    bval_comparison_log = qc_out_dir / 'bval_comparison_log.txt'

    for bval_std in bvals_std:
        modality_std = bval_std.name.split('_')[-1]
        for bval_input in bvals_input:
            modality_input = bval_input.name.split('_')[-1]
            if modality_std == modality_input:
                compare_bval_files([bval_input, bval_std],
                                    bval_comparison_log)

    compare_volume_to_standard_all_nifti(input_dir, standard_dir, qc_out_dir)



