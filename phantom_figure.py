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
import shutil
from typing import List
import math


def convert_to_img(dicom_folder: str, outdir: str, name: str) -> None:
    '''Convert dicoms into nifti to a given location outdir/name'''
    command = f'dcm2niix \
            -o {outdir} -f {name} -z y -b y {dicom_folder}'
    subprocess.run(command, shell=True, check=True, capture_output=True)


def load_data_bval(prefix: Path):
    '''Return data array and bval array from the files with given prefix'''
    data = nb.load(prefix.with_suffix('.nii.gz')).get_fdata()
    bval = np.loadtxt(prefix.with_suffix('.bval'))

    return data, bval


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


def create_b0_signal_figure_prev(data1: np.array, data1_bval: np.array,
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
        ax.set_xlabel("B value")
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

    fig.subplots_adjust(wspace=0.3, hspace=0.3)

    if savefig:
        fig.savefig(out)
    else:
        return fig


def create_image_signal_figure(dataset: List[tuple], out: str,
                               savefig: bool = False, col_num: int = 3, 
                               wide_fig: bool = False):
    '''Plot b0 summary from three different 4d dMRI volumes

    Key arguments:
        dataset: Tuple of (data, name), tuple.
        out: output image file name, eg) test.png, str.
        savefig: save figure if True, bool.
        col_num: number of figures in a single row, int.
        wide_fig: option to create horizontally long figure, bool.
    '''
    col_width = 4
    row_num = math.ceil(len(dataset) / col_num)
    row_height = 8
    width = len(dataset) * col_width
    height = row_num * row_height

    if wide_fig:
        fig, axes = plt.subplots(nrows=col_num, ncols=row_num,
                figsize=(height*2, width), dpi=150)
    else:
        fig, axes = plt.subplots(ncols=col_num, nrows=row_num,
                figsize=(width, height), dpi=150)

    # color
    cm = plt.get_cmap('brg')

    color_num = 0
    for ax, (data, name) in zip(np.ravel(axes), dataset):
        color = cm(1.*color_num/len(dataset))
        data_mean = [data[:, :, :, vol_num].mean() for vol_num in
                np.arange(data.shape[-1])]
        ax.plot(data_mean, color=color, linestyle='-', marker='o')
        ax.set_ylabel("Average signal in all voxels")
        ax.set_xlabel("Volume")
        ax.set_title(name)
        color_num += 1

    max_y = 0
    min_y = 100000
    for data in [x[0] for x in dataset]:
        values = np.array(
                [data[:, :, :, vol_num].mean() for vol_num
                    in np.arange(data.shape[-1])])
        max_y = values.max() if values.max() > max_y else max_y
        min_y = values.min() if values.min() < min_y else min_y

    for ax in np.ravel(axes):
        ax.set_ylim(min_y-5, max_y+5)

        if wide_fig:
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

    for ax in np.ravel(axes)[len(dataset):]:
        ax.axis('off')

    fig.subplots_adjust(wspace=0.3, hspace=0.3)

    if savefig:
        fig.savefig(out)
    else:
        return fig




def create_b0_signal_figure(dataset: List[tuple], out: str,
                            savefig: bool = False, col_num: int = 3, 
                            wide_fig: bool = False):
    '''Plot b0 summary from three different 4d dMRI volumes

    Key arguments:
        data1: first AP B0 volumes
        data2: second AP B0  volumes
        data3: b0 volumes extracted from the PA dMRI
        out: output image file name, eg) test.png
        savefig: save figure if True
    '''
    col_width = 4
    row_num = math.ceil(len(dataset) / col_num)
    row_height = 8
    width = len(dataset) * col_width
    height = row_num * row_height

    if wide_fig:
        fig, axes = plt.subplots(nrows=col_num, ncols=row_num,
                figsize=(height*2, width), dpi=150)
    else:
        fig, axes = plt.subplots(ncols=col_num, nrows=row_num,
                figsize=(width, height), dpi=150)

    # color
    cm = plt.get_cmap('brg')

    color_num = 0
    for ax, (data, bval, name) in zip(np.ravel(axes), dataset):
        color = cm(1.*color_num/len(dataset))
        data_mean = [data[:, :, :, vol_num].mean() for vol_num in
                np.arange(data.shape[-1])]
        ax.plot(data_mean, color=color, linestyle='-', marker='o')
        ax.set_ylabel("Average signal in all voxels")
        ax.set_xlabel("B0 value")
        ax.set_title(name)
        ax.set_xticks(np.arange(len(bval)))
        ax.set_xticklabels(bval)
        color_num += 1

    max_y = 0
    min_y = 100000
    for data in [x[0] for x in dataset]:
        values = np.array(
                [data[:, :, :, vol_num].mean() for vol_num
                    in np.arange(data.shape[-1])])
        max_y = values.max() if values.max() > max_y else max_y
        min_y = values.min() if values.min() < min_y else min_y

    for ax in np.ravel(axes):
        ax.set_ylim(min_y-5, max_y+5)

        if wide_fig:
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

    for ax in np.ravel(axes)[len(dataset):]:
        ax.axis('off')

    fig.subplots_adjust(wspace=0.3, hspace=0.3)

    if savefig:
        fig.savefig(out)
    else:
        return fig


def parse_args():
    '''Parse inputs coming from the terminal'''
    parser = argparse.ArgumentParser(description='Summarize phantom')

    # mode
    parser.add_argument('--mode', type=str, required=True,
            choices=['dmri_b0', 'fmri', 'dmri', 'json_check'],
            help='Select mode')

    # image input related options
    parser.add_argument('--dicom_dirs', type=str, nargs='+',
            help='List of dicom directories to plot summary. They will be '
                 'converted to nifti using dcm2niix to new directories.')
    parser.add_argument('--nifti_prefixes', type=str, nargs='+',
            help='List of nifti image prefixes to plot summary from.')
    parser.add_argument('--nifti_dirs', type=str, nargs='+',
            help='List of directories that contain unique nifti image')

    # extra options
    parser.add_argument('--names', type=str, nargs='+',
            help='List of name for each given dicom dirs, nifti prefixes or '
                 'nifti dirs')
    parser.add_argument('--store_nifti', action='store_true',
            help='Keep outputs of dcm2niix for later use.')
    parser.add_argument('--b0thr', type=int, default=50,
            help='b0 threshold, default=50')
    parser.add_argument('--fig_num_in_row', type=int, default=3,
            help='Number of columns in the figure')
    parser.add_argument('--wide_fig', action='store_true',
            help='Create wide figure')
    parser.add_argument('--out_image', type=str, help='Out image file')


    args = parser.parse_args()
    return args


def dmri_b0_summary(args):
    if args.mode == 'dmri_b0':
        if args.dicom_dirs:
            function = get_diffusion_data_from_dicom_dir
            vars = args.dicom_dirs
        elif args.nifti_prefixes:
            function = get_diffusion_data_from_nifti_prefix
            vars = args.nifti_prefixes
        elif args.nifti_dirs:
            function = get_diffusion_data_from_nifti_dir
            vars = args.nifti_dirs
        else:
            sys.exit('Data input needs to be provided. Provide one of '
            '--dicom_dirs, --nifti_prefixes or --nifti_dirs. Exiting.')

        dataset = []
        for num, var in enumerate(vars):
            name = args.names[num] if args.names else Path(var).name
            data, bval_arr = function(var, name, args.b0thr, args.store_nifti)
            dataset.append((data, bval_arr, name))

        create_b0_signal_figure(dataset, args.out_image,
                                True, args.fig_num_in_row, args.wide_fig)

def fmri_summary(args):
    if args.mode == 'fmri':
        function = get_nondmri_data
        if args.dicom_dirs:
            dtype = 'dicom_dir'
            vars = args.dicom_dirs
        elif args.nifti_prefixes:
            dtype = 'nifti_prefix'
            vars = args.nifti_prefixes
        elif args.nifti_dirs:
            dtype = 'nifti_dir'
            vars = args.nifti_dirs
        else:
            sys.exit('Data input needs to be provided. Provide one of '
            '--dicom_dirs, --nifti_prefixes or --nifti_dirs. Exiting.')

        dataset = []
        for num, var in enumerate(vars):
            name = args.names[num] if args.names else Path(var).name
            data = function(var, dtype, name, args.store_nifti)
            dataset.append((data, name))

        create_image_signal_figure(dataset, args.out_image,
                                   True, args.fig_num_in_row,
                                   args.wide_fig)


def json_check(args):
    if args.mode == 'json_check':
        pass


if __name__ == '__main__':
    args = parse_args()

    # dmri_b0_summary
    dmri_b0_summary(args)
    fmri_summary(args)
    json_check(args)
