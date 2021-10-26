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
from typing import List


logger = logging.getLogger(__name__)


all_elements_to_extract = [
    'AcquisitionMatrix',
    'AngioFlag',
    'BodyPartExamined', 'Columns',
    'ContentDate', 'DeviceSerialNumber',
    'EchoTime', 'EchoTrainLength', 'RepetitionTime',
    'FlipAngle', 'VariableFlipAngleFlag'
    'ImageOrientationPatient', 'ImagePositionPatient',
    'ImageType', 'InPlanePhaseEncodingDirection',
    'InstitutionAddress', 'InstitutionName', 'InstitutionalDepartmentName',
    'MRAcquisitionType', 'MagneticFieldStrength', 'Manufacturer',
    'ManufacturerModelName', 'Modality',
    'NumberOfAverages', 'NumberOfPhaseEncodingSteps',
    'PixelBandwidth', 'PixelSpacing', 'PositionReferenceIndicator',
    'ProtocolName',
    'Rows', 'SAR', 'SamplesPerPixel',
    'ScanningSequence', 'SequenceName', 'SequenceVariant',
    'SeriesDescription', 'SeriesInstanceUID', 'SeriesNumber', 'SeriesTime',
    'SliceLocation', 'SliceThickness', 'SpacingBetweenSlices',
    'SoftwareVersions', 'StudyDescription',
    'TransmitCoilName'
    ]


def get_dicom_files_walk(root: Union[Path, str],
                         one_file_for_series=False) -> pd.DataFrame:
    '''Find all dicom path under the root and return it as pandas DataFrame

    Key arguments:
        root: root directory of the dicom for a subject, str or Path.
        one_file_for_series: True if to return a df summary of each series,
                             bool.

    Returns:
        df: pd.DataFrame with file path, pydicom object, series name and 
            numberk, uid

    Notes:
        one_file_for_series = True, assumes there is a single series contained
        in each sub directories under the dicom root.
    '''
    dicom_paths = []
    start = time.time()

    # walk through the root
    for root, dirs, files in os.walk(root):
        for file in files:
            # includes the logics to detect dicoms without dcm / ima extension
            if file.lower().endswith('dcm') or file.lower().endswith('ima') \
                    or (file.startswith('MR') and \
                        len(Path(file).name.split('.')[-1]) > 10):
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
    if one_file_for_series:
        df_tmp = pd.DataFrame()
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


def get_additional_info_by_elem(dicom: pydicom.dataset.FileDataset,
                                element_name: str) -> str:
    '''Get additional information from dicom by element name'''
    try:
        return dicom.data_element(element_name).value
    except:
        return ''


def add_detailed_info_to_summary_df(df: pd.DataFrame,
                                    element_names: List[str]) -> tuple:
    '''Get additional information from dicom by element name'''

    for element_name in element_names:
        data = df.pydicom.apply(
                lambda x: get_additional_info_by_elem(x, element_name))
        df[element_name] = data

    return df


def get_csa_header(dicom: pydicom.dataset.FileDataset) -> pd.DataFrame:
    '''Clean up private information extracted'''
    info = get_additional_info(dicom, '0029', '1020')
    extracted_text = info.decode(errors='ignore').split(
            '### ASCCONV')[1]

    new_lines = []
    for line in extracted_text.split('\n'):
        if line.startswith('sAdjData.sAdjVolume') \
                or line.startswith('sSliceArray.asSlice[0].'):
            new_lines.append(line)

    df = pd.DataFrame({'raw_line': new_lines})
    df['var'] = df.raw_line.str.extract(r'(\S+)\s+')
    df['value'] = df.raw_line.str.extract(r'=\s+(\S+)')
    df.drop('raw_line', axis=1, inplace=True)

    return df


def get_diff_in_csa_for_all_measures(df: pd.DataFrame,
                                     measures: List[str] = None,
                                     get_same: bool = False) -> pd.DataFrame:
    '''Get a dataframe, including the rows that are different across columns

    Key Arguments:
        df: dataframe of dicom files as rows, with 'pydicom' column, which 
            contains the pydicom object.
        measures: list of strings to select the name of series in interest,
                  list of str.
        get_same: options to return dataframe including the rows that are the
                  same across columns as well, bool. If True, this function
                  returns tuple of pd.DataFrame.
    
    Returns:
        pd.DataFrame or Tuple[pd.DataFrame]

    Notes:
        - in the comparison of values, NaN cells are ignored.
    '''

    dfs = []
    for index, row in df.iterrows():
        if measures is not None:
            if any([x in row.series_desc.lower() for x in measures]):
                df_tmp = get_csa_header(row['pydicom'])
                df_tmp = df_tmp.set_index('var')
                df_tmp.columns = [f'{row.series_num}_{row.series_desc}']
                dfs.append(df_tmp)

        elif 'dmri' in row.series_desc.lower() or \
             'fmri'in row.series_desc.lower()  or \
             't1w'in row.series_desc.lower()  or \
             't2w'in row.series_desc.lower()  or \
             'distortion'in row.series_desc.lower():
            df_tmp = get_csa_header(row['pydicom'])
            df_tmp = df_tmp.set_index('var')
            df_tmp.columns = [f'{row.series_num}_{row.series_desc}']
            dfs.append(df_tmp)

    csa_df = pd.concat(dfs, axis=1, sort=False)

    diff_df = csa_df[csa_df.apply(
        lambda x: x[~x.isnull()].nunique() != 1, axis=1)].T.sort_index().T

    if not get_same:
        return diff_df
    else:
        common_df = csa_df[csa_df.apply(
            lambda x: x[~x.isnull()].nunique() == 1, axis=1)].T.sort_index().T
        return diff_df, common_df


def rearange_dicoms(dicom_df: pd.DataFrame,
                    new_root: Union[str, Path],
                    subject: str,
                    session: str,
                    force: bool = False) -> None:
    '''Copy the dicom in a new format for preprocessing'''
    new_root = Path(new_root)
    
    # series
    for (num, name, scan), table in dicom_df.groupby(
            ['series_num', 'series_desc', 'series_scan']):
        series_dir_path = new_root / subject / f'ses-{session}' / \
                f'{num:02}_{name}'

        if not force and series_dir_path.is_dir() \
                and len(table) == len(list(series_dir_path.glob('*'))):
            print(f'Not overwriting {series_dir_path}')
            continue

        series_dir_path.mkdir(exist_ok=True, parents=True)
        for _, row in table.iterrows():
            shutil.copy(row['file_path'], series_dir_path)
