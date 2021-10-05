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
from phantom_check.utils.files import load_data_bval, get_diffusion_data_from_nifti_prefix
from phantom_check.utils.visualize import create_b0_signal_figure, \
        create_image_signal_figure
from phantom_check.utils.files import get_nondmri_data
import tempfile
import pandas as pd

        
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

    parser.add_argument('--standard_dir', '-std', type=str,
                        help='Root of a standard dataset to compare to')
    # extra options
    args = parser.parse_args(argv)
    return args


def dicom_to_bids(input_dir: str, subject_name: str,
                  session_name: str, output_dir: str):
    print(f'Walking through {input_dir}, searching for dicom files')
    df_full = get_dicom_files_walk(input_dir)
    print(f'File walk - complete')

    # with tempfile.TemporaryDirectory() as tmpdir:
    dicom_clearned_up_output = Path(output_dir) / 'dicom'
    rearange_dicoms(df_full, dicom_clearned_up_output,
                    subject_name, session_name)

    heuristic_file = Path(phantom_check.__file__).parent.parent / 'data' / \
            'heuristic.py'

    command = f'heudiconv \
    -d {dicom_clearned_up_output}' + '/{subject}/ses-{session}/*/* ' \
    f'-f {heuristic_file} ' \
    f'-s {subject_name} -ss {session_name} -c dcm2niix \
    -b \
    -o {output_dir}'

    print(command)

    os.popen(command).read()

    return df_full


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


def compare_data_to_standard_all_jsons(input_dir: str,
                                       standard_dir: str,
                                       qc_out_dir: Path):
    json_paths_input = get_all_files_walk(input_dir, 'json')
    json_paths_std = get_all_files_walk(standard_dir, 'json')

    with open(qc_out_dir / 'json_comparison_log.txt', 'w') as fp:
        for json_path_input in json_paths_input:
            _, _, json_suffix_input = \
                    get_naming_parts_bids(json_path_input.name)

            for json_path_std in json_paths_std:
                _, _, json_suffix_std = \
                        get_naming_parts_bids(json_path_std.name)
                if json_suffix_input == json_suffix_std:
                    fp.write('Comparing\n')
                    fp.write(f'- {json_path_input}\n')
                    fp.write(f'- {json_path_std}\n')
                    df_all_diff, df_all_shared = json_check(
                            [json_path_input, json_path_std], False)
                    if len(df_all_diff) > 0:
                        print(df_all_diff)
                        dfAsString = df_all_diff.to_string(
                                header=False, index=False)
                        fp.write(dfAsString + '\n')
                    else:
                        fp.write('*No difference\n')
                    fp.write('='*80)
                    fp.write('\n\n\n\n')


def compare_data_to_standard_all_bvals(input_dir: str,
                                       standard_dir: str,
                                       qc_out_dir: Path):
    bval_paths_input = get_all_files_walk(input_dir, 'bval')
    bval_paths_std = get_all_files_walk(standard_dir, 'bval')

    os.remove(qc_out_dir / 'bval_comparison_log.txt')
    for bval_path_input in bval_paths_input:
        _, _, bval_suffix_input = get_naming_parts_bids(bval_path_input.name)

        for bval_path_std in bval_paths_std:
            _, _, bval_suffix_std = get_naming_parts_bids(bval_path_std.name)
            if bval_suffix_input == bval_suffix_std:
                print(bval_suffix_input, bval_suffix_std)
                compare_bval_files([bval_path_input, bval_path_std],
                                    qc_out_dir / 'bval_comparison_log.txt')


def compare_data_to_standard(input_dir: str,
                             standard_dir: str,
                             qc_out_dir: Path):
    compare_data_to_standard_all_jsons(input_dir, standard_dir, qc_out_dir)
    compare_data_to_standard_all_bvals(input_dir, standard_dir, qc_out_dir)


def quick_figures(subject_dir: Path, session_name: str, outdir: Path):
    # quick figures
    # b0 signal
    fig_num_in_row = 3
    dwi_dir = subject_dir / f"ses-{session_name}" / 'dwi'

    threshold = 50
    dataset = []
    for nifti_path in dwi_dir.glob('*.nii.gz'):
        if 'sbref' not in nifti_path.name:
            nifti_prefix = nifti_path.parent / nifti_path.name.split('.')[0]
            data, bval_arr = get_diffusion_data_from_nifti_prefix(
                    nifti_prefix, '', threshold, False)
            dataset.append((data, bval_arr,
                            nifti_prefix.name.split('ses-')[1]))

    create_b0_signal_figure(dataset, outdir / 'summary_b0.png',
                            True, fig_num_in_row, wide_fig=False)


    dwi_dir = subject_dir / f"ses-{session_name}" / 'dwi'
    dataset = []
    for nifti_path in dwi_dir.glob('*.nii.gz'):
        if 'sbref' not in nifti_path.name:
            nifti_prefix = nifti_path.parent / nifti_path.name.split('.')[0]
            data, _ = load_data_bval(nifti_prefix)
            dataset.append((data, nifti_prefix.name.split('ses-')[1]))

    create_image_signal_figure(dataset, outdir / 'summary_dwi.png',
                            True, fig_num_in_row, wide_fig=False)


    fmri_dir = subject_dir / f"ses-{session_name}" / 'func'
    dataset = []
    for nifti_path in fmri_dir.glob('*.nii.gz'):
        if 'sbref' not in nifti_path.name:
            nifti_prefix = nifti_path.parent / nifti_path.name.split('.')[0]
            data = get_nondmri_data(nifti_prefix, 'nifti_prefix', '', False)
            dataset.append((data, nifti_prefix.name.split('ses-')[1]))

    create_image_signal_figure(dataset, outdir / 'summary_fmri.png',
                            True, 4, wide_fig=True)


def dicom_to_bids_with_quick_qc(args):
    args.session_name = re.sub('[_-]', '', args.session_name)

    # dicom to bids
    dicom_to_bids(args.input_dir, args.subject_name,
                  args.session_name, args.output_dir)

    # variable settings
    subject_dir = Path(args.output_dir) / ('sub-' + re.sub(
            '[_-]', '', args.subject_name))
    qc_out_dir = Path(args.output_dir) / 'quick_qc' / \
            subject_dir.name / args.session_name
    qc_out_dir.mkdir(exist_ok=True, parents=True)

    # CSA extraction
    df = get_dicom_files_walk(args.input_dir, True)
    csa_diff_df, csa_common_df = get_diff_in_csa_for_all_measures(
            df, get_same=True)
    csa_df = pd.concat([csa_diff_df, csa_common_df],
                    sort=False).sort_index().T
    csa_df['series_num'] = csa_df.index.str.extract('(\d+)').astype(int).values
    csa_df.sort_values(by='series_num').drop(
            'series_num', axis=1).to_csv(qc_out_dir / 'csa_headers.csv')

    if args.standard_dir:
        # diff comparison (json & image figure)
        compare_data_to_standard(subject_dir, args.standard_dir, qc_out_dir)

if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    dicom_to_bids_with_quick_qc(args)
