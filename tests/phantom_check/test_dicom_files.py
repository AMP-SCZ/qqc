import pytest
import pandas as pd
from pathlib import Path
import phantom_check
import os
import pydicom
from typing import Union
import time
import numpy as np
import shutil
import re

from phantom_check.dicom_files import get_dicom_files_walk, \
        get_series_info, get_csa_header, rearange_dicoms, \
        get_diff_in_csa_for_all_measures, all_elements_to_extract, \
        get_additional_info, get_additional_info_by_elem, \
        add_detailed_info_to_summary_df
        

pd.set_option('max_columns', 10)


@pytest.fixture
def get_test_dicom_df() -> pd.DataFrame:
    '''Return test dicom path dataframe'''
    script_root = Path(phantom_check.__file__).parent.parent
    doc_root = script_root / 'docs'
    dicom_example_root = doc_root / 'dicom_example'
    dicom_path_db = dicom_example_root / 'db.csv'

    if dicom_path_db.is_file():
        df = pd.read_csv(dicom_path_db, index_col=0)
    else:
        dicom_paths = []
        for root, dirs, files in os.walk(dicom_example_root):
            for file in files:
                if file.endswith('dcm'):
                    dicom_paths.append(os.path.join(root, file))

        df = pd.DataFrame({'file_path': dicom_paths})
        df['series'] = df.file_path.apply(
                lambda x: Path(x).parent.parent.name)
        df.to_csv(dicom_path_db)

    return df


@pytest.fixture
def get_dicom_object(get_test_dicom_df):
    df = get_test_dicom_df
    dicom_file_loc = df.iloc[0]['file_path']
    dicom = pydicom.read_file(dicom_file_loc)

    return dicom


@pytest.fixture
def get_test_summary_df(get_test_dicom_df):
    db_df = get_test_dicom_df
    dicom_dir_loc = Path(db_df.iloc[0]['file_path']).parent.parent.parent
    df = get_dicom_files_walk(dicom_dir_loc, True)

    return df

def test_get_dicom_files_walk():
    dicom_dir_loc = '/data/predict/phantom_human_pilot/sourcedata/ProNET_Cambridge_Prisma/ses-humanpilot'
    df = get_dicom_files_walk(dicom_dir_loc, True)

    return df

def test_read_dicom_header(get_test_dicom_df):
    df = get_test_dicom_df
    dicom_file_loc = df.iloc[0]['file_path']
    pydicom.read_file(dicom_file_loc)


def test_get_dicom_object(get_test_dicom_df):
    _ = get_test_dicom_df
    

def test_extract_series(get_dicom_object):
    dicom = get_dicom_object
    num, description, instance_uid = get_series_info(dicom)


def test_get_test_summary_df(get_test_summary_df):
    _ = get_test_summary_df


def test_private_info(get_dicom_object):
    dicom = get_dicom_object
    csa_df = get_csa_header(dicom)
    print(csa_df)


def test_dicom_rearrange(get_test_summary_df):
    df = get_test_summary_df
    rearange_dicoms(df, 'test_root')

    print(os.popen('tree test_root').read())
    print(os.popen('ls test_root').read())
    shutil.rmtree('test_root')


def test_normalized(get_test_summary_df):
    df = get_test_summary_df

    print(df[['series_num', 'series_desc', 'norm']].sort_values(
        by='series_desc'))


def test_dicom_rearrange_two(get_test_summary_df):
    df = get_test_summary_df
    print(df.head())
    rearange_dicoms(df, 'sub-01')

    # print(os.popen('tree test_root').read())
    # print(os.popen('ls test_root').read())
    # shutil.rmtree('test_root')


def test_get_diff_in_csa_for_all_measures(get_test_summary_df):
    df = get_test_summary_df
    diff_df, common_df = get_diff_in_csa_for_all_measures(df, get_same=True)
    diff_df = get_diff_in_csa_for_all_measures(df, ['dmri', 'fmri'])
    diff_df, common_df = get_diff_in_csa_for_all_measures(
            df, ['dmri', 'fmri'], True)
    print(common_df)


def test_with_seoul_data_dir():
    dicom_dir_loc = '/data/predict/phantom_data/ProNET_Seoul/phantom/data' \
                    '/dicom/HEAD_PI_OTHERS_20210813_085128_199000'

    script_root = Path(phantom_check.__file__).parent.parent
    doc_root = script_root / 'docs'
    dicom_dir_loc = doc_root / 'dicom_example'

    df = get_dicom_files_walk(dicom_dir_loc, True)

    diff_df, common_df = get_diff_in_csa_for_all_measures(df, get_same=True)
    print(diff_df)
    print(common_df)
    # diff_df.to_csv('tmp_diff.csv')
    # common_df.to_csv('tmp_same.csv')


def test_add_detailed_info_to_summary_df(get_test_summary_df):
    df = get_test_summary_df

    df_new = add_detailed_info_to_summary_df(df, all_elements_to_extract)
    df_new.drop('pydicom', axis=1, inplace=True)
    print(df_new)


def test_whole_flow_with_heudiconv_2():
    script_root = Path(phantom_check.__file__).parent.parent
    doc_root = script_root / 'docs'
    dicom_example_root = doc_root / 'dicom_example'

    df = get_dicom_files_walk(dicom_example_root, True)
    csa_diff_df, csa_common_df = get_diff_in_csa_for_all_measures(
            df, get_same=True)
    df = add_detailed_info_to_summary_df(df, all_elements_to_extract)

    # compare to template
    # compare between scans
    # compare CSA

def test_flow_with_multiseries_directory():
    dicom_example_root = '/Users/kc244/phantom_check/tests/phantom_check/Alex_merged/new_dir'

    df_full = get_dicom_files_walk(dicom_example_root)
    # df_full = get_dicom_files_walk(dicom_example_root, True)

    df = get_dicom_files_walk(dicom_example_root, True)
    csa_diff_df, csa_common_df = get_diff_in_csa_for_all_measures(
            df, get_same=True)
    df = add_detailed_info_to_summary_df(df, all_elements_to_extract)

    rearange_dicoms(df_full, 'test_root_from_single_root')



def test_whole_flow_with_heudiconv():
    script_root = Path(phantom_check.__file__).parent.parent
    doc_root = script_root / 'docs'
    dicom_example_root = doc_root / 'dicom_example'

    df_full = get_dicom_files_walk(dicom_example_root)
    # df_full = get_dicom_files_walk(dicom_example_root, True)

    df = get_dicom_files_walk(dicom_example_root, True)
    csa_diff_df, csa_common_df = get_diff_in_csa_for_all_measures(
            df, get_same=True)
    df = add_detailed_info_to_summary_df(df, all_elements_to_extract)

    rearange_dicoms(df_full, 'test_root')

    command = 'heudiconv \
    -d {subject}/*/*/*dcm \
    -f /Users/kc244/phantom_check/data/heuristic.py \
    -s test_root -ss 001 -c dcm2niix --overwrite \
    -b \
    -o new_test_root_test'

    os.popen(command).read()

    # command = 'docker run -it --rm \
            # -v /Users/kc244/phantom_check/tests/phantom_check/new_test_root:/data:ro \
            # -v /Users/kc244/phantom_check/tests/phantom_check/new_test_root/mriqc_out:/out \
            # poldracklab/mriqc:latest \
            # /data /out group \
            # --verbose-reports'
    # with open('command.sh', 'w') as f:
        # f.write(re.sub('\s\s+', '\ \n\\t', command))
    # os.popen(command).read()

    # print(os.popen('tree new_test_root').read())
    # print(os.popen('ls new_test_root').read())
    # shutil.rmtree('new_test_root')


def test_whole_flow_with_heudiconv_seoul():
    dicom_example_root = '/data/predict/phantom_data/ProNET_Seoul/phantom/data' \
                    '/dicom/HEAD_PI_OTHERS_20210813_085128_199000'

    dicom_example_root = '/Users/kc244/Downloads/Elex_dicom'

    df_full = get_dicom_files_walk(dicom_example_root)
    # df_full = get_dicom_files_walk(dicom_example_root, True)

    df = get_dicom_files_walk(dicom_example_root, True)
    csa_diff_df, csa_common_df = get_diff_in_csa_for_all_measures(
            df, get_same=True)

    csa_diff_df.to_csv('csa_diff.txt')
    csa_diff_df.to_csv('csa_comman.txt')
    # df = add_detailed_info_to_summary_df(df, all_elements_to_extract)


    # rearange_dicoms(df_full, 'Alex')

    command = 'heudiconv \
    -d {subject}/*/*/*[IiDd][MmCc][AaMm] \
    -f /Users/kc244/phantom_check/data/heuristic.py \
    -s Alex -ss 001 -c dcm2niix --overwrite \
    -b \
    -o new_test_root'

    print(command)

    # print(os.popen(command).read())
    # print(os.popen('tree new_test_root').read())
    # print(os.popen('ls new_test_root').read())
    # shutil.rmtree('new_test_root')



def test_manufacturer_model_name():

    f = pydicom.read_file('/data/predict/phantom_data/phantom_data_BIDS/dicom/ProNET_Pittsburgh_Prisma/ses-phantom/14_DistortionMap_PA/MR.1.3.12.2.1107.5.2.43.67078.2021093013240198029914286')

    output = get_additional_info_by_elem(f, 'ManufacturerModelName')
    print('Output:', output)




def test_je_data():
    dicom_root = '/data/predict/data_from_nda_dev/MRI_ROOT/sourcedata/JE00068/ses-202206282'
    # df = get_dicom_files_walk(dicom_root)
    # print(df)

    df = get_dicom_files_walk(dicom_root, True)
    print(df)



