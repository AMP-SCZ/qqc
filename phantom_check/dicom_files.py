import pandas as pd
from pathlib import Path
import phantom_check
import os
import pydicom
from typing import Union
import time
import numpy as np
import shutil
import logging


logger = logging.getLogger(__name__)


def get_dicom_files_walk(root: Union[Path, str],
                         one_file_for_series=False) -> pd.DataFrame:
    '''Find all dicom path under the root and return it as pandas DataFrame

    Key arguments:
        root: root directory of the dicom for a subject, str or Path.
        one_file_for_series: True if to return a df summary of each series,
                             bool.

    Notes:
        one_file_for_series = True, assumes there is a single series contained
        in each sub directories under the dicom root.
    '''
    dicom_paths = []
    start = time.time()

    # walk through the root
    for root, dirs, files in os.walk(root):
        for file in files:
            if file.lower().endswith('dcm') or file.lower().endswith('ima'):
                dicom_paths.append(os.path.join(root, file))
            if one_file_for_series:  # to load a single file for each dir
                break
    end = time.time()
    t = end - start
    logger.debug(f'Time taken to walk through dicom root: {t}')

    # get dataframe and convert them into pydicom objects
    df = pd.DataFrame({'file_path': dicom_paths})
    start = time.time()
    df['pydicom'] = df.file_path.apply(lambda x: pydicom.read_file(x))
    end = time.time()
    t = end - start
    logger.debug(f'Time taken to dicomise dicom all paths: {t}')

    start = time.time()
    df['norm'] = df.pydicom.apply(lambda x:
            get_additional_info(x, '0008', '0008'))
    df['series'] = df.pydicom.apply(lambda x: get_series_info(x))
    df['series_num'] = df['series'].str[0]
    df['series_desc'] = df['series'].str[1]
    df['series_uid'] = df['series'].str[2]
    df.drop('series', axis=1, inplace=True)

    # if unique dicom for a series is required
    df_tmp = pd.DataFrame()
    if one_file_for_series:
        for group, table in df.groupby(
                ['series_num', 'series_desc', 'series_uid']):
            # get the first dicom file
            df_tmp = pd.concat([df_tmp, table.iloc[[0]]], axis=0)
    df = df_tmp.reset_index().drop('index', axis=1)

    # series_scan column to detect if there is any rescan
    gb_series = df.groupby(['series_num', 'series_desc', 'series_uid'])
    unique_count_df = gb_series.count().reset_index()
    series_names, counts = np.unique(unique_count_df['series_desc'],
                                     return_counts=True)

    for series_name, count in zip(series_names, counts):
        if count > 1:
            # index = df['series_names
            df_tmp = df[df['series_desc'] == series_name]
            for num, unique_series_uid in enumerate(
                    df_tmp.series_uid.unique(), 1):
                index = df[df['series_uid'] == unique_series_uid].index
                df.loc[index, 'series_scan'] = num
        else:
            index = df[df['series_desc'] == series_name].index
            df.loc[index, 'series_scan'] = 1

    end = time.time()
    t = end - start
    logger.debug(f'Time taken to extract info from pydicom objects: {t}')
    # df.drop('pydicom', axis=1, inplace=True)

    return df


def get_series_info(dicom: pydicom.dataset.FileDataset):
    '''Extract series information from pydicom dataset'''
    num = dicom.get(('0020', '0011')).value
    description = dicom.get(('0008', '103e')).value
    instance_uid = dicom.get(('0020', '000e')).value

    return num, description, instance_uid


def get_additional_info(dicom: pydicom.dataset.FileDataset,
                        group_number: str,
                        element_number: str) -> str:
    '''Get additional information from dicom'''
    info = dicom.get((group_number, element_number)).value
    return info


def get_csa_header(dicom: pydicom.dataset.FileDataset) -> pd.DataFrame:
    '''Clean up private information extracted'''
    info = get_additional_info(dicom, '0029', '1020')
    extracted_text = info.decode(errors='ignore').split(
            '### ASCCONV')[1]

    new_lines = []
    for line in extracted_text.split('\n'):
        if line.startswith('sAdjData') or line.startswith('sSliceArray'):
            new_lines.append(line)

    df = pd.DataFrame({'raw_line': new_lines})
    df['var'] = df.raw_line.str.extract(r'(\S+)\s+')
    df['value'] = df.raw_line.str.extract(r'=\s+(\S+)')
    df.drop('raw_line', axis=1, inplace=True)

    return df


def rearange_dicoms(dicom_df: pd.DataFrame,
                    new_root: Union[str, Path]) -> None:
    '''Copy the dicom in a new format for preprocessing'''
    new_root = Path(new_root)

    
    # series
    for (num, name, scan), table in dicom_df.groupby(
            ['series_num', 'series_desc', 'series_scan']):
        series_dir_path = new_root / 'ses-001' / f'{num:02}_{name}'
        series_dir_path.mkdir(exist_ok=True, parents=True)
        for _, row in table.iterrows():
            shutil.copy(row['file_path'], series_dir_path)
