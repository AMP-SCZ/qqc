import os
import re
import json
import nibabel as nb
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple, List
import logging

from qqc.utils.files import get_all_files_walk
from qqc.utils.names import get_naming_parts_bids
from qqc.utils.visualize import print_diff_shared
from qqc.utils.files import ampscz_json_load


logger = logging.getLogger(__name__)

class NoDwiException(Exception):
    pass



def extract_digits_from_3dFWHMx(output_str: str) -> pd.DataFrame:
    pass


def get_smoothness(input_nifti: Path) -> Tuple[List[float], List[float]]:
    command = f'3dFWHMx \
            -input {input_nifti} \
            -automask -ACF NULL -ShowMeClassicFWHM'
    output_text = os.popen(command).read()
    digit_list = re.findall('\d+\.\d+', output_text)
    fwhm_model_param = [float(x) for x in digit_list[-8:-4]]
    acf_model_param = [float(x) for x in digit_list[-4:]]

    return (fwhm_model_param, acf_model_param)

def compare_volume_to_standard_all_nifti(input_dir: str,
                                         standard_dir: str,
                                         qc_out_dir: Path):
    nifti_paths_input = get_all_files_walk(input_dir, 'nii.gz')
    nifti_paths_std = get_all_files_walk(standard_dir, 'nii.gz')

    volume_comparison_log = qc_out_dir / \
            'volume_slice_number_comparison_log.txt'

    volume_comparison_df = pd.DataFrame()
    num = 0

    for nifti_input in nifti_paths_input:
        _, _, nifti_suffix_input = get_naming_parts_bids(nifti_input.name)

        input_json_file_name = nifti_input.name.split('.')[0] + '.json'
        input_json = nifti_input.parent / input_json_file_name

        if not input_json.is_file():  # likely be from partial data
            volume_comparison_df.loc[num, 'nifti_suffix'] = nifti_suffix_input
            volume_comparison_df.loc[num, 'series_num'] = 1000 + num
            continue

        with open(input_json, 'r') as json_file:
            data = ampscz_json_load(json_file)

        series_num = data['SeriesNumber']
        series_desc = data['SeriesDescription'].lower()
        if 'ImageTypeText' in data.keys():
            image_type = data['ImageTypeText']
        else:
            image_type = data['ImageType']
        if 'PhaseEncodingDirection' in data.keys():
            encoding_dir = data['PhaseEncodingDirection']
        else:
            encoding_dir = ''

        for nifti_std in nifti_paths_std:
            _, _, nifti_suffix_std = get_naming_parts_bids(nifti_std.name)

            std_json_filename = nifti_std.name.split('.')[0] + '.json'
            std_json = nifti_std.parent / std_json_filename

            with open(std_json, 'r') as json_file:
                data = ampscz_json_load(json_file)

            std_series_num = data['SeriesNumber']
            std_series_desc = data['SeriesDescription'].lower()
            if 'ImageTypeText' in data.keys():
                std_image_type = data['ImageTypeText']
            else:
                std_image_type = data['ImageType']
            if 'PhaseEncodingDirection' in data.keys():
                std_encoding_dir = data['PhaseEncodingDirection']
            else:
                std_encoding_dir = ''

            if (series_desc == std_series_desc):
                if ('localizer' in series_desc.lower()) or \
                        ('scout' in series_desc.lower()):
                    if not encoding_dir == std_encoding_dir:
                        continue

                img_shape_std = nb.load(nifti_std).shape
                img_shape_input = nb.load(nifti_input).shape
                try:
                    volume_comparison_df.loc[num, 'series_num'] = series_num
                    volume_comparison_df.loc[num, 'series_desc'] = series_desc
                    volume_comparison_df.loc[num, 'series_desc_std'] = std_series_desc
                    volume_comparison_df.loc[num, 'nifti_suffix'] = nifti_suffix_input
                    volume_comparison_df.loc[num, 'nifti_suffix_std'] = nifti_suffix_std
                    volume_comparison_df.loc[num, 'input shape'] = str(img_shape_input)
                    volume_comparison_df.loc[num, 'standard shape'] = str(img_shape_std)
                    break

                except:
                    pass
            elif (series_desc == std_series_desc):
                print(series_desc)
                print(std_image_type)
                print(image_type)

        num += 1

    if len(volume_comparison_df) == 0:
        print('No matching series name - GE data')
        return


    volume_comparison_df['check'] = (volume_comparison_df['input shape'] ==
            volume_comparison_df['standard shape']).map(
                    {True: 'Pass', False: 'Fail'})

    if volume_comparison_df.series_desc.str.contains('localizer').any():
        if_localizer = volume_comparison_df.series_desc.str.contains(
                'localizer', na=False)
        localizer_index = volume_comparison_df[if_localizer].index
        volume_comparison_df.at[localizer_index, 'check'] = \
            volume_comparison_df[if_localizer]['check'].map(
                    {'Pass': 'Pass', 'Fail': 'Warning'})

    if volume_comparison_df.series_desc.str.contains('scout').any():
        if_scout = volume_comparison_df.series_desc.str.contains(
                'scout', na=False)
        scout_index = volume_comparison_df[if_scout].index
        volume_comparison_df.at[scout_index, 'check'] = volume_comparison_df[
            if_scout]['check'].map({'Pass': 'Pass', 'Fail': 'Warning'})

    volume_comparison_df.series_num = \
            volume_comparison_df.series_num.astype(int)

    volume_comparison_df.set_index('series_num', inplace=True)

    volume_comparison_summary = volume_comparison_df.iloc[[0]].copy()
    volume_comparison_summary.index = ['Summary']
    volume_comparison_summary['series_desc'] = ''
    volume_comparison_summary['series_desc_std'] = ''
    volume_comparison_summary['nifti_suffix'] = ''
    volume_comparison_summary['nifti_suffix_std'] = ''
    volume_comparison_summary['input shape'] = ''
    volume_comparison_summary['standard shape'] = ''

    volume_comparison_summary['check'] = 'Pass' if \
            ~(volume_comparison_df['check'] == 'Fail').any() else 'Fail'

    volume_comparison_df = pd.concat([volume_comparison_summary,
                                      volume_comparison_df.sort_index()])

    volume_comparison_df.to_csv(
            qc_out_dir / '03_volume_slice_number_comparison_log.csv')



def compare_volume_to_standard_all_nifti_test(input_dir: str,
                                         standard_dir: str,
                                         qc_out_dir: Path):
    nifti_paths_input = get_all_files_walk(input_dir, 'nii.gz')
    nifti_paths_std = get_all_files_walk(standard_dir, 'nii.gz')

    volume_comparison_log = qc_out_dir / \
            'volume_slice_number_comparison_log.txt'

    volume_comparison_df = pd.DataFrame()
    num = 0

    for nifti_input in nifti_paths_input:
        try:
            _, _, nifti_suffix_input = \
                get_naming_parts_bids(nifti_input.name)
        except:
            nifti_suffix_input = nifti_input.name[:-7]

        input_json = nifti_input.parent / (
                nifti_input.name[:-7] + '.json')
        with open(input_json, 'r') as json_file:
            data = ampscz_json_load(json_file)

            image_type = data['ImageType']
            series_num = data['SeriesNumber']
            series_desc = data['SeriesDescription'].lower()

        img_shape_input = nb.load(nifti_input).shape
        volume_comparison_df.loc[num, 'template'] = False
        volume_comparison_df.loc[num, 'series_num'] = series_num
        volume_comparison_df.loc[num, 'series_desc'] = series_desc
        volume_comparison_df.loc[num, 'nifti_suffix'] = nifti_suffix_input
        volume_comparison_df.loc[num, 'input shape'] = str(img_shape_input)
        num += 1

    for nifti_std in nifti_paths_std:
        try:
            _, _, nifti_suffix_std = get_naming_parts_bids(
                    nifti_std.name)
        except:
            nifti_suffix_std = nifti_std.name.split('.')[:-7]

        # if partial_rescan:
        std_json = nifti_std.parent / (nifti_std.name[:-7] + '.json')
        with open(std_json, 'r') as json_file:
            data = ampscz_json_load(json_file)
            std_image_type = data['ImageType']
            std_series_num = data['SeriesNumber']
            std_series_desc = data['SeriesDescription'].lower()

        img_shape_std = nb.load(nifti_std).shape
        volume_comparison_df.loc[num, 'template'] = True
        volume_comparison_df.loc[num, 'series_num'] = series_num
        volume_comparison_df.loc[num, 'series_desc_std'] = std_series_desc
        volume_comparison_df.loc[num, 'nifti_suffix_std'] = nifti_suffix_std
        volume_comparison_df.loc[num, 'standard shape'] = str(img_shape_std)
        num += 1

    if len(volume_comparison_df) == 0:
        print('No matching series name - GE data')
        return

    volume_comparison_df.series_num = \
            volume_comparison_df.series_num.astype(int)

    volume_comparison_df.set_index('series_num', inplace=True)
    volume_comparison_df.sort_values([
        'template', 'series_num']).to_csv(
            qc_out_dir / '03_volume_slice_number_comparison_log.csv')



def is_nifti_16bit(diffusion_nifti_file: Path) -> Tuple[bool, float]:
    '''Estimates maximum intensity in the image and returns True if > 4096'''
    data = nb.load(diffusion_nifti_file).get_fdata()
    max_val = np.max(data)
    if max_val > 4096:
        return (True, np.max(data))
    else:
        return (False, np.max(data))


def is_dwi_dir_16bit(dwi_nifti_dir: Path) -> Tuple[bool, float]:
    for root, dirs, files in os.walk(dwi_nifti_dir):
        for file in files:
            if file.endswith('.nii.gz'):
                return is_nifti_16bit(Path(root) / file)
                
    raise NoDwiException


def is_fmap_dir_16bit(fmap_nifti_dir: Path) -> Tuple[bool, float]:
    for root, dirs, files in os.walk(fmap_nifti_dir):
        for file in files:
            if file.endswith('.nii.gz'):
                return is_nifti_16bit(Path(root) / file)
                
    raise NoDwiException

def is_session_dir_16bit(nifti_root: Path) -> Tuple[bool, float]:
    for root, dirs, files in os.walk(nifti_root):
        for directory in dirs:
            if directory == 'dwi':
                return is_dwi_dir_16bit(Path(root) / directory)
            else:
                continue
                
    raise NoDwiException


def compare_bit_to_std(input_dir: str,
                       standard_dir: str,
                       qc_out_dir: Path) -> None:
    bit_comparison_log = qc_out_dir / 'bit_check.csv'
    try:
        input_bit = is_session_dir_16bit(input_dir)  # (bool, float)
    except NoDwiException:
        logger.critical('No B0 nifti found in the input data')
        input_bit = 'no data'
    std_bit = is_session_dir_16bit(standard_dir)

    df = pd.DataFrame({
        'Input data': [input_bit[0], input_bit[1]],
        'Standard data': [std_bit[0], std_bit[1]]})
    df.index = ['16 bit', 'B0 Max value']
    df.index.name = ''
    df.loc['16 bit', 'check'] = df.loc['16 bit']['Input data'] == \
            df.loc['16 bit']['Standard data']
    df['check'] = df['check'].map({True: 'Pass', False: 'Fail'})
                        
    df.to_csv(bit_comparison_log)
