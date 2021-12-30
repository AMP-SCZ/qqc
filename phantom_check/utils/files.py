import phantom_check
from typing import List
import tempfile
import shutil
import subprocess
from pathlib import Path
import nibabel as nb
import numpy as np
import pandas as pd
import sys
import json
from sklearn.cluster import KMeans
from sklearn import preprocessing
import os


def get_all_files_walk(root_dir: str, extension: str) -> List[Path]:
    '''Return a list of all json file paths under a root_dir'''
    path_list = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.' + extension) and not file.startswith('.'):
                path_list.append(Path(root) / file)

    return path_list


def load_data_bval(prefix: Path):
    '''Return data array and bval array from the files with given prefix'''
    data = nb.load(prefix.with_suffix('.nii.gz')).get_fdata()
    bval = np.loadtxt(prefix.with_suffix('.bval'))

    return data, bval


def convert_to_img(dicom_folder: str, outdir: str, name: str) -> None:
    '''Convert dicoms into nifti to a given location outdir/name'''
    command = f'dcm2niix \
            -o {outdir} -f {name} -z y -b y {dicom_folder}'
    subprocess.run(command, shell=True, check=True, capture_output=True)


def get_jsons_from_dicom_dirs(dicom_dirs: List[str],
                              names: List[str] = None,
                              save_outputs: bool = True):
    '''Get json files from the dicom directories'''
    json_files = []
    for num, dicom_dir in enumerate(dicom_dirs):
        name = names[num] if names else Path(dicom_dir).name
        temp_dir = tempfile.TemporaryDirectory()
        convert_to_img(dicom_dir, temp_dir.name, name)
        json_files.append(Path(temp_dir) / (name + '.json'))

        if save_outputs:
            shutil.copytree(temp_dir.name, name)

        temp_dir.cleanup()

    return json_files


def get_nondmri_data(data_source: str,
                     dtype: List[str],
                     name: str,
                     save_outputs: bool = False):
    '''Get fMRI data and name

    Key Arguments:
        - data_source: Nifiti prefix, dicom or nifti directory, str
            - dicom_dir
            - nifti_dir
            - nifti_prefix
        - name: name of the data source, str.
        - save_outputs: save dcm2niix outputs when data_source == dicom dir,
                        bool.
    '''
    if dtype == 'dicom_dir':
        temp_dir = tempfile.TemporaryDirectory()
        convert_to_img(data_source, temp_dir.name, name)
        data = nb.load(
                (Path(temp_dir.name) / name).with_suffix(
                    '.nii.gz')).get_fdata()
        if save_outputs:
            shutil.copytree(temp_dir.name, name)
        temp_dir.cleanup()

    elif dtype == 'nifti_prefix':
        data = nb.load(Path(data_source).with_suffix('.nii.gz')).get_fdata()

    elif dtype == 'nifti_dir':
        nifti_prefix = list(Path(data_source).glob('*.nii.gz'))[0]
        data = nb.load(nifti_prefix).get_fdata()

    else:
        print('Please provide correct dtype')
        print('Exiting')
        sys.exit()

    return data


def get_diffusion_data_from_dicom_dir(dicom_dir: str,
                                      name: str,
                                      threshold: str,
                                      save_outputs: bool = False):
    '''Convert dicoms to load 4D dMRI data and threshold it before return'''
    temp_dir = tempfile.TemporaryDirectory()
    convert_to_img(dicom_dir, temp_dir.name, name)
    data, bval_arr = load_data_bval(Path(temp_dir.name) / name)
    data = data[:, :, :, bval_arr < threshold]
    bval_arr = bval_arr[bval_arr < threshold]

    if save_outputs:
        shutil.copytree(temp_dir.name, name)

    temp_dir.cleanup()

    return data, bval_arr


def get_diffusion_data_from_nifti_prefix(nifti_prefix: str,
                                         name: str,
                                         threshold: str,
                                         save_outputs: bool = False):
    '''Convert dicoms to load 4D dMRI data and threshold it before return

    Notes:
        There are unused inputs, in order to abstract the type of the data
        source given in the parent function.

    '''
    data, bval_arr = load_data_bval(Path(nifti_prefix))
    data = data[:, :, :, bval_arr < threshold]
    bval_arr = bval_arr[bval_arr < threshold]

    return data, bval_arr


def get_diffusion_data_from_nifti_dir(nifti_dir: str,
                                      name: str,
                                      threshold: str,
                                      save_outputs: bool = False):
    '''Convert dicoms to load 4D dMRI data and threshold it before return

    Notes:
        There are unused inputs, in order to abstract the type of the data
        source given in the parent function.
    '''

    nifti_prefix = list(Path(nifti_dir).glob('*.nii.gz'))[0]
    data, bval_arr = load_data_bval(
            nifti_prefix.parent / nifti_prefix.name.split('.')[0])
    data = data[:, :, :, bval_arr < threshold]
    bval_arr = bval_arr[bval_arr < threshold]

    return data, bval_arr


def load_anat_json_from_mriqc(json_file: str) -> pd.DataFrame:
    '''Read json file from mriqc

    Returns a dataframe with the index of qc_vars, and the values as a column
    '''
    with open(json_file, 'r') as f:
        json_dict = json.load(f)

    subject = Path(json_file).name.split('.json')[0]

    json_dict = dict((x, y) for x, y in json_dict.items()
                if x not in ["bids_meta", "provenance"])

    df = pd.DataFrame.from_dict(
            json_dict, orient='index', columns=[subject])

    return df


def load_anat_jsons_from_mriqc(json_files: list,
                               normalize: bool = False) -> pd.DataFrame:
    '''Read json files from mriqc

    Returns a dataframe with the index of qc_vars, and subjects as columns
    '''

    dfs = []
    for json_file in json_files:
        df_tmp = load_anat_json_from_mriqc(json_file)
        dfs.append(df_tmp)

    df = pd.concat(dfs, axis=1)


    # df_open_data = load_and_filter_anat_qc_from_open_data(
    
    if normalize:
        # normalize each rows
        df = df.div(df.sum(axis=1), axis=0).fillna(0)

    kmeans = KMeans(n_clusters=3, random_state=0).fit(
            df.mean(axis=1).values.reshape(-1, 1))
    df['labels'] = kmeans.labels_

    return df


def load_and_filter_anat_qc_from_open_data(csv_file: str) -> pd.DataFrame:
    '''Load anat qc from open data'''

    df = pd.read_csv(csv_file)

    # filter
    df = df[df['bids_meta.MagneticFieldStrength'] == 3]

    return df


def add_open_data_qc_measures(df: pd.DataFrame,
                              df_open: pd.DataFrame) -> pd.DataFrame:
    '''Add open data columns to the mriqc df'''
    df.loc['source'] = 'mriqc'

    # add open data qc measures
    open_data_csv = Path(phantom_check.__file__).parent.parent / \
            'data' / 'T1w_demo.csv'
    df_open = load_and_filter_anat_qc_from_open_data(open_data_csv)
    df_open['source'] = 'opendata'

    df_open = df_open[[x for x in df_open.columns if x in df.index]].T

    df = pd.concat([df, df_open], axis=1)

    return df
