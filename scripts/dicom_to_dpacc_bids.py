#!/usr/bin/env python
import argparse
from pathlib import Path
import sys
import os
import re
from typing import List, Tuple

import phantom_check
from phantom_check.dicom_files import get_dicom_files_walk, \
        get_csa_header, rearange_dicoms, \
        get_diff_in_csa_for_all_measures, all_elements_to_extract, \
        add_detailed_info_to_summary_df

from phantom_check import json_check, json_check_for_a_session
from phantom_check import compare_bval_files

        
def parse_args(argv):
    '''Parse inputs coming from the terminal'''
    parser = argparse.ArgumentParser(description='dicom_to_depacc_bids')

    # image input related options
    parser.add_argument('--input_dir', '-i', type=str,
                        help='List of raw dicom root directories.')

    parser.add_argument('--subject_name', '-s', type=str,
                        help='Subject name.')

    parser.add_argument('--session_name', '-ss', type=str,
                        help='Session name.')

    parser.add_argument('--output_dir', '-o', type=str,
                        help='BIDS Output directory')

    # extra options
    args = parser.parse_args(argv)
    return args


def dicom_to_bids(input_dir: str, subject_name: str,
                  session_name: str, output_dir: str):
    df_full = get_dicom_files_walk(input_dir)
    rearange_dicoms(df_full, 'test_dicom')

    heuristic_file = Path(phantom_check.__file__).parent / 'data' / \
            'heuristic.py'

    command = 'heudiconv \
    -d {subject}/*/*/*dcm ' \
    f'-f {heuristic_file} ' \
    f'-s {subject_name} -ss {session_name} -c dcm2niix --overwrite \
    -b \
    -o {output_dir}'

    os.popen(command).read()


def get_all_files_walk(root_dir: str, extension: str) -> List[Path]:
    '''Return a list of all json file paths under a root_dir'''
    json_path_list = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.' + extension):
                json_path_list.append(Path(root) / file)

    return json_path_list


def get_naming_parts_bids(file_name: str) -> Tuple[str]:
    '''Return (subject_name, session_name, rest_of_str) from BIDS file'''
    subject_name = re.search(r'sub-([A-Za-z0-9]+)_', file_name).group(1)
    session_name = re.search(r'ses-([A-Za-z0-9]+)_', file_name).group(1)
    json_suffix = file_name.split(session_name)[1]

    return subject_name, session_name, json_suffix


def compare_data_to_standard_all_jsons(input_dir: str, standard_dir: str):
    json_paths_input = get_all_files_walk(input_dir, 'json')
    json_paths_std = get_all_files_walk(standard_dir, 'json')

    for json_path_input in json_paths_input:
        _, _, json_suffix_input = get_naming_parts_bids(json_path_input.name)

        for json_path_std in json_paths_std:
            _, _, json_suffix_std = get_naming_parts_bids(json_path_std.name)
            if json_suffix_input == json_paths_std:

                df_all_diff, df_all_shared = json_check(
                        [json_path_input, json_path_std])


def compare_data_to_standard_all_bvals(input_dir: str, standard_dir: str):
    bval_paths_input = get_all_files_walk(input_dir, 'bval')
    bval_paths_std = get_all_files_walk(standard_dir, 'bval')

    for bval_path_input in bval_paths_input:
        _, _, bval_suffix_input = get_naming_parts_bids(bval_path_input.name)

        for bval_path_std in bval_paths_std:
            _, _, bval_suffix_std = get_naming_parts_bids(bval_path_std.name)
            if bval_suffix_input == bval_paths_std:
                compare_bval_files([bval_path_input, bval_path_std])


def compare_data_to_standard(input_dir: str, standard_dir: str):
    compare_data_to_standard_all_jsons(input_dir, standard_dir)
    compare_data_to_standard_all_bvals(input_dir, standard_dir)



if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    dicom_to_bids(args.input_dir, args.subject_name,
                  args.session_name, args.output_dir)

    # compare_data_to_standard(args.output_dir, args.standard_dir)

    # csa_diff_df, csa_common_df = get_diff_(
            # df, get_same=True)
    # df = add_detailed_info_to_summary_df(df, all_elements_to_extract)

