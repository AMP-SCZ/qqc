import pandas as pd
from pathlib import Path
import qqc
import os
import pydicom
from typing import Union
import time
import numpy as np
import shutil
import logging
from typing import List
import re
import sys
import json

from qqc.utils.files import get_all_files_walk

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


def get_dicom_counts(sorted_dicom_dir: Path, **kwargs) -> pd.DataFrame:
    debug = kwargs.get('debug', False)

    logger.info(sorted_dicom_dir)
    df = pd.DataFrame({'series_dir': list(sorted_dicom_dir.glob('*'))})
    df['dicom_count'] = df.series_dir.apply(lambda x: len(list(x.glob('*'))))
    df['series_dir'] = df.series_dir.apply(lambda x: x.name)
    df['series_num'] = df.series_dir.apply(lambda x: x.split('_')[0]).astype(
            int)

    logger.info(df)
    df['series_dir'] = df['series_dir'].str.extract(r'\d+_(.+)')
    df.sort_values('series_num', inplace=True)
    df = df[['series_num', 'series_dir', 'dicom_count']]

    if debug:
        logger.info(f'debug: {debug}')
        logger.info(f'sorted_dicom_dir: {sorted_dicom_dir}')
        logger.info(f'count df:\n{df}')

    return df


def update_dicom_counts(dicom_count_input_df: pd.DataFrame,
                        session_dir: Path,
                        **kwargs) -> pd.DataFrame:
    json_paths_input = get_all_files_walk(session_dir, 'json')
    debug = kwargs.get('debug', False)

    # series_num and series_description of json files
    series_num_desc_tuples = []
    for json_file in json_paths_input:
        with open(json_file, 'r') as fp:
            data = json.load(fp)
            series_num_desc_tuples.append((data['SeriesDescription'],
                                           data['SeriesNumber']))

    for index, row in dicom_count_input_df.iterrows():
        input_tuple = (row['series_dir'], row['series_num'])
        if input_tuple in series_num_desc_tuples:
            dicom_count_input_df.loc[index, 'heudiconv converted'] = True
        else:
            dicom_count_input_df.loc[index, 'heudiconv converted'] = False

    all_pass = 'Pass' if dicom_count_input_df['heudiconv converted'].all() \
            else 'Fail'
    dicom_count_input_df = pd.concat([
        pd.DataFrame({'heudiconv converted': [all_pass]}),
        dicom_count_input_df])[['series_num', 'series_dir', 'dicom_count',
            'heudiconv converted']]

    return dicom_count_input_df


def get_dicom_files_walk(dicom_root: Union[Path, str],
                         one_file_for_series=False,
                         quick_scan=False) -> pd.DataFrame:
    '''Find all dicom path under the root and return it as pandas DataFrame

    Key arguments:
        dicom_root: root directory of the dicom for a subject, str or Path.
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
    logger.info('Walking through the raw dicom directory to find dicom files')
    max_number_of_dirs = 0
    for _, folders, _ in os.walk(dicom_root):
        max_number_of_dirs = len(folders) \
                if (max_number_of_dirs < len(folders)) else max_number_of_dirs

    num = 0
    logger.info('Searching for files...')
    for root, folders, files in os.walk(dicom_root):
        for file in [x for x in files if not x.startswith('.')]:
            if file.endswith('xml'):
                continue

            file_lower = file.lower()
            # includes the logics to detect dicoms without dcm / ima extension
            # file with only digits in the filename
            try:
                if file_lower.endswith('dcm') or file_lower.endswith('ima') \
                        or (file.startswith('MR') and \
                            len(Path(file).name.split('.')[-1]) > 10) \
                        or file.startswith('MR.') \
                        or len(re.search('\d+', file).group(0)) == len(file):
                    dicom_paths.append(os.path.join(root, file))
                    num += 1
                elif not file_lower.startswith('.'):
                    dicom_paths.append(os.path.join(root, file))
                    num += 1
                
                if one_file_for_series:  # to load a single file for each dir
                    break

            except:
                logger.warning(f'There are non-dicom files {root}/{file}')

    logger.info('READING complete')

    if num == 0:
        logger.critical(f'No dicom files found under {dicom_root}')
        logger.info(f'No dicom files found under {dicom_root}')
    else:
        logger.info(f'There are {num} files detected as dicom by QQC')

    end = time.time()
    t = end - start
    logger.info(f'Time taken to walk through dicom root: {t}')

    # get dataframe and convert them into pydicom objects
    logger.info('Convert dicom information to pandas dataframe')
    df = pd.DataFrame({'file_path': dicom_paths})
    start = time.time()

    # drop files
    df = df[~df['file_path'].str.endswith('.gif')]
    df = df[~df['file_path'].str.endswith('.GIF')]
    df = df[~df['file_path'].str.endswith('.bvec')]
    df = df[~df['file_path'].str.endswith('.bval')]
    df = df.reset_index()

    logger.info('Read dicoms into pydicom object')
    # TODO: update the lines below to make the process faster
    if quick_scan:
        df['parent'] = df.file_path.apply(lambda x: Path(x).parent)
        df['norm'] = pd.NA
        df['series'] = pd.NA
        for dirname, table in df.groupby('parent'):
            pydicom_obj = pydicom.read_file(table.iloc[0]['file_path'],
                                            force=True)
            try:
                table.at[table.index[0], 'norm'] = get_additional_info(
                        pydicom_obj, '0008', '0008')
            except:
                table.at[table.index[0], 'norm'] = 'unknown'

            table.at[table.index[0], 'series'] = get_series_info(pydicom_obj)
            table['norm'] = table['norm'].fillna(method='ffill')
            table['series'] = table['series'].fillna(method='ffill')
            df.at[table.index, 'norm'] = table['norm']
            df.at[table.index, 'series'] = table['series']

        end = time.time()
        t = end - start
        logger.info(f'Quick-scan enabled')
        logger.info(f'Time taken to dicomise dicom all paths: {t}')

    else:
        df['pydicom'] = df.file_path.apply(lambda x: pydicom.read_file(x,
            force=True))
        end = time.time()
        t = end - start
        logger.info(f'Time taken to dicomise dicom all paths: {t}')

        logger.info('READING complete 2')

        start = time.time()
        logger.info('Extracting information from pydicom objects')
        try:
            df['norm'] = df.pydicom.apply(lambda x:
                    get_additional_info(x, '0008', '0008'))
        except:  #GE
            df['norm'] = 'unknown'

        df['series'] = df.pydicom.apply(lambda x: get_series_info(x))

    logger.info('Extracting information from pydicom objects')
    try:
        df['series_num'] = df['series'].str[0]
        df['series_desc'] = df['series'].str[1]
        df['series_uid'] = df['series'].str[2]
        df.drop('series', axis=1, inplace=True)
    except IndexError:
        logger.critical('Pydicom objects have incorrect dicom header')

    # if unique dicom for a series is required
    if one_file_for_series:
        df_tmp = pd.DataFrame()
        for group, table in df.groupby(
                ['series_num', 'series_desc', 'series_uid']):
            # get the first dicom file
            df_tmp = pd.concat([df_tmp, table.iloc[[0]]], axis=0)
        df = df_tmp.reset_index().drop('index', axis=1)

    # series_scan column to detect if there is any rescan
    logger.info('Searching for duplicated data using series number,'
                'description, and uid')
    gb_series = df.groupby(['series_num', 'series_desc', 'series_uid'])
    unique_count_df = gb_series.count().reset_index()

    dup_df = unique_count_df[unique_count_df[
            ['series_num', 'series_desc', 'series_uid']].duplicated()]

    df['series_scan'] = 1
    for _, row in dup_df.iterrows():
        num = 1
        logger.warning('There are more than one unique scan for %s' %
                       row.series_desc)
        df_tmp = df[
                (df['series_num'] == row.series_num) &
                (df['series_desc'] == row.series_desc) &
                (df['series_uid'] == row.series_uid)]

        df.loc[df_tmp.index, 'series_scan'] = num

    end = time.time()
    t = end - start
    logger.debug(f'Time taken to extract info from pydicom objects: {t}')

    return df


def get_series_info(dicom: pydicom.dataset.FileDataset):
    '''Extract series information from pydicom dataset'''
    try:
        num = dicom.get(('0020', '0011')).value
        description = dicom.get(('0008', '103e')).value
        instance_uid = dicom.get(('0008', '0018')).value
    except AttributeError:
        print(dicom)
        logger.warning("Dicom doesn't have num, description, or instance_uid "
                       "attributes.")
        logger.warning("The dicom sourcedata may have non dicom files.")
        sys.exit()

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
    try:
        info = get_additional_info(dicom, '0029', '1020')
    except:
        return pd.DataFrame({'var': ['unknown'], 'value': 'unknown'})

    extracted_text = info.decode(errors='ignore').split(
            '### ASCCONV')[1]

    new_lines = []
    for line in extracted_text.split('\n'):
        if line.startswith('sAdjData.sAdjVolume') \
                or line.startswith('sSliceArray.asSlice[0].'):
            new_lines.append(line)


    df = pd.DataFrame({'raw_line': new_lines})

    if len(new_lines) == 0:
        df['var'] = []
        df['value'] = []
        df.drop('raw_line', axis=1, inplace=True)

    else:
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
                    force: bool = False,
                    rename_dicoms: bool = False) -> None:
    '''Copy dicoms to a new directory structure

    Each row in the dicom_df represent individual dicom file. All dicom files
    in this data frame will be copied to the following BIDS structure.

    > {new_root}/{subject}/{session}/{series_num}_{series_desc}


    Key Arguments:
        dicom_df: dicom information database, pd.DataFrame.
        new_root: root of the output dicom directory, str or Path.
        subject: subject name to be used in the data path, str.
        session: session name to be used in the data path, str.
        force: force overwriting copy, bool.
        rename_dicoms: change output dicom file name to 'MR.{series_uid}'

    Notes:
        If there are dicom files with the same file name for a series,
        rename_dicoms=True should be used to avoid the function overwriting
        the dicom files with the same file name.
    '''
    logger.info('Arranging dicoms')
    new_root = Path(new_root)
    if rename_dicoms:
        logger.info('Changing dicom filenames')

    for (num, name, scan), table in dicom_df.groupby(
            ['series_num', 'series_desc', 'series_scan']):
        logger.info(f'Preparing to copy {name}')

        session_dir_path = new_root / subject / f'ses-{session}'
        series_dir_path =  session_dir_path / f'{num:02}_{name}'

        if not force and series_dir_path.is_dir() \
                and len(table) == len(list(series_dir_path.glob('*'))):
            logger.warning(f'Not overwriting {series_dir_path}')
            continue

        series_dir_path.mkdir(exist_ok=True, parents=True)
        logger.info(f'Looping through dicom files under {name}')
        for _, row in table.iterrows():
            if rename_dicoms:  # philips
                dicom_out = series_dir_path / ('MR.' + row['series_uid'])
                try:
                    shutil.copy(row['file_path'], dicom_out)
                except shutil.SameFileError:
                    pass
            else:
                try:
                    shutil.copy(row['file_path'], series_dir_path)
                except shutil.SameFileError:
                    pass
