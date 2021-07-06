#!/usr/bin/env python

import argparse
from pathlib import Path
import subprocess
import sys
import os
import nibabel as nb
import numpy as np
import matplotlib.pyplot as plt
import tempfile


def convert_to_img(dicom_folder: str, outdir: str, name: str) -> None:
    '''Convert dicoms into nifti to a given location outdir/name'''
    command = f'dcm2niix \
            -o {outdir} -f {name} {dicom_folder}'
    subprocess.check_call(command, shell=True)


def load_data_bval(prefix: Path):
    '''Return data array and bval array from the files with given prefix'''
    data = nb.load(prefix.with_suffix('.nii')).get_fdata()
    bval = np.loadtxt(prefix.with_suffix('.bval'))

    return data, bval


def get_data(dicom_folder: str, name: str, threshold: str):
    '''Convert dicoms to load 4D dMRI data and threshold it before return'''
    temp_dir = tempfile.TemporaryDirectory()
    convert_to_img(dicom_folder, temp_dir.name, name)
    data, bval_arr = load_data_bval(Path(temp_dir.name) / name)
    data = data[:, :, :, bval_arr < threshold]
    bval_arr = bval_arr[bval_arr < threshold]
    temp_dir.cleanup()

    return data, bval_arr


def create_b0_signal_figure(data1: np.array, data1_bval: np.array,
                            data2: np.array, data2_bval: np.array,
                            data3: np.array, data3_bval: np.array,
                            out: str, savefig: bool = False):
    '''Plot b0 summary from three different 4d dMRI volumes

    Key arguments:
        data1: first AP B0 volumes
        data2: second AP B0  volumes
        data3: b0 volumes extracted from the PA dMRI
        out: output image file name, eg) test.png
        savefig: save figure if True
    '''
    fig, axes = plt.subplots(ncols=3, figsize=(12, 8), dpi=150)

    for ax, (data, bval, name, color) in zip(
            np.ravel(axes),
            [(data1, data1_bval, 'b0 AP 1', 'b'),
             (data3, data3_bval, 'b0 PA dMRI', 'r'),
             (data2, data2_bval, 'b0 AP 2', 'b')]):
        data_mean = [data[:, :, :, vol_num].mean() for vol_num in
                np.arange(data.shape[-1])]
        ax.plot(data_mean, color+'-')
        ax.plot(data_mean, color+'o')
        ax.set_ylabel("Average signal in all voxels")
        ax.set_xlabel("B0 value")
        ax.set_title(name)
        ax.set_xticks(np.arange(len(bval)))
        ax.set_xticklabels(bval)

    max_y = 0
    min_y = 100000
    for x in data1, data2, data3:
        values = np.array(
                [x[:, :, :, vol_num].mean() for vol_num
                    in np.arange(x.shape[-1])])
        max_y = values.max() if values.max() > max_y else max_y
        min_y = values.min() if values.min() < min_y else min_y

    for ax in axes:
        ax.set_ylim(min_y-5, max_y+5)

    fig.subplots_adjust(wspace=0.3)

    if savefig:
        fig.savefig(out)
    else:
        return fig


def parse_args(argv):
    '''Parse inputs coming from the terminal'''
    parser = argparse.ArgumentParser(description='Summarize phantom')

    parser.add_argument('--apb0dir1', type=str, help='First AP b0 dicom dir')
    parser.add_argument('--apb0dir2', type=str, help='Second AP b0 dicom dir')
    parser.add_argument('--padmridir', type=str, help='PA dMRI dicom dir')
    parser.add_argument('--b0thr', type=int, default=50,
            help='b0 threshold, default=50')
    parser.add_argument('--out', type=str, help='Out image file')
    args = parser.parse_args(argv)
    return args


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])

    ap_b0_1_data, ap_b0_1_bval_arr = get_data(
            args.apb0dir1, 'apb0_1', args.b0thr)
    ap_b0_2_data, ap_b0_2_bval_arr = get_data(
            args.apb0dir2, 'apb0_2', args.b0thr)
    pa_dmri_data, pa_dmri_bval_arr = get_data(
            args.padmridir, 'padmri', args.b0thr)

    create_b0_signal_figure(ap_b0_1_data, ap_b0_1_bval_arr,
                            ap_b0_2_data, ap_b0_2_bval_arr,
                            pa_dmri_data, pa_dmri_bval_arr,
                            args.out, True)
