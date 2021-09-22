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

from phantom_check.dicom_files import get_dicom_files_walk, \
        get_series_info, get_csa_header, rearange_dicoms

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
