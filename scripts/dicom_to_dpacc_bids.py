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
pd.set_option('max_columns', 50)
pd.set_option('max_rows', 500)
import json
import nibabel as nb
        

def parse_args(argv):
    '''Parse inputs coming from the terminal'''
    parser = argparse.ArgumentParser(description='dicom_to_depacc_bids')

    # image input related options
    parser.add_argument('--input_dir', '-i', type=str,
                        help='Raw dicom root directory.')

    parser.add_argument('--subject_name', '-s', type=str,
                        help='Subject name.')

    parser.add_argument('--session_name', '-ss', type=str,
                        help='Session name.')

    parser.add_argument('--output_dir', '-o', type=str,
                        help='BIDS Output directory')

    parser.add_argument('--standard_dir', '-std', type=str,
                        help='Root of a standard dataset to compare to')

    parser.add_argument('--skyra', '-sk', action='store_true',
                        help='For skyra scans - match DWI / compared to other '
                             'skyra etc. (Option for U24 study)')

    # extra options
    args = parser.parse_args(argv)
    return args


def dicom_to_bids(input_dir: str, subject_name: str,
                  session_name: str, output_dir: str) -> pd.DataFrame:
    '''Rearrange before converting to BIDS structure using dicom headers

    Key arguments:
        - input_dir: raw dicom root directory, str.
        - subject_name: name of the subject, str.
        - session_name: name of the session, str.
        - output_dir: output BIDS raw directory, str.

    Returns:
        - df_full: output pd.DataFrame from
                   phantom_check.dicom_files.get_dicom_files_walk function

    Notes:
        - currently saving newly arranged dicom files under 'dicom' directory
          under the output_dir. To be fully follow BIDS suggestions, this 
          location should be updated in future.
    '''
    print(f'Walking through {input_dir}, searching for dicom files')
    df_full = get_dicom_files_walk(input_dir)
    print(f'File walk - complete')

    # assert number of series
    series_num_unmatched = False
    if not df_full.set_index == '30':
        print('='*80)
        print('Please double check number of series')
        print('='*80)
        series_num_unmatched = True


    # with tempfile.TemporaryDirectory() as tmpdir:
    dicom_clearned_up_output = Path(output_dir) / 'dicom'
    print('Copying dicoms to a preset structure')
    print(f'\tto {dicom_clearned_up_output}')
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
                                       qc_out_dir: Path):
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

            for json_path_std in json_paths_std:
                _, _, json_suffix_std = \
                        get_naming_parts_bids(json_path_std.name)
                if json_suffix_input == json_suffix_std:
                    fp.write(f'Comparing {series_number} {series_name}\n')
                    fp.write(f'- {json_path_input}\n')
                    fp.write(f'- {json_path_std}\n')
                    df_all_diff, df_all_shared = json_check(
                            [json_path_input, json_path_std], False)
                    if len(df_all_diff) > 0:
                        dfAsString = df_all_diff.to_string()

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


def compare_volume_to_standard_all_nifti(input_dir: str,
                                         standard_dir: str,
                                         qc_out_dir: Path):
    nifti_paths_input = get_all_files_walk(input_dir, 'nii.gz')
    nifti_paths_std = get_all_files_walk(standard_dir, 'nii.gz')

    volume_comparison_log = qc_out_dir / \
            'volume_slice_number_comparison_log.txt'
    with open(volume_comparison_log, 'w') as fp:
        for nifti_std in nifti_paths_std:
            for nifti_input in nifti_paths_input:
                _, _, nifti_suffix_input = \
                    get_naming_parts_bids(nifti_input.name)

                _, _, nifti_suffix_std = \
                    get_naming_parts_bids(nifti_std.name)

                if nifti_suffix_input == nifti_suffix_std:
                    img_shape_std = nb.load(nifti_std).shape
                    img_shape_input = nb.load(nifti_input).shape

                    fp.write('Comparing data array shape '
                             f"{nifti_input}\n")
                    if img_shape_std == img_shape_input:
                        fp.write('Data array in the same shape - '
                                 f'{img_shape_input}\n\n')
                    else:
                        fp.write('**Data array in a different shape\n')
                        fp.write(f'{nifti_input} : {img_shape_input}\n')
                        fp.write(f'{nifti_std} : {img_shape_std}\n')
                        fp.write('\n\n')


def compare_data_to_standard(input_dir: str,
                             standard_dir: str,
                             qc_out_dir: Path):
    compare_data_to_standard_all_jsons(input_dir, standard_dir, qc_out_dir)
    compare_data_to_standard_all_bvals(input_dir, standard_dir, qc_out_dir)
    compare_volume_to_standard_all_nifti(input_dir, standard_dir, qc_out_dir)


def quick_figures(subject_dir: Path, outdir: Path):
    # quick figures
    # b0 signal
    fig_num_in_row = 3
    dwi_dir = subject_dir / 'dwi'

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


    dwi_dir = subject_dir / 'dwi'
    dataset = []
    for nifti_path in dwi_dir.glob('*.nii.gz'):
        if 'sbref' not in nifti_path.name:
            nifti_prefix = nifti_path.parent / nifti_path.name.split('.')[0]
            data, _ = load_data_bval(nifti_prefix)
            dataset.append((data, nifti_prefix.name.split('ses-')[1]))

    create_image_signal_figure(dataset, outdir / 'summary_dwi.png',
                            True, fig_num_in_row, wide_fig=False)


    fmri_dir = subject_dir / 'func'
    dataset = []
    for nifti_path in fmri_dir.glob('*.nii.gz'):
        if 'sbref' not in nifti_path.name:
            nifti_prefix = nifti_path.parent / nifti_path.name.split('.')[0]
            data = get_nondmri_data(nifti_prefix, 'nifti_prefix', '', False)
            dataset.append((data, nifti_prefix.name.split('ses-')[1]))

    create_image_signal_figure(dataset, outdir / 'summary_fmri.png',
                            True, 4, wide_fig=True)


def bids_file_name_to_series_num(filename: str) -> int:
    if filename.endswith('.json'):
        with open(filename, 'r') as fp:
            return json.load(fp)['SeriesNumber']


def within_phantom_qc(session_dir: Path, qc_out_dir: Path):
    json_paths_input = get_all_files_walk(session_dir, 'json')

    with open(qc_out_dir / 'within_phantom_qc.txt', 'w') as fp:
        fp.write('Checking shim settings'+ '\n')
        df_all_diff, df_all_shared = json_check_for_a_session(
                json_paths_input,
                print_diff=False, print_shared=False,
                specific_field='ShimSetting')
        fp.write(df_all_diff.to_string() + '\n\n')

        fp.write('Checking image orientation in dMRI, fMRI and '
                 'distortionMaps'+ '\n')
        non_anat_json_paths_input = [x for x in json_paths_input
                                      if x.parent.name != 'anat']
        df_all_diff, df_all_shared = json_check_for_a_session(
                non_anat_json_paths_input,
                print_diff=False, print_shared=False,
                specific_field='ImageOrientationPatientDICOM')
        if df_all_diff.empty:
            fp.write('Image Orientations are consistent' + '\n\n')
            fp.write(df_all_shared.to_string() + '\n\n')
        else:
            fp.write(df_all_diff.to_string() + '\n\n')

        # anat
        fp.write('Checking image orientation in anat'+ '\n')
        anat_json_paths_input = [x for x in json_paths_input
                                  if x.parent.name == 'anat']
        df_all_diff, df_all_shared = json_check_for_a_session(
                anat_json_paths_input,
                print_diff=False, print_shared=False,
                specific_field='ImageOrientationPatientDICOM')
        if df_all_diff.empty:
            fp.write('Image Orientations are consistent' + '\n\n')
            fp.write(df_all_shared.to_string() + '\n\n')
        else:
            fp.write(df_all_diff.to_string() + '\n\n')


def save_csa(df_full: pd.DataFrame, qc_out_dir: Path) -> None:
    csa_diff_df, csa_common_df = get_diff_in_csa_for_all_measures(
            df_full, get_same=True)
    csa_df = pd.concat([csa_diff_df, csa_common_df],
                    sort=False).sort_index().T
    csa_df['series_num'] = csa_df.index.str.extract('(\d+)').astype(int).values
    csa_df.sort_values(by='series_num').drop(
            'series_num', axis=1).to_csv(qc_out_dir / 'csa_headers.csv')


def dicom_to_bids_with_quick_qc(args) -> None:
    '''Sort dicoms, before converting them to BIDS nifti. Also run quick QC.

    Key arguments:
        args: Argparse parsed arguments.
            - Must have attributes
              - subject_name: name of the subject, str.
              - session_name: name of the session, str.
              - input_dir: raw dicom root directory, str.
              - output_dir: output BIDS raw directory, str.

            - Optional attributes
              - standard_dir: root of a standard dataset to compare the input
                              data to, str.
              - skyra: True if the input_dir is skyra data, bool.

    1. run dicom to dicom BIDS
    '''
    args.session_name = re.sub('[_-]', '', args.session_name)

    # raw dicom to BIDS
    # raw dicom -> cleaned up dicom structure -> BIDS
    df_full = dicom_to_bids(args.input_dir, args.subject_name,
                            args.session_name, args.output_dir)

    # QC start
    subject_dir = Path(args.output_dir) / \
        ('sub-' + re.sub('[_-]', '', args.subject_name))
    session_dir = subject_dir / ('ses-' + args.session_name)
    qc_out_dir = Path(args.output_dir) / 'quick_qc' / \
        subject_dir.name / args.session_name
    qc_out_dir.mkdir(exist_ok=True, parents=True)

    # within data QC
    print('Within phantom QC')
    within_phantom_qc(session_dir, qc_out_dir)

    # CSA extraction
    print('CSA extraction')
    df_with_one_series = pd.concat([
        x[1].iloc[0] for x in df_full.groupby('series_num')], axis=1).T
    save_csa(df_with_one_series, qc_out_dir)

    if args.standard_dir:
        print('Comparison to standard')
        compare_data_to_standard(session_dir, args.standard_dir, qc_out_dir)

        # skyra scans have different number of diffusion weighting,
        # therefore, need to compare DWI manually
        if args.skyra:
            compare_data_to_standard_lazy(
                    session_dir, args.standard_dir, qc_out_dir)


    if args.skyra:
        skyra_preset_loc = '/data/predict/phantom_data/phantom_data_BIDS/' \
                           'sub-PrescientAdelaideSkyra/ses-humanpilot'
        print('Comparison to Skyra standard')
        print(f'Preset to {skyra_preset_loc}')
        qc_out_dir_skyra = qc_out_dir / 'comparison_to_skyra_Adelaide'
        qc_out_dir_skyra.mkdir(exist_ok=True, parents=True)
        compare_data_to_standard(session_dir, skyra_preset_loc, qc_out_dir_skyra)

    print('Creating summary figures')
    quick_figures(session_dir, qc_out_dir)


def compare_data_to_standard_lazy(input_dir: str,
                                  standard_dir: str,
                                  qc_out_dir: Path):
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


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    dicom_to_bids_with_quick_qc(args)
