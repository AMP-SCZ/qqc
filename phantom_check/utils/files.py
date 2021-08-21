from typing import List
import tempfile
import shutil
import subprocess
from pathlib import Path
import nibabel as nb
import numpy as np
import sys


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
    '''Convert dicoms to load 4D dMRI data and threshold it before return'''
    data, bval_arr = load_data_bval(Path(nifti_prefix))
    data = data[:, :, :, bval_arr < threshold]
    bval_arr = bval_arr[bval_arr < threshold]

    return data, bval_arr


def get_diffusion_data_from_nifti_dir(nifti_dir: str,
                            name: str,
                            threshold: str,
                            save_outputs: bool = False):
    '''Convert dicoms to load 4D dMRI data and threshold it before return'''
    nifti_prefix = list(Path(nifti_dir).glob('*.nii.gz'))[0]
    data, bval_arr = load_data_bval(
            nifti_prefix.parent / nifti_prefix.name.split('.')[0])
    data = data[:, :, :, bval_arr < threshold]
    bval_arr = bval_arr[bval_arr < threshold]

    return data, bval_arr
