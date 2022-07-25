import nibabel as nb
import numpy as np
import pandas as pd
import json
from pathlib import Path
import re

from qqc.utils.files import get_all_files_walk
from qqc.utils.names import get_naming_parts_bids
from qqc.utils.visualize import print_diff_shared


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
        _, _, nifti_suffix_input = \
            get_naming_parts_bids(nifti_input.name)

        input_json = nifti_input.parent / (
                nifti_input.name.split('.')[0] + '.json')
        with open(input_json, 'r') as json_file:
            data = json.load(json_file)

            image_type = data['ImageType']
            series_num = data['SeriesNumber']
            series_desc = data['SeriesDescription'].lower()

        print()
        for nifti_std in nifti_paths_std:
            _, _, nifti_suffix_std = \
                get_naming_parts_bids(nifti_std.name)
            # if partial_rescan:
            std_json = nifti_std.parent / (
                    nifti_std.name.split('.')[0] + '.json')
            with open(std_json, 'r') as json_file:
                data = json.load(json_file)
                std_image_type = data['ImageType']
                std_series_num = data['SeriesNumber']
                std_series_desc = data['SeriesDescription'].lower()

            print('----')
            print('input')
            print(series_desc)
            print(image_type)
            print('output')
            print(std_series_desc)
            print(std_image_type)
            print('----')

            # # for JE site, extracted image type is different
            # if (series_desc == std_series_desc):
                # pass
                # # print(series_desc, std_series_desc)
                # # print(image_type, std_image_type)

            # for var_to_remove in 'RESAMPLED', 'FMRI', 'NONE', 'MOSAIC':
                # if var_to_remove in image_type:
                    # image_type.pop(image_type.index(var_to_remove))
                # if var_to_remove in std_image_type:
                    # std_image_type.pop(std_image_type.index(var_to_remove))

            # ###

            if (series_desc == std_series_desc) & \
                    (all([x in std_image_type for x in image_type])):
                # print(series_desc, std_series_desc)
                # print(image_type, std_image_type)
                # make sure the number of localizer and scout files are
                # the same
                if ('localizer' in series_desc.lower()) or \
                        ('scout' in series_desc.lower()):
                    if nifti_input.name[-8] != nifti_std.name[-8]:
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

        num += 1

    print(volume_comparison_df)
    volume_comparison_df['check'] = (volume_comparison_df['input shape'] ==
            volume_comparison_df['standard shape']).map(
                    {True: 'Pass', False: 'Fail'})

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



